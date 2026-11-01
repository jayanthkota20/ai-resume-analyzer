import os
import string
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv(
    Path(__file__).resolve().parent / ".env",
    encoding="utf-8-sig",
)

BASE_URL = "https://identitytoolkit.googleapis.com/v1"


def _request(action, payload):
    api_key = os.getenv("FIREBASE_API_KEY", "").strip()

    if not api_key:
        raise ValueError(
            "FIREBASE_API_KEY is missing. "
            "Check Streamlit Secrets or your local .env file."
        )

    try:
        response = requests.post(
            f"{BASE_URL}/accounts:{action}",
            params={"key": api_key},
            json=payload,
            timeout=(10, 25),
        )
    except requests.RequestException:
        raise ValueError(
            "Could not connect to Firebase. Please try again."
        ) from None

    try:
        data = response.json()
    except ValueError:
        raise ValueError(
            "Firebase returned an unexpected response. "
            "Please try again."
        ) from None

    if not isinstance(data, dict):
        raise ValueError(
            "Firebase returned an unexpected response."
        )

    if not response.ok:
        error_data = data.get("error", {})

        if not isinstance(error_data, dict):
            error_data = {}

        code = str(
            error_data.get("message", "")
        ).split(" : ")[0]

        messages = {
            "EMAIL_EXISTS": (
                "An account already exists with this email. "
                "Please sign in instead."
            ),
            "INVALID_EMAIL": "Please enter a valid email address.",
            "INVALID_LOGIN_CREDENTIALS": "Incorrect email or password.",
            "EMAIL_NOT_FOUND": "Incorrect email or password.",
            "INVALID_PASSWORD": "Incorrect email or password.",
            "WEAK_PASSWORD": (
                "Your password does not meet the requirements."
            ),
            "USER_DISABLED": "This account has been disabled.",
            "OPERATION_NOT_ALLOWED": (
                "Enable Email/Password authentication "
                "in your Firebase project."
            ),
            "TOO_MANY_ATTEMPTS_TRY_LATER": (
                "Too many requests. Please wait before trying again."
            ),
            "API_KEY_INVALID": (
                "The Firebase API key is invalid."
            ),
            "INVALID_ID_TOKEN": (
                "Your verification session expired. "
                "Please sign in again."
            ),
            "TOKEN_EXPIRED": (
                "Your verification session expired. "
                "Please sign in again."
            ),
            "USER_NOT_FOUND": (
                "This account is no longer available."
            ),
        }

        raise ValueError(
            messages.get(
                code,
                "Firebase could not complete the request. "
                "Please check your project settings and try again.",
            )
        )

    return data


def create_account(email, password):
    email = email.strip()

    if not email or not password:
        raise ValueError(
            "Please enter your email and password."
        )

    if len(password) < 8:
        raise ValueError(
            "Your password must have at least 8 characters."
        )

    if not any(
        character in string.ascii_uppercase
        for character in password
    ):
        raise ValueError(
            "Include at least one uppercase letter (A–Z)."
        )

    if not any(
        character in string.punctuation
        for character in password
    ):
        raise ValueError(
            "Include at least one special symbol, "
            "such as @, #, or !."
        )

    return _request(
        "signUp",
        {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        },
    )


def get_account_info(id_token):
    if not id_token:
        raise ValueError(
            "Please sign in again to check your account."
        )

    data = _request(
        "lookup",
        {"idToken": id_token},
    )

    users = data.get("users", [])

    if not users or not isinstance(users[0], dict):
        raise ValueError(
            "Firebase could not find your account."
        )

    return users[0]


def send_verification_email(id_token):
    if not id_token:
        raise ValueError(
            "Please sign in again to request verification."
        )

    _request(
        "sendOobCode",
        {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token,
        },
    )

    return (
        "Verification email requested. "
        "Check your inbox and spam folder."
    )


def sign_in(email, password):
    email = email.strip()

    if not email or not password:
        raise ValueError(
            "Please enter your email and password."
        )

    response = _request(
        "signInWithPassword",
        {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        },
    )

    token = response.get("idToken")

    if not token:
        raise ValueError(
            "Firebase returned an incomplete sign-in response."
        )

    account = get_account_info(token)

    response["emailVerified"] = (
        account.get("emailVerified") is True
    )

    return response


def reset_password(email):
    email = email.strip()

    if not email:
        raise ValueError("Please enter your email address.")

    try:
        _request(
            "sendOobCode",
            {
                "requestType": "PASSWORD_RESET",
                "email": email,
            },
        )

    except ValueError as error:
        if str(error) != "Incorrect email or password.":
            raise

    return (
        "If an account exists for that email, "
        "you will receive password reset instructions."
    )