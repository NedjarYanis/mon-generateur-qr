import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_FILE = os.environ.get("DATABASE_PATH", "passes.db")

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS passes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pass_type TEXT NOT NULL,
                nom TEXT DEFAULT '',
                prenom TEXT DEFAULT '',
                card_number TEXT DEFAULT '',
                qr_data TEXT DEFAULT '',
                link TEXT NOT NULL,
                image_tag TEXT DEFAULT '',
                user_agent TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                essais_restants INTEGER DEFAULT 0,
                extra_data TEXT DEFAULT '{}'
            )
        """)
        conn.commit()
    migrate_legacy_json_files()

def migrate_legacy_json_files():
    # Migrate visitor_log.json if present
    if os.path.exists("visitor_log.json"):
        try:
            with open("visitor_log.json", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                        save_pass(
                            pass_type=item.get("duree", "day"),
                            nom=item.get("Nom", ""),
                            prenom=item.get("Prenom", ""),
                            link=item.get("link", ""),
                            image_tag=item.get("image_tag", item.get("link", "")),
                            user_agent=item.get("user_agent", ""),
                            status="active",
                            essais_restants=0,
                            legacy_id=item.get("id"),
                            timestamp=item.get("timestamp")
                        )
                    except Exception as e:
                        print(f"Error migrating line from visitor_log.json: {e}")
        except Exception as e:
            print(f"Error opening visitor_log.json for migration: {e}")

    # Migrate used_qr_codes.json if present
    if os.path.exists("used_qr_codes.json"):
        try:
            with open("used_qr_codes.json", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                        save_pass(
                            pass_type="boisson",
                            nom=item.get("Nom", ""),
                            prenom=item.get("Prenom", ""),
                            link=item.get("link", ""),
                            image_tag=item.get("image_tag", item.get("link", "")),
                            user_agent=item.get("user_agent", ""),
                            status="used",
                            essais_restants=item.get("essais_restants", 2),
                            legacy_id=item.get("id"),
                            timestamp=item.get("timestamp")
                        )
                    except Exception as e:
                        print(f"Error migrating line from used_qr_codes.json: {e}")
        except Exception as e:
            print(f"Error opening used_qr_codes.json for migration: {e}")

def save_pass(
    pass_type: str,
    nom: str,
    prenom: str,
    link: str,
    image_tag: Optional[str] = None,
    user_agent: str = "",
    card_number: str = "",
    qr_data: str = "",
    status: str = "active",
    essais_restants: int = 0,
    legacy_id: Optional[int] = None,
    timestamp: Optional[str] = None
) -> int:
    created_at = timestamp or datetime.now().isoformat()
    img = image_tag if image_tag is not None else link

    with get_db_connection() as conn:
        cursor = conn.cursor()
        if legacy_id is not None:
            # Check if this legacy record is already migrated
            cursor.execute("SELECT id FROM passes WHERE id = ?", (legacy_id,))
            existing = cursor.fetchone()
            if existing:
                return existing["id"]
            cursor.execute("""
                INSERT INTO passes (id, pass_type, nom, prenom, card_number, qr_data, link, image_tag, user_agent, created_at, status, essais_restants)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (legacy_id, pass_type, nom, prenom, card_number, qr_data, link, img, user_agent, created_at, status, essais_restants))
            conn.commit()
            return legacy_id
        else:
            cursor.execute("""
                INSERT INTO passes (pass_type, nom, prenom, card_number, qr_data, link, image_tag, user_agent, created_at, status, essais_restants)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pass_type, nom, prenom, card_number, qr_data, link, img, user_agent, created_at, status, essais_restants))
            conn.commit()
            return cursor.lastrowid

def get_all_passes(pass_type: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
    with get_db_connection() as conn:
        query = "SELECT * FROM passes WHERE 1=1"
        params = []
        if pass_type:
            query += " AND pass_type = ?"
            params.append(pass_type)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY id DESC"
        cursor = conn.execute(query, params)
        rows = cursor.fetchall()
        
        # Format compatible with both legacy templates and modern UI
        result = []
        for r in rows:
            d = dict(r)
            # Add legacy capitalized keys for template backward compatibility
            d["Nom"] = d["nom"]
            d["Prenom"] = d["prenom"]
            d["duree"] = d["pass_type"]
            d["timestamp"] = d["created_at"]
            result.append(d)
        return result

def get_pass_by_id(pass_id: int) -> Optional[Dict[str, Any]]:
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM passes WHERE id = ?", (pass_id,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d["Nom"] = d["nom"]
        d["Prenom"] = d["prenom"]
        d["duree"] = d["pass_type"]
        d["timestamp"] = d["created_at"]
        return d

def mark_as_used(pass_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute(
            "UPDATE passes SET status = 'used', essais_restants = 2 WHERE id = ?",
            (pass_id,)
        )
        conn.commit()
        return cursor.rowcount > 0

def use_drink_attempt(pass_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT essais_restants FROM passes WHERE id = ?", (pass_id,))
        row = cursor.fetchone()
        if not row:
            return False
        
        remaining = row["essais_restants"] - 1
        new_status = "consumed" if remaining <= 0 else "used"
        remaining = max(0, remaining)
        
        conn.execute(
            "UPDATE passes SET essais_restants = ?, status = ? WHERE id = ?",
            (remaining, new_status, pass_id)
        )
        conn.commit()
        return True

def delete_pass_by_id(pass_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM passes WHERE id = ?", (pass_id,))
        conn.commit()
        return cursor.rowcount > 0

def get_stats() -> Dict[str, int]:
    with get_db_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM passes").fetchone()[0]
        active = conn.execute("SELECT COUNT(*) FROM passes WHERE status = 'active'").fetchone()[0]
        used = conn.execute("SELECT COUNT(*) FROM passes WHERE status = 'used'").fetchone()[0]
        drinks = conn.execute("SELECT COUNT(*) FROM passes WHERE pass_type = 'boisson' OR status = 'used'").fetchone()[0]
        return {
            "total": total,
            "active": active,
            "used": used,
            "drinks": drinks
        }
