import io
import base64
import random
import time
import hashlib
import qrcode
from PIL import Image

def generate_qr_image(data: str, box_size: int = 10, border: int = 2) -> Image.Image:
    """Generate a high quality QR Code PIL Image with Basic-Fit brand styling."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#000000", back_color="#ffffff")
    return img

def generate_qr_png_bytes(data: str) -> bytes:
    """Return raw PNG bytes of the generated QR code."""
    img = generate_qr_image(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def generate_qr_data_url(data: str) -> str:
    """Return a base64 Data URL (data:image/png;base64,...) for embedding in HTML/CSS."""
    png_bytes = generate_qr_png_bytes(data)
    encoded = base64.b64encode(png_bytes).decode("ascii")
    return f"data:image/png;base64,{encoded}"

def format_boisson_code() -> str:
    """Generate random Basic-Fit boisson code: V000 + 6 digits."""
    digits = "".join(random.choices("0123456789", k=6))
    return f"V000{digits}"

def format_app_card_code(
    card_number: str,
    device_id: str = "8d20fc96-1b0e-4982-8292-e97caed114ec",
    guid: str = "2L8"
) -> str:
    """
    Generate authentic Basic-Fit turnstile QR code format:
    GM2:{CARD_NUMBER}:{GUID}:{TIMESTAMP_SECONDS}:{SHA256_LAST_8}
    """
    card = (card_number or "V00347833").strip().upper()
    if not card.startswith("V") and len(card) >= 7 and card.isdigit():
        card = f"V{card}"
        
    dev_id = (device_id or "8d20fc96-1b0e-4982-8292-e97caed114ec").strip()
    clean_guid = (guid or "2L8").strip().upper()
    
    # Unix timestamp in SECONDS (10 digits)
    timestamp = str(int(time.time()))
    
    # Compute SHA256 of card + guid + timestamp + device_id
    raw_payload = f"{card}{clean_guid}{timestamp}{dev_id}"
    sha256_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
    last8_hash = sha256_hash[-8:].upper()
    
    return f"GM2:{card}:{clean_guid}:{timestamp}:{last8_hash}"

def format_day_pass_code(first_name: str, last_name: str) -> str:
    """Generate a structured day pass token."""
    rand_token = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=8))
    timestamp = int(time.time())
    return f"BF-DAY-{timestamp}-{rand_token}"

def format_week_pass_code(first_name: str, last_name: str) -> str:
    """Generate a structured week pass token."""
    rand_token = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ23456789", k=10))
    timestamp = int(time.time())
    return f"BF-WEEK-{timestamp}-{rand_token}"
