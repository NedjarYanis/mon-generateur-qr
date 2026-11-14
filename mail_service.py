import os
import random
import hashlib
import requests
from typing import Optional, List

DEFAULT_DOMAINS = [
    "@quickmail.site",
    "@tempmail.net",
    "@inboxpass.com",
    "@gymtemp.org",
    "@burnermail.io"
]

def hash_email(email: str) -> str:
    """Return MD5 hash of email."""
    return hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()

def random_string(length: int = 12) -> str:
    letters = "abcdefghijklmnopqrstuvwxyz"
    return "".join(random.choices(letters, k=length))

def get_rapidapi_domains() -> List[str]:
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return DEFAULT_DOMAINS
    
    url = "https://privatix-temp-mail-v1.p.rapidapi.com/request/domains/"
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "privatix-temp-mail-v1.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data
    except Exception as e:
        print(f"RapidAPI domains fetch error: {e}")
    return DEFAULT_DOMAINS

def generate_temp_email() -> str:
    """Generate a temporary email address safely without crashing."""
    prefix = random_string(12)
    domains = get_rapidapi_domains()
    domain = random.choice(domains)
    if not domain.startswith("@"):
        domain = f"@{domain}"
    return f"{prefix}{domain}"

def check_rapidapi_inbox(hashed_email: str) -> Optional[str]:
    """Check RapidAPI privatix temp mail inbox for QR pass link."""
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        return None
    
    url = f"https://privatix-temp-mail-v1.p.rapidapi.com/request/mail/id/{hashed_email}/"
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "privatix-temp-mail-v1.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0].get("mail_html", "")
    except Exception as e:
        print(f"RapidAPI inbox check error: {e}")
    return None
