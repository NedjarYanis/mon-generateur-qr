import os
import random
import io
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    redirect,
    flash,
    send_file,
    jsonify
)
from database import (
    init_db,
    save_pass,
    get_all_passes,
    get_pass_by_id,
    mark_as_used,
    use_drink_attempt,
    delete_pass_by_id,
    get_stats
)
from qr_service import (
    generate_qr_png_bytes,
    generate_qr_data_url,
    format_boisson_code,
    format_app_card_code
)
from mail_service import generate_temp_email, hash_email
from automation import execute_week_pass, execute_day_pass

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "basicfit-qr-secret-key-2026")

# Initialize SQLite database and run any legacy migrations
init_db()

# --- HELPER FUNCTIONS FOR BACKWARD COMPATIBILITY ---
def namegen() -> str:
    letters = "abcdefghijklmnopqrstuvwxyz"
    return "".join(random.choices(letters, k=8)).capitalize()

def mailgen() -> str:
    return generate_temp_email()

def link_boisson_gen() -> str:
    code = format_boisson_code()
    return f"https://basic-fit-qr-code-generator.herokuapp.com/create-qr-code?data={code}"

def save_visitor_info(user_agent, link, type_qr, nom, prenom, image_tag=None):
    save_pass(
        pass_type=type_qr,
        nom=nom,
        prenom=prenom,
        link=link,
        image_tag=image_tag or link,
        user_agent=user_agent
    )

# --- ROUTES ---

@app.route('/')
@app.route('/home')
def home():
    stats = get_stats()
    recent_passes = get_all_passes()[:5]
    return render_template(
        "index.html",
        isDay=True,
        isWeek=True,
        stats=stats,
        recent_passes=recent_passes
    )

@app.route('/result_week', methods=['POST'])
def result_week():
    user_agent = request.headers.get('User-Agent', '')
    nom = request.form.get('nom', '').strip() or namegen()
    prenom = request.form.get('prenom', '').strip() or namegen()
    
    img_src, link, msg = execute_week_pass(user_agent, nom, prenom)
    flash(msg, "success")
    return render_template(
        'index.html',
        link=img_src,
        qr_code_data=link,
        nom=nom,
        prenom=prenom,
        pass_type="Semaine",
        isDay=False,
        isWeek=True
    )

@app.route('/result_day', methods=['POST'])
def result_day():
    user_agent = request.headers.get('User-Agent', '')
    nom = request.form.get('nom', '').strip() or namegen()
    prenom = request.form.get('prenom', '').strip() or namegen()
    
    img_src, link, msg = execute_day_pass(user_agent, nom, prenom)
    flash(msg, "success")
    return render_template(
        'index.html',
        link=img_src,
        qr_code_data=link,
        nom=nom,
        prenom=prenom,
        pass_type="Jour",
        isWeek=False,
        isDay=True
    )

@app.route('/history')
def result_history():
    pass_filter = request.args.get('type')
    valid_entries = get_all_passes(pass_type=pass_filter)
    stats = get_stats()
    return render_template(
        'index.html',
        isWeek=False,
        isDay=False,
        visitor_data=valid_entries,
        stats=stats,
        current_filter=pass_filter
    )

@app.route('/mark_used/<int:qr_id>', methods=['POST'])
def mark_used(qr_id):
    success = mark_as_used(qr_id)
    if success:
        flash("Pass marqué comme utilisé ! 2 essais boissons ont été crédités.", "success")
        return redirect(url_for('boissons'))
    flash(f"QR code #{qr_id} introuvable.", "warning")
    return redirect(url_for('result_history'))

@app.route('/get_boisson_image', methods=['POST', 'GET'])
def boisson_affiche():
    if request.method == 'POST':
        user_agent = request.headers.get('User-Agent', '')
        nom = request.form.get('nom', '').strip() or "Client"
        prenom = request.form.get('prenom', '').strip() or "Boisson"
        code = format_boisson_code()
        
        # Generate both high-res data URL and standard link
        data_url = generate_qr_data_url(code)
        online_link = f"https://basic-fit-qr-code-generator.herokuapp.com/create-qr-code?data={code}"
        
        save_pass(
            pass_type="boisson",
            nom=nom,
            prenom=prenom,
            link=online_link,
            image_tag=data_url,
            user_agent=user_agent,
            qr_data=code,
            status="used",
            essais_restants=2
        )
        flash(f"Nouveau QR Boisson généré : {code} (2 essais crédités)", "success")
        return render_template('boissonNew.html', link=data_url, raw_code=code, isGen=True)
        
    return render_template('boissonNew.html', isGen=False)

@app.route('/boissons')
def boissons():
    used_entries = get_all_passes(status='used')
    # Include all boisson passes
    all_drinks = [e for e in get_all_passes() if e.get("pass_type") == "boisson" or e.get("essais_restants", 0) > 0]
    return render_template('boissons.html', used_entries=all_drinks)

@app.route('/use_drink/<int:qr_id>', methods=['POST'])
def use_drink(qr_id):
    success = use_drink_attempt(qr_id)
    if success:
        flash("Un essai boisson a été consommé avec succès !", "success")
    else:
        flash(f"QR boisson #{qr_id} introuvable.", "danger")
    return redirect(url_for('boissons'))

@app.route('/delete_pass/<int:qr_id>', methods=['POST'])
def delete_pass(qr_id):
    success = delete_pass_by_id(qr_id)
    if success:
        flash(f"Pass #{qr_id} supprimé avec succès.", "info")
    return redirect(request.referrer or url_for('result_history'))

@app.route('/app')
def appGen():
    return render_template("qrAppGen.html")

@app.route('/generate_app_qr', methods=['POST'])
def generate_app_qr():
    card_number = request.form.get("card_number", "").strip() or "V00347833"
    device_id = request.form.get("device_id", "").strip() or "8d20fc96-1b0e-4982-8292-e97caed114ec"
    user_agent = request.headers.get('User-Agent', '')
    
    code = format_app_card_code(card_number, device_id=device_id)
    data_url = generate_qr_data_url(code)
    
    save_pass(
        pass_type="app",
        nom="Carte Portique",
        prenom=card_number,
        card_number=card_number,
        link=code,
        image_tag=data_url,
        user_agent=user_agent,
        qr_data=code,
        status="active"
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({
            "status": "success",
            "image": data_url,
            "code": code,
            "card_number": card_number
        })
        
    flash(f"QR Portique généré pour la carte {card_number}", "success")
    return render_template("qrAppGen.html", link=data_url, card_number=card_number, raw_code=code)

# --- NATIVE QR IMAGE API ---
@app.route('/api/qr')
def serve_qr_image():
    """Live high-speed QR generator endpoint."""
    data = request.args.get("data", "https://basic-fit.com")
    png_bytes = generate_qr_png_bytes(data)
    return send_file(
        io.BytesIO(png_bytes),
        mimetype="image/png",
        as_attachment=False,
        download_name="qr_code.png"
    )

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "service": "mon-generateur-qr", "version": "2.0.0"})

# --- ERROR HANDLERS ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template("index.html", error_message="Page introuvable (404).", isDay=True, isWeek=True), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("index.html", error_message="Une erreur interne est survenue. Le système a sécurisé vos données.", isDay=True, isWeek=True), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)