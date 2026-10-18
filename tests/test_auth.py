"""Existing LMS authentication tests from Labs 3 to 6."""
import auth


# TC-001: valid login (REQ-01)
def test_valid_login_with_correct_credentials():
    result = auth.validate_login("student@uni.edu", "ValidPass1")
    assert result["success"] is True
    assert result["user_id"] == "STU-001"


# TC-002: lockout after 3 failed attempts (REQ-02)
def test_account_lockout_after_3_failed_attempts():
    assert auth.check_lockout("student@uni.edu", attempt_count=3) is False
    assert auth.is_locked("student@uni.edu") is True


# TC-003: password reset email for a registered user (REQ-03)
def test_password_reset_email_send():
    result = auth.send_reset_email("student@uni.edu")
    assert result["sent"] is True


# TC-004: session expires after 30 minutes of inactivity (REQ-04)
def test_session_expires_after_30_min():
    auth.create_session("student@uni.edu", idle_minutes=31)
    assert auth.is_session_valid("student@uni.edu") is False


# TC-005: empty email or password is rejected (REQ-01)
def test_login_rejects_empty_password():
    result = auth.validate_login("student@uni.edu", "")
    assert result["success"] is False
    assert result["error"] == "Email and password are required"


# TC-006: malformed email is rejected (REQ-01)
def test_login_rejects_invalid_email_format():
    result = auth.validate_login("student-at-uni.edu", "ValidPass1")
    assert result["success"] is False
    assert result["error"] == "Invalid email format"


# TC-007: wrong password is rejected (REQ-01)
def test_login_rejects_wrong_password():
    result = auth.validate_login("student@uni.edu", "WrongPass9")
    assert result["success"] is False
    assert result["error"] == "Invalid credentials"
