"""New tests added in Lab 7 to cover the gaps found in the baseline report."""
import auth
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Experiment C: guided tests
# ---------------------------------------------------------------------------

# --- verify_reset_token ----------------------------------------------------

# Target: verify_reset_token() valid token returns True
def test_verify_reset_token_accepts_valid_token():
    token = auth.generate_reset_token("student@uni.edu")
    assert auth.verify_reset_token(token) is True


# Target: verify_reset_token() unknown token returns False
def test_verify_reset_token_rejects_unknown_token():
    assert auth.verify_reset_token("no-such-token") is False


# Target: verify_reset_token() expired token returns False
def test_verify_reset_token_rejects_expired_token():
    token = auth.generate_reset_token("student@uni.edu", hours_ago=2)
    assert auth.verify_reset_token(token) is False


# Target: verify_reset_token() used token returns False
def test_verify_reset_token_rejects_used_token():
    token = auth.generate_reset_token("student@uni.edu")
    auth.mark_token_used(token)
    assert auth.verify_reset_token(token) is False


# --- check_lockout ---------------------------------------------------------

# Target: check_lockout() account already locked returns False
def test_check_lockout_blocks_already_locked_account():
    auth.lock_account("student@uni.edu")
    assert auth.check_lockout("student@uni.edu", attempt_count=0) is False


# Target: check_lockout() attempt_count below 3 returns True
def test_check_lockout_allows_two_failed_attempts():
    assert auth.check_lockout("student@uni.edu", attempt_count=2) is True
    assert auth.is_locked("student@uni.edu") is False


# Target: check_lockout() unknown account with 3 attempts (user is None branch)
def test_check_lockout_blocks_unknown_account_at_three_attempts():
    assert auth.check_lockout("nobody@uni.edu", attempt_count=3) is False


# --- validate_login --------------------------------------------------------

# Target: validate_login() email not registered
def test_validate_login_rejects_unregistered_email():
    result = auth.validate_login("ghost@uni.edu", "ValidPass1")
    assert result["success"] is False
    assert result["user_id"] is None
    assert result["error"] == "Invalid credentials"


# Target: validate_login() locked account is refused
def test_validate_login_refuses_locked_account():
    auth.lock_account("student@uni.edu")
    result = auth.validate_login("student@uni.edu", "ValidPass1")
    assert result["success"] is False
    assert result["error"] == "Account is locked"


# Target: validate_login() third wrong password locks the account
def test_validate_login_locks_account_after_three_wrong_passwords():
    for _ in range(3):
        auth.validate_login("student@uni.edu", "WrongPass9")
    assert auth.is_locked("student@uni.edu") is True


# ---------------------------------------------------------------------------
# Experiment D, Step 1: session tests (user id STU001)
# ---------------------------------------------------------------------------

# Target: is_session_valid() no session exists returns False
def test_is_session_valid_returns_false_when_no_session():
    assert auth.is_session_valid("STU001") is False


# Target: is_session_valid() idle 29 minutes is still valid (below timeout)
def test_is_session_valid_accepts_session_idle_29_minutes():
    auth.create_session("STU001", idle_minutes=29)
    assert auth.is_session_valid("STU001") is True


# Target: is_session_valid() idle exactly 30 minutes is expired (boundary, >= check)
def test_is_session_valid_rejects_session_idle_exactly_30_minutes():
    auth.create_session("STU001", idle_minutes=30)
    assert auth.is_session_valid("STU001") is False
    assert "STU001" not in auth.auth_store.sessions  # expired session is destroyed


# Target: handle_session() no session yet creates one and returns True
def test_handle_session_creates_session_when_none_exists():
    assert auth.handle_session("STU001") is True
    assert auth.is_session_valid("STU001") is True


# Target: handle_session() session idle 45 minutes returns False
def test_handle_session_rejects_expired_session():
    auth.create_session("STU001", idle_minutes=45)
    assert auth.handle_session("STU001") is False


# Target: handle_session() valid session is refreshed (update_session_activity)
def test_handle_session_refreshes_valid_session():
    auth.create_session("STU001", idle_minutes=25)
    before = auth.auth_store.sessions["STU001"]["last_activity"]
    assert auth.handle_session("STU001") is True
    after = auth.auth_store.sessions["STU001"]["last_activity"]
    assert after > before


# ---------------------------------------------------------------------------
# Experiment D, Step 2: password reset email tests
# ---------------------------------------------------------------------------

# Target: send_reset_email() email not registered
def test_send_reset_email_rejects_unregistered_email():
    result = auth.send_reset_email("ghost@uni.edu")
    assert result["sent"] is False
    assert result["error"] == "Email address not found"


# Target: send_reset_email() rate limit reached on the fourth request
def test_send_reset_email_enforces_rate_limit():
    for _ in range(3):
        assert auth.send_reset_email("student@uni.edu")["sent"] is True
    result = auth.send_reset_email("student@uni.edu")
    assert result["sent"] is False
    assert result["error"] == "Rate limit exceeded"


# Target: send_reset_email() token generation raises an exception
def test_send_reset_email_reports_token_generation_failure():
    with patch("auth.generate_reset_token", side_effect=RuntimeError("boom")):
        result = auth.send_reset_email("student@uni.edu")
    assert result["sent"] is False
    assert result["error"] == "Token generation failed: boom"


# Target: send_reset_email() SMTP delivery raises ConnectionError
def test_send_reset_email_reports_smtp_failure():
    with patch("auth._deliver_email", side_effect=ConnectionError("server down")):
        result = auth.send_reset_email("student@uni.edu")
    assert result["sent"] is False
    assert result["error"] == "SMTP error: server down"
