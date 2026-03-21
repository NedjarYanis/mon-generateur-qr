from flask import Flask, render_template, url_for, request, redirect
import random
import re
import time
import json
import hashlib
import requests
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

app = Flask(__name__)
isWeek = True
isDay = True

# --- CONFIGURATION SELENIUM POUR RENDER ---
def get_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    # Chemin vers le binaire Chrome installé par le Dockerfile
    chrome_options.binary_location = "/usr/bin/google-chrome"
    
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')
    
    return webdriver.Chrome(options=chrome_options)

# --- FONCTIONS UTILES ---
def get_domain():
    url2 = "https://privatix-temp-mail-v1.p.rapidapi.com/request/domains/"
    headers = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
        'x-rapidapi-host': "privatix-temp-mail-v1.p.rapidapi.com"
    }
    response2 = requests.get(url2, headers=headers)
    return response2.json()

def mailgen():
    letter = "abcdefghijklmnopqrstuvwxyz"
    millieu = "".join(random.sample(letter, 13))
    domain_list = get_domain()
    domain = domain_list[random.randint(0, len(domain_list) - 1)]
    return str(millieu) + domain

def namegen():
    letter = "abcdefghijklmnopqrstuvwxyz"
    return "".join(random.sample(letter, 13))

def hash_email(email):
    return hashlib.md5(email.encode('utf-8')).hexdigest()

def link_boisson_gen():
    link = "https://basic-fit-qr-code-generator.herokuapp.com/create-qr-code?data=V000"
    numbers = "0123456789"
    millieu = "".join(random.sample(numbers, 6))
    return link + str(millieu)

# --- LOGIQUE D'EXECUTION ---
def execute_week(ua, nom, prenom):
    driver = get_driver()
    mail = mailgen()
    hashed_email = hash_email(mail)

    try:
        driver.get('https://amigos.basic-fit.com/register?sig=eb13261d3788ee141c96dd065e78c7dd4d61b6adf42497fb0f648cbbc1f4faf9&id=001R6000002Hbq1IAC&campaign=701R6000002HbhyIAC&utm_id=b3f2de58-8206-40ac-b3de-a37f3a0f8e11&sfmc_id=220296788&sfmc_activityid=ecfebade-1f92-4e07-a413-ed832b598534')
        time.sleep(5)
        driver.find_element(By.XPATH, '//*[@id="genderForm"]/div[2]/label[1]').click()
        driver.find_element(By.XPATH, '//*[@id="birthdate"]').send_keys("01-01-2000")
        driver.find_element(By.XPATH, '//*[@id="firstname"]').send_keys(nom)
        driver.find_element(By.XPATH, '//*[@id="lastname"]').send_keys(prenom)
        driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(mail)
        driver.find_element(By.XPATH, '//*[@id="j_id0:j_id2:opt2"]/div/label').click()
        driver.find_element(By.XPATH, '//*[@id="signup"]/div[3]/button').click()
        time.sleep(10)
    finally:
        driver.quit()

    url = f"https://privatix-temp-mail-v1.p.rapidapi.com/request/mail/id/{hashed_email}/"
    headers = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
        'x-rapidapi-host': "privatix-temp-mail-v1.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200 and len(response.json()) > 0:
        html_content = response.json()[0]['mail_html']
        pattern = r'src="(https://basic-fit-qr-code-generator\.herokuapp\.com/create-qr-code\?data=[^"]+)"'
        match = re.search(pattern, html_content)
        if match:
            src_value = match.group(1)
            save_visitor_info(ua, src_value, "week", nom, prenom, src_value)
            return src_value
    return None

def execute_day(ua, nom, prenom):
    # Utilisation directe de l'API pour le Day Pass (plus léger que Selenium)
    url = "https://member.basic-fit.com/api/signUpForm/signUp"
    mail = mailgen()
    payload = {
        "firstName": nom,
        "lastName": prenom,
        "email": mail,
        "locale": "fr-FR",
        "dateOfBirth": "2005-10-10T00:00:00.000Z",
        "promotions": True,
        "tos": True,
        "campaignId": "2Hl7qICv6IYQIWyHqWQou0"
    }
    headers = { "Content-Type": "application/json", "User-Agent": ua }
    
    requests.post(url, json=payload, headers=headers)
    time.sleep(10)
    
    hashed_email = hash_email(mail)
    url_mail = f"https://privatix-temp-mail-v1.p.rapidapi.com/request/mail/id/{hashed_email}/"
    headers_api = {
        'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
        'x-rapidapi-host': "privatix-temp-mail-v1.p.rapidapi.com"
    }

    response = requests.get(url_mail, headers=headers_api)
    if response.status_code == 200 and len(response.json()) > 0:
        html_content = response.json()[0]['mail_html']
        pattern = r'src="(https://basic-fit-qr-code-generator\.herokuapp\.com/create-qr-code\?data=[^"]+)"'
        match = re.search(pattern, html_content)
        if match:
            src_value = match.group(1)
            save_visitor_info(ua, src_value, "day", nom, prenom, src_value)
            return src_value
    return None

# --- GESTION DES FICHIERS ---
def save_visitor_info(user_agent, link, type_qr, nom, prenom, image_tag=None):
    try:
        next_id = 1
        if os.path.exists("visitor_log.json"):
            with open("visitor_log.json", "r") as f:
                lines = f.readlines()
                if lines:
                    next_id = json.loads(lines[-1])["id"] + 1
        
        data = {
            "id": next_id,
            "timestamp": datetime.now().isoformat(),
            "user_agent": user_agent,
            "link": link,
            "image_tag": image_tag,
            "Nom": nom,
            "Prenom": prenom,
            "duree": type_qr
        }
        with open("visitor_log.json", "a") as f:
            json.dump(data, f)
            f.write("\n")
    except Exception as e:
        print(f"Erreur sauvegarde: {e}")

# --- ROUTES FLASK ---
@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html", isDay=isDay, isWeek=isWeek)

@app.route('/result_week', methods=['POST'])
def result_week():
    user_agent = request.headers.get('User-Agent')
    nom = request.form.get('nom') or namegen()
    prenom = request.form.get('prenom') or namegen()
    link = execute_week(user_agent, nom, prenom)
    return render_template('index.html', link=link, isDay=False, isWeek=True)

@app.route('/result_day', methods=['POST'])
def result_day():
    user_agent = request.headers.get('User-Agent')
    nom = request.form.get('nom') or namegen()
    prenom = request.form.get('prenom') or namegen()
    link = execute_day(user_agent, nom, prenom)
    return render_template('index.html', link=link, isWeek=False, isDay=True)

@app.route('/history')
def result_history():
    valid_entries = []
    if os.path.exists("visitor_log.json"):
        with open("visitor_log.json", "r") as f:
            for line in f:
                data = json.loads(line)
                valid_entries.append(data)
    return render_template('index.html', isWeek=False, isDay=False, visitor_data=valid_entries)

@app.route('/boissons')
def boissons():
    used_entries = []
    if os.path.exists("used_qr_codes.json"):
        with open("used_qr_codes.json", "r") as f:
            for line in f:
                used_entries.append(json.loads(line))
    return render_template('boissons.html', used_entries=used_entries)

@app.route('/app')
def appGen():
    return render_template("qrAppGen.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)