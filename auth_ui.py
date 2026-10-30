import hashlib
import hmac
import secrets
import string
import time

import streamlit as st

from email_service import send_signin_code, send_welcome_email
from firebase_auth import create_account, reset_password, sign_in


CODE_TTL = 5 * 60
CHALLENGE_TTL = 15 * 60
RESEND_COOLDOWN = 60
MAX_CODE_ATTEMPTS = 5
MAX_CODE_SENDS = 3


def _clear_session():
    """Remove the previous user's inputs, notes, and results."""
    for key in list(st.session_state):
        del st.session_state[key]


def _show_background():
    st.markdown(
        """
<style>
.stApp {
    background: #edf4f1 !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

.block-container {
    max-width: 560px !important;
    padding-top: 3rem !important;
    padding-bottom: 3rem !important;
    position: relative;
}

.auth-backdrop {
    position: fixed;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
    z-index: 0;
    background:
        radial-gradient(circle at 15% 15%, #cfe9df 0, transparent 40%),
        radial-gradient(circle at 85% 75%, #d9e4f3 0, transparent 40%),
        #edf4f1;
}

.auth-backdrop .skyline {
    position: absolute;
    bottom: 3%;
    left: 0;
    width: 100%;
    height: 38vh;
    min-height: 200px;
    color: #719b8d;
    opacity: 0.38;
}

.resume-paper {
    position: absolute;
    width: 105px;
    height: 140px;
    padding: 17px;
    box-sizing: border-box;
    border-radius: 10px;
    border: 1px solid #c1d6cd;
    background: rgba(255, 255, 255, 0.95);
    box-shadow: 0 12px 30px rgba(35, 75, 61, 0.09);
    animation: paper-drift 8s ease-in-out infinite alternate;
}

.resume-paper::before {
    content: "";
    display: block;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #a4cdbb;
    margin-bottom: 12px;
}

.resume-paper::after {
    content: "";
    display: block;
    width: 100%;
    height: 5px;
    border-radius: 3px;
    background: #8fb5a6;
    box-shadow:
        0 12px 0 #d0ded8,
        0 24px 0 #d0ded8,
        0 36px 0 #d0ded8;
}

.paper-one {
    top: 12%;
    left: 8%;
    --tilt: -14deg;
}

.paper-two {
    top: 18%;
    right: 9%;
    --tilt: 13deg;
    animation-delay: -3s;
}

.paper-three {
    top: 52%;
    left: 15%;
    --tilt: 9deg;
    animation-delay: -5s;
}

.paper-four {
    top: 57%;
    right: 13%;
    --tilt: -11deg;
    animation-delay: -2s;
}

@keyframes paper-drift {
    from {
        transform: translateY(0) rotate(var(--tilt));
    }
    to {
        transform: translateY(-24px) rotate(var(--tilt));
    }
}

.st-key-auth_shell {
    position: relative;
    z-index: 1;
    background: #ffffff !important;
    border: 1px solid #d9e5df;
    border-radius: 24px;
    padding: 30px;
    box-shadow:
        0 24px 70px rgba(25, 66, 51, 0.13),
        0 4px 14px rgba(25, 66, 51, 0.05);
    color-scheme: light;
}

.auth-brand {
    text-align: center;
    color: #096b65;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.8px;
    margin-bottom: 16px;
}

.auth-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 58px;
    height: 58px;
    margin: 0 auto 16px;
    border-radius: 18px;
    background: #e4f2ec;
    font-size: 27px;
}

.auth-title {
    text-align: center;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: clamp(26px, 4vw, 34px);
    font-weight: 750;
    line-height: 1.2;
    letter-spacing: -0.8px;
    color: #172b27;
    margin: 0 0 12px;
}

.auth-description {
    text-align: center;
    font-family: "Segoe UI", Arial, sans-serif;
    color: #52645e;
    font-size: 15px;
    line-height: 1.6;
    margin-bottom: 20px;
}

.st-key-auth_shell p,
.st-key-auth_shell label,
.st-key-auth_shell [data-testid="stWidgetLabel"] p {
    font-family: "Segoe UI", Arial, sans-serif !important;
    color: #182230 !important;
}

.st-key-auth_shell h2,
.st-key-auth_shell h3 {
    color: #172b27 !important;
}

.st-key-auth_shell [data-testid="stCaptionContainer"] p {
    color: #52645e !important;
    font-size: 12px !important;
}

.st-key-auth_shell [data-testid="stForm"] {
    background: #ffffff !important;
    border: none !important;
    padding: 0 !important;
}

.st-key-auth_shell [data-testid="stTextInput"] input,
.st-key-auth_shell [data-testid="stTextInput"] input:focus {
    background: #ffffff !important;
    color: #182230 !important;
    -webkit-text-fill-color: #182230 !important;
    caret-color: #182230 !important;
    font-size: 16px !important;
}

.st-key-auth_shell [data-baseweb="input"],
.st-key-auth_shell [data-baseweb="base-input"] {
    background: #ffffff !important;
    border-radius: 10px;
}

.st-key-auth_shell [data-baseweb="input"] {
    border-color: #98aaa1 !important;
}

.st-key-auth_shell input::placeholder {
    color: #697970 !important;
    -webkit-text-fill-color: #697970 !important;
    opacity: 1;
}

.st-key-auth_shell input:-webkit-autofill,
.st-key-auth_shell input:-webkit-autofill:hover,
.st-key-auth_shell input:-webkit-autofill:focus {
    -webkit-box-shadow: 0 0 0 1000px #ffffff inset !important;
    -webkit-text-fill-color: #182230 !important;
    caret-color: #182230 !important;
}

.st-key-auth_shell input:autofill {
    background: #ffffff !important;
    color: #182230 !important;
    box-shadow: 0 0 0 1000px #ffffff inset !important;
}

.st-key-auth_shell [data-testid="stTextInput"] button {
    background: #eef4f1 !important;
    color: #23483f !important;
}

.st-key-auth_shell [data-testid="stTextInput"] button svg {
    color: #23483f !important;
}

.st-key-auth_shell [data-testid="stFormSubmitButton"] button {
    background: #096b65 !important;
    color: #ffffff !important;
    border: 1px solid #096b65 !important;
    min-height: 48px;
    border-radius: 11px !important;
}

.st-key-auth_shell [data-testid="stFormSubmitButton"] button p {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 700 !important;
}

.st-key-auth_shell [data-testid="stFormSubmitButton"] button:hover {
    background: #07534e !important;
}

.st-key-auth_shell [data-testid="stButton"] button {
    background: #ffffff !important;
    color: #096b65 !important;
    border: 1px solid #b4cec1 !important;
    border-radius: 11px !important;
    min-height: 44px;
}

.st-key-auth_shell [data-testid="stButton"] button p {
    color: #096b65 !important;
    -webkit-text-fill-color: #096b65 !important;
    font-weight: 600 !important;
}

.st-key-auth_shell [data-testid="stButton"] button:hover {
    background: #edf6f1 !important;
}

.st-key-auth_shell button:disabled {
    opacity: 0.55 !important;
    cursor: not-allowed !important;
}

.st-key-auth_shell [role="tablist"] {
    gap: 16px;
}

.st-key-auth_shell [role="tab"] {
    color: #52645e !important;
    background: transparent !important;
}

.st-key-auth_shell [role="tab"][aria-selected="true"] p {
    color: #096b65 !important;
    font-weight: 700;
}

.st-key-auth_shell [data-baseweb="tab-highlight"] {
    background: #096b65 !important;
}

.st-key-signin_email_code input {
    text-align: center;
    font-size: 24px !important;
    font-weight: 700 !important;
    letter-spacing: 8px;
}

@media (max-width: 900px) {
    .paper-three,
    .paper-four {
        display: none;
    }

    .paper-one {
        left: -35px;
        top: 8%;
    }

    .paper-two {
        right: -35px;
        top: 55%;
    }
}

@media (max-width: 600px) {
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 16px !important;
        padding-right: 16px !important;
    }

    .st-key-auth_shell {
        padding: 22px 18px;
        border-radius: 20px;
    }

    .resume-paper {
        opacity: 0.45;
    }
}

@media (prefers-reduced-motion: reduce) {
    .resume-paper {
        animation: none;
        transform: rotate(var(--tilt));
    }
}
</style>

<div class="auth-backdrop" aria-hidden="true">
<div class="resume-paper paper-one"></div>
<div class="resume-paper paper-two"></div>
<div class="resume-paper paper-three"></div>
<div class="resume-paper paper-four"></div>

<svg class="skyline" viewBox="0 0 1400 250"
     xmlns="http://www.w3.org/2000/svg">
<g fill="currentColor" stroke="currentColor"
   stroke-width="3" stroke-linejoin="round">

<g transform="translate(15,15)">
<path d="M5 140 L30 130 L30 95 L45 95 L45 120 L70 110
L70 75 L86 75 L86 100 L115 88 L115 55 L130 55 L130 80
L165 65 L175 88 L135 108 L135 130 L120 130 L120 115
L88 132 L88 155 L72 155 L72 140 L38 157 L38 175
L20 175 L20 165 L5 172Z"/>
</g>

<g transform="translate(215,15)">
<path d="M20 190 L20 88 L85 42 L150 88 L150 190Z"/>
<path d="M5 87 L85 25 L165 87Z"/>
<rect x="38" y="100" width="15" height="73" fill="#edf4f1"/>
<rect x="72" y="100" width="25" height="90" fill="#edf4f1"/>
<rect x="117" y="100" width="15" height="73" fill="#edf4f1"/>
</g>

<g transform="translate(420,15)">
<circle cx="80" cy="45" r="11"/>
<path d="M68 63 L93 63 L140 80 L136 91 L97 83 L101 160
L116 190 L45 190 L62 160 L66 83 L25 91 L21 80Z"/>
<path d="M28 194 L132 194 L145 215 L15 215Z"/>
</g>

<g transform="translate(610,15)">
<path d="M10 192 L40 192 L40 170 L55 170 L55 148 L70 148
L70 125 L86 125 L86 100 L103 100 L103 125 L119 125
L119 148 L134 148 L134 170 L150 170 L150 192
L180 192 L180 210 L10 210Z"/>
<rect x="82" y="78" width="25" height="23"/>
<path d="M88 119 L101 119 L101 210 L88 210Z" fill="#edf4f1"/>
</g>

<g transform="translate(825,15)">
<path d="M5 202 L40 125 L65 145 L100 65 L145 135 L170 202Z"/>
<path d="M30 192 L50 172 L70 172 L70 157 L87 157 L87 142
L104 142 L104 127 L120 142 L120 160 L140 160
L140 180 L155 192Z" fill="#edf4f1"/>
<path d="M48 185 L145 185 M63 169 L135 169" fill="none"/>
</g>

<g transform="translate(1020,15)">
<path d="M10 100 Q85 55 160 100 L160 190 Q85 224 10 190Z"/>
<path d="M10 123 Q85 85 160 123 M10 151 Q85 117 160 151
M10 178 Q85 148 160 178" fill="none" stroke="#edf4f1"/>
<path d="M35 100 L35 193 M60 91 L60 200 M85 88 L85 203
M110 91 L110 200 M135 100 L135 193"
fill="none" stroke="#edf4f1" stroke-width="8"/>
</g>

<g transform="translate(1210,15)">
<rect x="30" y="130" width="120" height="70"/>
<path d="M57 130 Q38 98 90 70 Q142 98 123 130Z"/>
<path d="M90 70 L90 53"/>
<path d="M77 200 L77 165 Q90 143 103 165 L103 200Z"
fill="#edf4f1"/>
<rect x="12" y="105" width="10" height="95"/>
<rect x="158" y="105" width="10" height="95"/>
<path d="M8 105 L17 88 L26 105Z M154 105 L163 88 L172 105Z"/>
<path d="M0 205 L180 205"/>
</g>

</g>
</svg>
</div>
""",
        unsafe_allow_html=True,
    )


def _password_errors(password):
    errors = []

    if len(password) < 8:
        errors.append("Use at least 8 characters.")

    if not any(char in string.ascii_uppercase for char in password):
        errors.append("Include at least one uppercase letter (A–Z).")

    if not any(char in string.punctuation for char in password):
        errors.append(
            "Include at least one special symbol, such as @, #, or !."
        )

    return errors


def _code_digest(salt, code):
    return hashlib.sha256(
        f"{salt}:{code}".encode("utf-8")
    ).hexdigest()


def _send_pending_code(pending):
    """Send a new code, invalidating any previous code."""
    now = time.time()

    if now >= pending["deadline"]:
        return False

    if pending["attempts"] >= MAX_CODE_ATTEMPTS:
        return False

    if pending["send_count"] >= MAX_CODE_SENDS:
        return False

    if now - pending["last_send_at"] < RESEND_COOLDOWN:
        return False

    pending["send_count"] += 1
    pending["last_send_at"] = now
    pending["code_hash"] = None
    pending["sent"] = False

    code = f"{secrets.randbelow(1_000_000):06d}"
    salt = secrets.token_hex(32)

    pending["salt"] = salt
    pending["code_expires_at"] = min(
        now + CODE_TTL,
        pending["deadline"],
    )

    accepted = send_signin_code(pending["email"], code)

    if accepted:
        pending["code_hash"] = _code_digest(salt, code)
        pending["sent"] = True

    st.session_state["pending_signin"] = pending
    return accepted


def _verify_pending_code(pending, entered_code):
    now = time.time()

    if pending.get("used"):
        return "used"

    if now >= pending["deadline"]:
        return "session_expired"

    if pending["attempts"] >= MAX_CODE_ATTEMPTS:
        return "locked"

    if not pending.get("code_hash"):
        return "not_sent"

    if now >= pending["code_expires_at"]:
        return "expired"

    pending["attempts"] += 1

    valid_format = (
        len(entered_code) == 6
        and entered_code.isascii()
        and entered_code.isdigit()
    )

    if valid_format and hmac.compare_digest(
        _code_digest(pending["salt"], entered_code),
        pending["code_hash"],
    ):
        pending["used"] = True
        return "ok"

    if pending["attempts"] >= MAX_CODE_ATTEMPTS:
        return "locked"

    return "incorrect"


def _show_sign_in():
    with st.form("login_form", clear_on_submit=True):
        email = st.text_input(
            "Email address",
            placeholder="you@example.com",
            key="login_email",
        )

        password = st.text_input(
            "Password",
            placeholder="Enter your password",
            type="password",
            key="login_password",
        )

        submitted = st.form_submit_button(
            "Continue",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not email.strip() or not password:
            st.error("Enter your email address and password.")
        else:
            try:
                with st.spinner("Checking your account..."):
                    response = sign_in(email.strip(), password)

                user_email = response.get("email")
                user_id = response.get("localId")
                token = response.get("idToken")

                if not user_email or not user_id or not token:
                    raise ValueError(
                        "Firebase returned an incomplete sign-in response."
                    )

                lifetime = int(response.get("expiresIn", 3600))

                if lifetime <= 0:
                    raise ValueError(
                        "Your sign-in session expired. Please try again."
                    )

                now = time.time()
                auth_expires_at = now + lifetime

                _clear_session()

                pending = {
                    "email": user_email,
                    "uid": user_id,
                    "auth_expires_at": auth_expires_at,
                    "deadline": min(
                        now + CHALLENGE_TTL,
                        auth_expires_at,
                    ),
                    "attempts": 0,
                    "send_count": 0,
                    "last_send_at": 0,
                    "code_hash": None,
                    "code_expires_at": 0,
                    "salt": "",
                    "sent": False,
                    "used": False,
                }

                st.session_state["pending_signin"] = pending

                with st.spinner("Sending your verification code..."):
                    _send_pending_code(pending)

                st.rerun()

            except ValueError as error:
                st.error(str(error))

    if st.button(
        "Forgot password?",
        key="open_password_reset",
        use_container_width=True,
    ):
        st.session_state["auth_show_reset"] = True
        st.rerun()


def _show_code_verification():
    pending = st.session_state.get("pending_signin")

    if not pending:
        return

    now = time.time()

    st.subheader("Check your email")
    st.write(pending["email"])

    if now >= pending["deadline"]:
        st.warning(
            "This sign-in request expired. "
            "Go back and enter your email and password again."
        )

    elif pending["attempts"] >= MAX_CODE_ATTEMPTS:
        st.error(
            "Too many incorrect attempts. "
            "Go back to sign in and start again."
        )

    else:
        if pending["sent"]:
            st.caption(
                "Enter the latest six-digit code. "
                "Check your spam folder if you don't see the email."
            )
        else:
            st.warning(
                "We couldn't confirm your code email was sent. "
                "Wait one minute, then request another code."
            )

        code_expired = (
            pending["sent"]
            and now >= pending["code_expires_at"]
        )

        if code_expired:
            st.warning("Your code expired. Request a new one.")

        with st.form("verify_code_form", clear_on_submit=True):
            entered_code = st.text_input(
                "Verification code",
                placeholder="000000",
                max_chars=6,
                key="signin_email_code",
            )

            verify_clicked = st.form_submit_button(
                "Verify and sign in",
                type="primary",
                use_container_width=True,
                disabled=not pending["sent"] or code_expired,
            )

        if verify_clicked:
            status = _verify_pending_code(
                pending,
                entered_code.strip(),
            )

            st.session_state["pending_signin"] = pending

            if status == "ok":
                account = {
                    "mode": "signed_in",
                    "email": pending["email"],
                    "uid": pending["uid"],
                    "expires_at": pending["auth_expires_at"],
                    "email_code_verified": True,
                }

                _clear_session()
                st.session_state["auth_account"] = account
                st.rerun()

            elif status == "incorrect":
                remaining = MAX_CODE_ATTEMPTS - pending["attempts"]
                st.error(
                    f"That code isn't correct. "
                    f"You have {remaining} attempts remaining."
                )

            elif status == "locked":
                st.error(
                    "Too many incorrect attempts. "
                    "Go back to sign in and start again."
                )

            elif status == "expired":
                st.error("Your code expired. Request a new one.")

            else:
                st.error(
                    "This code is no longer available. "
                    "Go back to sign in and try again."
                )

        seconds_left = max(
            0,
            int(
                RESEND_COOLDOWN
                - (time.time() - pending["last_send_at"])
                + 0.999
            ),
        )

        st.caption(
            f"Code requests: {pending['send_count']}/{MAX_CODE_SENDS}. "
            "Requesting another code does not reset incorrect attempts."
        )

        if seconds_left:
            st.caption(
                f"Wait about {seconds_left} seconds before resending. "
                "This timer updates when you interact with the page."
            )

        resend_disabled = (
            pending["send_count"] >= MAX_CODE_SENDS
            or pending["attempts"] >= MAX_CODE_ATTEMPTS
        )

        if st.button(
            "Resend code",
            key="resend_signin_code",
            use_container_width=True,
            disabled=resend_disabled,
        ):
            if time.time() >= pending["deadline"]:
                st.error(
                    "This sign-in request expired. "
                    "Go back to sign in and start again."
                )

            elif (
                time.time() - pending["last_send_at"]
                < RESEND_COOLDOWN
            ):
                st.warning(
                    "Please wait one minute between code requests."
                )

            else:
                with st.spinner("Sending a new code..."):
                    _send_pending_code(pending)

                st.rerun()

        if pending["send_count"] >= MAX_CODE_SENDS:
            st.caption(
                "You have reached the code request limit "
                "for this sign-in attempt."
            )

    if st.button(
        "Back to sign in",
        key="cancel_code_verification",
        use_container_width=True,
    ):
        _clear_session()
        st.rerun()


def _show_sign_up():
    with st.form("signup_form", clear_on_submit=True):
        email = st.text_input(
            "Email address",
            placeholder="you@example.com",
            key="signup_email",
        )

        password = st.text_input(
            "Create password",
            placeholder="Choose a strong password",
            type="password",
            help=(
                "Use at least 8 characters, one uppercase letter, "
                "and one special symbol such as @, #, or !."
            ),
            key="signup_password",
        )

        st.caption(
            "At least 8 characters · One uppercase letter · "
            "One special symbol (@, #, !)"
        )

        confirm_password = st.text_input(
            "Confirm password",
            placeholder="Enter your password again",
            type="password",
            key="signup_confirm_password",
        )

        submitted = st.form_submit_button(
            "Create account",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    errors = _password_errors(password)

    if not email.strip():
        errors.append("Enter your email address.")

    if password != confirm_password:
        errors.append("The passwords do not match.")

    if errors:
        for error in errors:
            st.error(error)
        return

    try:
        with st.spinner("Creating your account..."):
            create_account(email.strip(), password)

    except ValueError as error:
        st.error(str(error))
        return

    st.success(
        "Your account is ready. "
        "Open the Sign in tab to continue."
    )

    with st.spinner("Sending your welcome email..."):
        email_accepted = send_welcome_email(email.strip())

    if email_accepted:
        st.caption(
            "Your welcome email is on its way. "
            "Check your inbox or spam folder."
        )
    else:
        st.caption(
            "Your account is ready, but we couldn't confirm "
            "your welcome email was sent."
        )


def _show_reset_password():
    st.subheader("Reset your password")
    st.write(
        "Enter your account email to request reset instructions."
    )

    with st.form("reset_form", clear_on_submit=True):
        email = st.text_input(
            "Email address",
            placeholder="you@example.com",
            key="reset_email",
        )

        submitted = st.form_submit_button(
            "Send reset instructions",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not email.strip():
            st.error("Enter your email address.")
        else:
            try:
                with st.spinner("Sending your request..."):
                    message = reset_password(email.strip())

                st.success(message)

            except ValueError as error:
                st.error(str(error))

    if st.button(
        "Back to sign in",
        key="close_password_reset",
        use_container_width=True,
    ):
        st.session_state["auth_show_reset"] = False
        st.rerun()


def require_login():
    """Require verified sign-in or explicit guest access."""
    account = st.session_state.get("auth_account")
    expired = False

    # Older signed-in sessions must complete the new code step.
    if (
        account
        and account.get("mode") == "signed_in"
        and not account.get("email_code_verified")
    ):
        _clear_session()
        account = None

    if account:
        expires_at = account.get("expires_at")

        if expires_at is not None and time.time() >= expires_at:
            _clear_session()
            expired = True

        else:
            with st.sidebar:
                st.subheader("Your account")

                if account["mode"] == "guest":
                    st.write("Browsing as a guest")
                    button_label = "Back to sign in"
                else:
                    st.write(account["email"])
                    st.caption("Sign-in code verified")
                    button_label = "Sign out"

                st.caption(
                    "Reviews and notes are kept in this session only. "
                    "Download anything you want to keep."
                )

                if st.button(
                    button_label,
                    key="account_sign_out",
                    use_container_width=True,
                ):
                    _clear_session()
                    st.rerun()

            return

    _show_background()

    with st.container(key="auth_shell"):
        st.markdown(
            """
<div class="auth-brand">BUILD AND APPLY THROUGH US</div>
<div class="auth-badge" aria-hidden="true">💼</div>
<div class="auth-title">Your next opportunity<br>starts here.</div>
<div class="auth-description">
A stronger resume. A clearer direction.<br>
Take your next step with confidence.
</div>
""",
            unsafe_allow_html=True,
        )

        if expired:
            st.info("Your session expired. Please sign in again.")

        if st.session_state.get("pending_signin"):
            _show_code_verification()

        elif st.session_state.get("auth_show_reset", False):
            _show_reset_password()

        else:
            login_tab, signup_tab = st.tabs(
                ["Sign in", "Create account"]
            )

            with login_tab:
                _show_sign_in()

            with signup_tab:
                _show_sign_up()

        st.divider()

        if st.button(
            "Continue as guest →",
            key="continue_as_guest",
            use_container_width=True,
        ):
            _clear_session()
            st.session_state["auth_account"] = {
                "mode": "guest",
            }
            st.rerun()

        st.caption(
            "Reviews and notes are available during this session. "
            "Account history is not enabled yet."
        )

    st.stop()