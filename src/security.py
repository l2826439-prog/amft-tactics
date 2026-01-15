"""
セキュリティモジュール
- パスワード認証
- セッション管理
- アクセスログ
- ブルートフォース対策
"""

import hashlib
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

# Security config file path
SECURITY_DIR = Path(__file__).parent / "data"
CONFIG_FILE = SECURITY_DIR / "security_config.json"
ACCESS_LOG_FILE = SECURITY_DIR / "access_log.json"

# Default password (hashed) - Change this on first use!
# Default: "tactics2026" 
DEFAULT_PASSWORD_HASH = hashlib.sha256("tactics2026".encode()).hexdigest()

# Session timeout (minutes)
SESSION_TIMEOUT_MINUTES = 30

# Max failed attempts before lockout
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

def ensure_security_dir():
    """Ensure security directory exists"""
    SECURITY_DIR.mkdir(parents=True, exist_ok=True)

def load_config():
    """Load security configuration"""
    ensure_security_dir()
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Create default config
        config = {
            "password_hash": DEFAULT_PASSWORD_HASH,
            "failed_attempts": 0,
            "lockout_until": None,
            "security_enabled": True
        }
        save_config(config)
        return config

def save_config(config):
    """Save security configuration"""
    ensure_security_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str) -> bool:
    """Verify password against stored hash"""
    config = load_config()
    
    # Check if locked out
    if config.get("lockout_until"):
        lockout_time = datetime.fromisoformat(config["lockout_until"])
        if datetime.now() < lockout_time:
            return False
        else:
            # Lockout expired, reset
            config["lockout_until"] = None
            config["failed_attempts"] = 0
            save_config(config)
    
    # Verify password
    input_hash = hash_password(password)
    if input_hash == config["password_hash"]:
        # Reset failed attempts on success
        config["failed_attempts"] = 0
        save_config(config)
        log_access("login_success")
        return True
    else:
        # Increment failed attempts
        config["failed_attempts"] = config.get("failed_attempts", 0) + 1
        if config["failed_attempts"] >= MAX_FAILED_ATTEMPTS:
            config["lockout_until"] = (datetime.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)).isoformat()
            log_access("lockout_triggered")
        save_config(config)
        log_access("login_failed")
        return False

def change_password(old_password: str, new_password: str) -> tuple[bool, str]:
    """Change the password"""
    if not verify_password(old_password):
        return False, "現在のパスワードが正しくありません"
    
    if len(new_password) < 6:
        return False, "パスワードは6文字以上にしてください"
    
    config = load_config()
    config["password_hash"] = hash_password(new_password)
    save_config(config)
    log_access("password_changed")
    return True, "パスワードを変更しました"

def is_locked_out() -> tuple[bool, int]:
    """Check if currently locked out. Returns (is_locked, remaining_minutes)"""
    config = load_config()
    if config.get("lockout_until"):
        lockout_time = datetime.fromisoformat(config["lockout_until"])
        if datetime.now() < lockout_time:
            remaining = int((lockout_time - datetime.now()).total_seconds() / 60) + 1
            return True, remaining
    return False, 0

def get_failed_attempts() -> int:
    """Get current number of failed attempts"""
    config = load_config()
    return config.get("failed_attempts", 0)

def log_access(event_type: str, details: str = ""):
    """Log an access event"""
    ensure_security_dir()
    
    # Load existing log
    log_entries = []
    if ACCESS_LOG_FILE.exists():
        try:
            with open(ACCESS_LOG_FILE, 'r', encoding='utf-8') as f:
                log_entries = json.load(f)
        except:
            log_entries = []
    
    # Add new entry
    log_entries.append({
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "details": details
    })
    
    # Keep only last 100 entries
    log_entries = log_entries[-100:]
    
    # Save
    with open(ACCESS_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_entries, f, indent=2, ensure_ascii=False)

def get_access_log(limit: int = 20) -> list:
    """Get recent access log entries"""
    if ACCESS_LOG_FILE.exists():
        try:
            with open(ACCESS_LOG_FILE, 'r', encoding='utf-8') as f:
                entries = json.load(f)
                return entries[-limit:][::-1]  # Most recent first
        except:
            return []
    return []

def is_security_enabled() -> bool:
    """Check if security is enabled"""
    config = load_config()
    return config.get("security_enabled", True)

def toggle_security(enabled: bool):
    """Enable or disable security"""
    config = load_config()
    config["security_enabled"] = enabled
    save_config(config)
    log_access("security_toggled", f"enabled={enabled}")
