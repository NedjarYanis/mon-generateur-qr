import os
import pytest
from app import app
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
    generate_qr_image,
    generate_qr_png_bytes,
    generate_qr_data_url,
    format_boisson_code,
    format_app_card_code,
    format_day_pass_code,
    format_week_pass_code
)
from mail_service import generate_temp_email, hash_email

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

def test_qr_service():
    # Test QR image generation
    img = generate_qr_image("TEST-QR")
    assert img is not None
    assert img.size[0] > 0

    # Test PNG bytes
    png_bytes = generate_qr_png_bytes("TEST-BYTES")
    assert png_bytes.startswith(b"\x89PNG")

    # Test Data URL
    data_url = generate_qr_data_url("TEST-DATA-URL")
    assert data_url.startswith("data:image/png;base64,")

    # Test code formatters
    boisson = format_boisson_code()
    assert boisson.startswith("V000")
    assert len(boisson) == 10

    app_card = format_app_card_code("80012345")
    assert "GM2:80012345:BPZ:" in app_card
    assert app_card.endswith(":95A5CAF2")

    day_code = format_day_pass_code("Jean", "Dupont")
    assert day_code.startswith("BF-DAY-")

    week_code = format_week_pass_code("Jean", "Dupont")
    assert week_code.startswith("BF-WEEK-")

def test_mail_service():
    email = generate_temp_email()
    assert "@" in email
    assert len(email) > 10

    h = hash_email("test@example.com")
    assert len(h) == 32

def test_database_crud():
    pass_id = save_pass(
        pass_type="day",
        nom="TestNom",
        prenom="TestPrenom",
        link="https://example.com/qr",
        image_tag="data:image/png;base64,abc",
        user_agent="Pytest-Agent"
    )
    assert pass_id is not None
    assert pass_id > 0

    fetched = get_pass_by_id(pass_id)
    assert fetched is not None
    assert fetched["nom"] == "TestNom"
    assert fetched["prenom"] == "TestPrenom"
    assert fetched["status"] == "active"

    # Mark as used
    ok = mark_as_used(pass_id)
    assert ok is True
    updated = get_pass_by_id(pass_id)
    assert updated["status"] == "used"
    assert updated["essais_restants"] == 2

    # Consume drink attempt
    ok2 = use_drink_attempt(pass_id)
    assert ok2 is True
    updated2 = get_pass_by_id(pass_id)
    assert updated2["essais_restants"] == 1

    # Consume second drink attempt -> status becomes consumed
    ok3 = use_drink_attempt(pass_id)
    assert ok3 is True
    updated3 = get_pass_by_id(pass_id)
    assert updated3["essais_restants"] == 0
    assert updated3["status"] == "consumed"

    # Stats
    stats = get_stats()
    assert stats["total"] >= 1

    # Delete
    del_ok = delete_pass_by_id(pass_id)
    assert del_ok is True
    assert get_pass_by_id(pass_id) is None

def test_home_page(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b"Basic-Fit" in res.data
    assert b"Pass Semaine" in res.data
    assert b"Pass Journ" in res.data

def test_result_day_generation(client):
    res = client.post('/result_day', data={'prenom': 'Alice', 'nom': 'Martin'})
    assert res.status_code == 200
    assert b"Alice" in res.data
    assert b"Martin" in res.data
    assert b"Pass Journ" in res.data

def test_result_day_empty_generation(client):
    res = client.post('/result_day', data={'prenom': '', 'nom': ''})
    assert res.status_code == 200
    assert b"Pass Journ" in res.data

def test_result_week_generation(client):
    res = client.post('/result_week', data={'prenom': 'Bob', 'nom': 'Bernard'})
    assert res.status_code == 200
    assert b"Bob" in res.data
    assert b"Bernard" in res.data
    assert b"Pass Semaine" in res.data

def test_history_page(client):
    res = client.get('/history')
    assert res.status_code == 200
    assert b"Historique des passes" in res.data

def test_history_filters(client):
    for f in ['day', 'week', 'boisson', 'app']:
        res = client.get(f'/history?type={f}')
        assert res.status_code == 200

def test_boissons_flow(client):
    # Generate drink QR
    res = client.post('/get_boisson_image', data={'prenom': 'DrinkUser', 'nom': 'Tester'})
    assert res.status_code == 200
    assert b"QR Boisson" in res.data
    assert b"V000" in res.data

    # Check /boissons
    res2 = client.get('/boissons')
    assert res2.status_code == 200
    assert b"DrinkUser" in res2.data

def test_mark_used_and_use_drink_endpoints(client):
    # Create pass to test mark_used
    pid = save_pass("day", "Jean", "Valjean", "https://link", "data:img")
    
    # Mark used -> redirects to /boissons
    res = client.post(f'/mark_used/{pid}', follow_redirects=True)
    assert res.status_code == 200
    assert b"marqu" in res.data or b"cr\xc3\xa9dit" in res.data

    # Consume drink attempt -> redirects to /boissons
    res2 = client.post(f'/use_drink/{pid}', follow_redirects=True)
    assert res2.status_code == 200

    # Non-existent ID handling
    res3 = client.post('/mark_used/999999', follow_redirects=True)
    assert res3.status_code == 200

    res4 = client.post('/use_drink/999999', follow_redirects=True)
    assert res4.status_code == 200

    # Delete pass
    res5 = client.post(f'/delete_pass/{pid}', follow_redirects=True)
    assert res5.status_code == 200

def test_app_card_generation(client):
    # Form post
    res = client.post('/generate_app_qr', data={'card_number': '99887766'})
    assert res.status_code == 200
    assert b"99887766" in res.data

    # AJAX post
    res_ajax = client.post(
        '/generate_app_qr',
        data={'card_number': '11223344'},
        headers={'X-Requested-With': 'XMLHttpRequest'}
    )
    assert res_ajax.status_code == 200
    data = res_ajax.get_json()
    assert data["status"] == "success"
    assert "GM2:11223344:BPZ:" in data["code"]
    assert data["image"].startswith("data:image/png;base64,")

def test_api_qr_endpoint(client):
    res = client.get('/api/qr?data=HELLO-TEST')
    assert res.status_code == 200
    assert res.content_type == "image/png"
    assert res.data.startswith(b"\x89PNG")

def test_api_health(client):
    res = client.get('/api/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"

def test_404_handler(client):
    res = client.get('/nonexistent-page-test-404')
    assert res.status_code == 404
    assert b"404" in res.data
