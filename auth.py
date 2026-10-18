"""University Library Management System: Authentication Module (Lab 7)."""
import re
import uuid
from datetime import datetime, timedelta

MAX_FAILED_ATTEMPTS = 3
SESSION_TIMEOUT_MINUTES = 30
TOKEN_LIFETIME_HOURS = 1
MAX_RESET_EMAILS = 3


class AuthStore:
    """In-memory data store used in place of a real database."""

    def __init__(self):
        self.users = {
            "student@uni.edu": {
                "user_id": "STU-001",
                "password": "ValidPass1",
                "locked": False,
                "attempt_count": 0,
            }
        }
        self.sessions = {}
        self.reset_tokens = {}
        self.reset_email_attempts = {}


auth_store = None


def initialize_store():
    """Create a fresh store. Tests call this to start from a clean state."""
    global auth_store
    auth_store = AuthStore()


initialize_store()


# ---------------------------------------------------------------------------
# Login validation
# ---------------------------------------------------------------------------

def validate_login(email, password):
    """Validate email format and password.

    Returns a dict with the keys: success, user_id, error.
    """
    if not email or not password:
        return {"success": False, "user_id": None,
                "error": "Email and password are required"}
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return {"success": False, "user_id": None,
                "error": "Invalid email format"}
    user = auth_store.users.get(email)
    if user is None:
        return {"success": False, "user_id": None,
                "error": "Invalid credentials"}
    if user["locked"]:
        return {"success": False, "user_id": user["user_id"],
                "error": "Account is locked"}
    if user["password"] != password:
        user["attempt_count"] += 1
        if user["attempt_count"] >= MAX_FAILED_ATTEMPTS:
            user["locked"] = True
        return {"success": False, "user_id": user["user_id"],
                "error": "Invalid credentials"}
    user["attempt_count"] = 0
    return {"success": True, "user_id": user["user_id"], "error": None}


# ---------------------------------------------------------------------------
# Account lockout
# ---------------------------------------------------------------------------

def check_lockout(email, attempt_count):
    """Return True if a login attempt is allowed, False if it is blocked."""
    user = auth_store.users.get(email)
    if user is not None and user["locked"]:
        return False
    if attempt_count >= MAX_FAILED_ATTEMPTS:
        if user is not None:
            user["locked"] = True
        return False
    return True


def lock_account(email):
    """Lock a user account."""
    user = auth_store.users.get(email)
    if user is not None:
        user["locked"] = True


def unlock_account(email):
    """Unlock a user account and clear its failed attempts."""
    user = auth_store.users.get(email)
    if user is not None:
        user["locked"] = False
        user["attempt_count"] = 0


def is_locked(email):
    """Return True if the account exists and is locked."""
    user = auth_store.users.get(email)
    if user is None:
        return False
    return user["locked"]


def reset_attempt_count(email):
    """Clear the failed login attempts of an account."""
    user = auth_store.users.get(email)
    if user is not None:
        user["attempt_count"] = 0


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

def create_session(user_id, idle_minutes=0):
    """Create a session whose last activity was idle_minutes ago."""
    now = datetime.now()
    auth_store.sessions[user_id] = {
        "created_at": now,
        "last_activity": now - timedelta(minutes=idle_minutes),
    }


def destroy_session(user_id):
    """Remove a session if it exists."""
    if user_id in auth_store.sessions:
        del auth_store.sessions[user_id]


def is_session_valid(user_id):
    """Return True if the session exists and was active in the last 30 minutes."""
    session = auth_store.sessions.get(user_id)
    if session is None:
        return False
    idle_time = datetime.now() - session["last_activity"]
    if idle_time >= timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        destroy_session(user_id)
        return False
    return True


def update_session_activity(user_id):
    """Set the last activity of an existing session to now."""
    session = auth_store.sessions.get(user_id)
    if session is not None:
        session["last_activity"] = datetime.now()


def handle_session(user_id, idle_minutes=0):
    """Create a session if none exists, otherwise validate and refresh it.

    Returns True if the user has a usable session after the call.
    """
    if user_id not in auth_store.sessions:
        create_session(user_id, idle_minutes)
        return True
    if not is_session_valid(user_id):
        return False
    update_session_activity(user_id)
    return True


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------

def generate_reset_token(email, hours_ago=0):
    """Create a reset token. hours_ago lets tests create an old token."""
    token = str(uuid.uuid4())
    auth_store.reset_tokens[token] = {
        "email": email,
        "created_at": datetime.now() - timedelta(hours=hours_ago),
        "used": False,
    }
    return token


def mark_token_used(token):
    """Mark a reset token as used."""
    reset = auth_store.reset_tokens.get(token)
    if reset is not None:
        reset["used"] = True


def verify_reset_token(token):
    """Return True if the token exists, is under one hour old and is unused."""
    reset = auth_store.reset_tokens.get(token)
    if reset is None:
        return False
    age = datetime.now() - reset["created_at"]
    if age > timedelta(hours=TOKEN_LIFETIME_HOURS):
        return False
    if reset["used"]:
        return False
    return True


def _deliver_email(email, token):
    """Simulated SMTP delivery. Tests patch this function to force failures."""
    return True


def send_reset_email(email):
    """Send a password reset email to a registered user."""
    if email not in auth_store.users:
        return {"sent": False, "error": "Email address not found"}
    attempts = auth_store.reset_email_attempts.get(email, 0)
    if attempts >= MAX_RESET_EMAILS:
        return {"sent": False, "error": "Rate limit exceeded"}
    try:
        token = generate_reset_token(email)
    except Exception as exc:
        return {"sent": False, "error": f"Token generation failed: {exc}"}
    auth_store.reset_email_attempts[email] = attempts + 1
    try:
        _deliver_email(email, token)
    except ConnectionError as exc:
        return {"sent": False, "error": f"SMTP error: {exc}"}
    return {"sent": True, "token": token, "error": None}
