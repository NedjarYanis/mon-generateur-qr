import io
import base64
import random
import time
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
    img = qr.make_image(fill_color="#10121a", back_color="#ffffff")
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

def format_app_card_code(card_number: str) -> str:
    """Generate official Basic-Fit app card format: GM2:{card_number}:BPZ:{timestamp}:95A5CAF2."""
    clean_card = (card_number or "12345678").strip()
    timestamp_ms = int(time.time() * 1000)
    return f"GM2:{clean_card}:BPZ:{timestamp_ms}:95A5CAF2"

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
