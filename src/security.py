"""
マルチユーザーセキュリティモジュール
- 複数ユーザー対応（管理者 + 一般ユーザー）
- ユーザー登録・認証
- アクセスログ（管理者のみ閲覧可能）
- パスワードリセット（管理者のみ実行可能）
"""

import hashlib
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, List, Dict

# Security config file path
SECURITY_DIR = Path(__file__).parent / "data"
USERS_FILE = SECURITY_DIR / "users.json"
ACCESS_LOG_FILE = SECURITY_DIR / "access_log.json"

# Session timeout (minutes)
SESSION_TIMEOUT_MINUTES = 30

# Max failed attempts before lockout
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15

# User roles
ROLE_ADMIN = "admin"
ROLE_USER = "user"

# Default passwords
DEFAULT_ADMIN_PASSWORD = "admin2026"
DEFAULT_USER_PASSWORD = "tactics2026"

# Admin username
ADMIN_USERNAME = "host_this_app"


def ensure_security_dir():
    """Ensure security directory exists"""
    SECURITY_DIR.mkdir(parents=True, exist_ok=True)


def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def load_users() -> Dict:
    """Load users database"""
    ensure_security_dir()
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # Create default users database with admin
    users = {
        ADMIN_USERNAME: {
            "password_hash": hash_password(DEFAULT_ADMIN_PASSWORD),
            "role": ROLE_ADMIN,
            "created_at": datetime.now().isoformat(),
            "failed_attempts": 0,
            "lockout_until": None
        }
    }
    save_users(users)
    return users


def save_users(users: Dict):
    """Save users database"""
    ensure_security_dir()
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def user_exists(username: str) -> bool:
    """Check if a username exists"""
    users = load_users()
    return username.lower() in [u.lower() for u in users.keys()]


def register_user(username: str, password: str = None) -> Tuple[bool, str]:
    """Register a new user with default or specified password"""
    if not username or len(username) < 3:
        return False, "ユーザー名は3文字以上にしてください"
    
    if user_exists(username):
        return False, "このユーザー名はすでに使用されています"
    
    if username.lower() == ADMIN_USERNAME.lower():
        return False, "このユーザー名は使用できません"
    
    users = load_users()
    users[username] = {
        "password_hash": hash_password(password or DEFAULT_USER_PASSWORD),
        "role": ROLE_USER,
        "created_at": datetime.now().isoformat(),
        "failed_attempts": 0,
        "lockout_until": None
    }
    save_users(users)
    log_access("user_registered", username)
    return True, f"ユーザー「{username}」を登録しました（初期パスワード: {DEFAULT_USER_PASSWORD}）"


def verify_user(username: str, password: str) -> Tuple[bool, Optional[str]]:
    """Verify user credentials. Returns (success, role or None)"""
    users = load_users()
    
    # Find user (case-insensitive)
    actual_username = None
    for u in users.keys():
        if u.lower() == username.lower():
            actual_username = u
            break
    
    if not actual_username:
        log_access("login_failed_unknown_user", username)
        return False, None
    
    user = users[actual_username]
    
    # Check lockout
    if user.get("lockout_until"):
        lockout_time = datetime.fromisoformat(user["lockout_until"])
        if datetime.now() < lockout_time:
            return False, None
        else:
            user["lockout_until"] = None
            user["failed_attempts"] = 0
            save_users(users)
    
    # Verify password
    if hash_password(password) == user["password_hash"]:
        user["failed_attempts"] = 0
        save_users(users)
        log_access("login_success", actual_username)
        return True, user["role"]
    else:
        user["failed_attempts"] = user.get("failed_attempts", 0) + 1
        if user["failed_attempts"] >= MAX_FAILED_ATTEMPTS:
            user["lockout_until"] = (datetime.now() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)).isoformat()
            log_access("lockout_triggered", actual_username)
        save_users(users)
        log_access("login_failed", actual_username)
        return False, None


def change_password(username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
    """Change user's own password"""
    success, _ = verify_user(username, old_password)
    if not success:
        return False, "現在のパスワードが正しくありません"
    
    if len(new_password) < 6:
        return False, "パスワードは6文字以上にしてください"
    
    users = load_users()
    for u in users.keys():
        if u.lower() == username.lower():
            users[u]["password_hash"] = hash_password(new_password)
            save_users(users)
            log_access("password_changed", username)
            return True, "パスワードを変更しました"
    
    return False, "ユーザーが見つかりません"


def admin_reset_password(target_username: str) -> Tuple[bool, str]:
    """Admin resets a user's password to default (admin only)"""
    users = load_users()
    
    for u in users.keys():
        if u.lower() == target_username.lower():
            users[u]["password_hash"] = hash_password(DEFAULT_USER_PASSWORD)
            users[u]["failed_attempts"] = 0
            users[u]["lockout_until"] = None
            save_users(users)
            log_access("admin_password_reset", f"target={target_username}")
            return True, f"「{target_username}」のパスワードを初期化しました（新パスワード: {DEFAULT_USER_PASSWORD}）"
    
    return False, "ユーザーが見つかりません"


def get_all_users() -> List[Dict]:
    """Get list of all users (admin only)"""
    users = load_users()
    result = []
    for username, data in users.items():
        result.append({
            "username": username,
            "role": data.get("role", ROLE_USER),
            "created_at": data.get("created_at", "不明"),
            "is_locked": data.get("lockout_until") is not None
        })
    return result


def is_admin(username: str) -> bool:
    """Check if user is admin"""
    users = load_users()
    for u in users.keys():
        if u.lower() == username.lower():
            return users[u].get("role") == ROLE_ADMIN
    return False


def is_locked_out(username: str) -> Tuple[bool, int]:
    """Check if user is locked out. Returns (is_locked, remaining_minutes)"""
    users = load_users()
    for u in users.keys():
        if u.lower() == username.lower():
            user = users[u]
            if user.get("lockout_until"):
                lockout_time = datetime.fromisoformat(user["lockout_until"])
                if datetime.now() < lockout_time:
                    remaining = int((lockout_time - datetime.now()).total_seconds() / 60) + 1
                    return True, remaining
    return False, 0


def get_failed_attempts(username: str) -> int:
    """Get failed attempts for a user"""
    users = load_users()
    for u in users.keys():
        if u.lower() == username.lower():
            return users[u].get("failed_attempts", 0)
    return 0


def log_access(event_type: str, username: str = ""):
    """Log an access event"""
    ensure_security_dir()
    
    log_entries = []
    if ACCESS_LOG_FILE.exists():
        try:
            with open(ACCESS_LOG_FILE, 'r', encoding='utf-8') as f:
                log_entries = json.load(f)
        except:
            log_entries = []
    
    log_entries.append({
        "timestamp": datetime.now().isoformat(),
        "event": event_type,
        "username": username
    })
    
    # Keep only last 200 entries
    log_entries = log_entries[-200:]
    
    with open(ACCESS_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_entries, f, indent=2, ensure_ascii=False)


def get_access_log(limit: int = 50) -> List[Dict]:
    """Get access log (admin only)"""
    if ACCESS_LOG_FILE.exists():
        try:
            with open(ACCESS_LOG_FILE, 'r', encoding='utf-8') as f:
                entries = json.load(f)
                return entries[-limit:][::-1]
        except:
            return []
    return []


def is_security_enabled() -> bool:
    """Security is always enabled in multi-user mode"""
    return True


# Backward compatibility
def verify_password(password: str) -> bool:
    """Legacy function - not used in multi-user mode"""
    return False


def get_user_display_name(username: str) -> str:
    """Get display name for user"""
    if username.lower() == ADMIN_USERNAME.lower():
        return "管理者"
    return username
