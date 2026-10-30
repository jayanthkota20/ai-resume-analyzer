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
            "FIREBASE_API_KEY is missing. Check your .env file "
            "and restart Streamlit."
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
            "Could not connect to Firebase. "
            "Check your internet connection and try again."
        ) from None

    try:
        data = response.json()
    except ValueError:
        raise ValueError(
            "Firebase returned an unexpected response. Please try again."
        ) from None

    if not response.ok:
        error = data.get("error", {})
        code = str(error.get("message", "")).split(" : ")[0]

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
                "Your password does not meet the project's requirements."
            ),
            "USER_DISABLED": "This account has been disabled.",
            "OPERATION_NOT_ALLOWED": (
                "Enable Email/Password authentication "
                "in your Firebase project."
            ),
            "TOO_MANY_ATTEMPTS_TRY_LATER": (
                "Too many attempts. Please wait and try again."
            ),
            "API_KEY_INVALID": (
                "The Firebase API key is invalid. Check your .env file."
            ),
        }

        raise ValueError(
            messages.get(
                code,
                "Firebase could not complete the request. "
                "Check your project settings and try again.",
            )
        )

    return data


def create_account(email, password):
    email = email.strip()

    if not email or not password:
        raise ValueError("Please enter your email and password.")

    if len(password) < 8:
        raise ValueError("Your password must have at least 8 characters.")

    if not any(character.isupper() for character in password):
        raise ValueError(
        "Your password must include at least one uppercase letter."
    )

    if not any(character in string.punctuation for character in password):
        raise ValueError(
        "Your password must include at least one special symbol, "
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


def sign_in(email, password):
    email = email.strip()

    if not email or not password:
        raise ValueError("Please enter your email and password.")

    return _request(
        "signInWithPassword",
        {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        },
    )


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
        # Keep the response the same for an unregistered email.
        if str(error) != "Incorrect email or password.":
            raise

    return (
        "If an account exists for that email, "
        "you will receive password reset instructions."
    )