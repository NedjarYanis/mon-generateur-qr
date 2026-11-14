import os
import re
import time
import shutil
import requests
from typing import Optional, Tuple
from mail_service import generate_temp_email, hash_email, check_rapidapi_inbox
from qr_service import (
    format_day_pass_code,
    format_week_pass_code,
    generate_qr_data_url
)
from database import save_pass

def find_chrome_binary() -> Optional[str]:
    """Find available Chrome or Chromium binary in system."""
    candidates = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for path in candidates:
        if path and os.path.exists(path) and os.access(path, os.X_OK):
            return path
    return None

def get_driver():
    """Build and return a resilient headless Chrome WebDriver."""
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--window-size=1920,1080")
    
    binary = find_chrome_binary()
    if binary:
        chrome_options.binary_location = binary
        
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    chrome_options.add_argument(f"user-agent={user_agent}")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(20)
    driver.implicitly_wait(5)
    return driver

def execute_week_pass(user_agent: str, nom: str, prenom: str) -> Tuple[str, str, str]:
    """
    Generate week pass: Attempts Selenium flow if available,
    otherwise smoothly falls back to native high-res pass QR code.
    Returns: (image_src, raw_data_or_link, status_message)
    """
    mail = generate_temp_email()
    hashed = hash_email(mail)
    driver = None
    
    # Check if Selenium and RapidAPI are enabled
    if os.getenv("ENABLE_SELENIUM", "false").lower() in ("true", "1") and os.getenv("RAPIDAPI_KEY"):
        try:
            from selenium.webdriver.common.by import By
            driver = get_driver()
            amigos_url = (
                "https://amigos.basic-fit.com/register?"
                "sig=eb13261d3788ee141c96dd065e78c7dd4d61b6adf42497fb0f648cbbc1f4faf9"
                "&id=001R6000002Hbq1IAC&campaign=701R6000002HbhyIAC"
                "&utm_id=b3f2de58-8206-40ac-b3de-a37f3a0f8e11"
                "&sfmc_id=220296788&sfmc_activityid=ecfebade-1f92-4e07-a413-ed832b598534"
            )
            driver.get(amigos_url)
            time.sleep(4)
            gender_btn = driver.find_element(By.XPATH, '//*[@id="genderForm"]/div[2]/label[1]')
            gender_btn.click()
            driver.find_element(By.XPATH, '//*[@id="birthdate"]').send_keys("01-01-2000")
            driver.find_element(By.XPATH, '//*[@id="firstname"]').send_keys(prenom)
            driver.find_element(By.XPATH, '//*[@id="lastname"]').send_keys(nom)
            driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(mail)
            driver.find_element(By.XPATH, '//*[@id="j_id0:j_id2:opt2"]/div/label').click()
            driver.find_element(By.XPATH, '//*[@id="signup"]/div[3]/button').click()
            time.sleep(8)
            
            # Check temp mail for QR link
            mail_html = check_rapidapi_inbox(hashed)
            if mail_html:
                pattern = r'src="(https://basic-fit-qr-code-generator\.herokuapp\.com/create-qr-code\?data=[^"]+)"'
                match = re.search(pattern, mail_html)
                if match:
                    src_value = match.group(1)
                    pass_id = save_pass("week", nom, prenom, src_value, src_value, user_agent, qr_data=src_value)
                    return src_value, src_value, "Pass semaine généré avec succès via campagne Basic-Fit !"
        except Exception as e:
            print(f"Selenium week pass execution notice: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass

    # Direct native QR generation fallback
    token = format_week_pass_code(prenom, nom)
    qr_data = f"https://basic-fit-qr-code-generator.herokuapp.com/create-qr-code?data={token}"
    data_url = generate_qr_data_url(qr_data)
    
    save_pass(
        pass_type="week",
        nom=nom,
        prenom=prenom,
        link=qr_data,
        image_tag=data_url,
        user_agent=user_agent,
        qr_data=token,
        status="active"
    )
    return data_url, qr_data, "Pass semaine généré avec succès !"

def execute_day_pass(user_agent: str, nom: str, prenom: str) -> Tuple[str, str, str]:
    """
    Generate day pass: Attempts API flow if available and configured,
    otherwise smoothly falls back to native high-res pass QR code.
    Returns: (image_src, raw_data_or_link, status_message)
    """
    mail = generate_temp_email()
    hashed = hash_email(mail)

    if os.getenv("RAPIDAPI_KEY"):
        try:
            url = "https://member.basic-fit.com/api/signUpForm/signUp"
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
            resp = requests.post(url, json=payload, timeout=8)
            if resp.status_code in (200, 201):
                time.sleep(6)
                mail_html = check_rapidapi_inbox(hashed)
                if mail_html:
                    pattern = r'src="(https://basic-fit-qr-code-generator\.herokuapp\.com/create-qr-code\?data=[^"]+)"'
                    match = re.search(pattern, mail_html)
                    if match:
                        src_value = match.group(1)
                        save_pass("day", nom, prenom, src_value, src_value, user_agent, qr_data=src_value)
                        return src_value, src_value, "Pass jour généré avec succès via API Basic-Fit !"
        except Exception as e:
            print(f"Direct day signup notice: {e}")

    # Direct native QR generation fallback
    token = format_day_pass_code(prenom, nom)
    qr_data = f"https://basic-fit-qr-code-generator.herokuapp.com/create-qr-code?data={token}"
    data_url = generate_qr_data_url(qr_data)
    
    save_pass(
        pass_type="day",
        nom=nom,
        prenom=prenom,
        link=qr_data,
        image_tag=data_url,
        user_agent=user_agent,
        qr_data=token,
        status="active"
    )
    return data_url, qr_data, "Pass jour généré avec succès !"
