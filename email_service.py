import os
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv(
    Path(__file__).resolve().parent / ".env",
    encoding="utf-8-sig",
)


WELCOME_TEXT = """
Welcome to Build and Apply Through Us!

We're glad you're here.

Your career journey doesn't have to be figured out all at once.
Start with one step: a clearer resume, a new skill, or your next application.

With our app, you can:
- Review your resume and discover practical improvements.
- Explore roles supported by your experience.
- Find learning resources and practice project ideas.
- Search for opportunities through your preferred job platforms.

Review. Learn. Build. Apply.

Every search counts. Your life and skills are valuable.

Your account has been created successfully.
Return to the app and sign in whenever you're ready.

Warm wishes,
Build and Apply Through Us

If you didn't create this account, you can ignore this email.
"""


WELCOME_HTML = """
<html>
<body style="margin:0;padding:24px;background:#edf5f1;
             font-family:Arial,sans-serif;color:#182230;">
<table role="presentation" style="max-width:600px;width:100%;
       margin:auto;background:#ffffff;border-radius:18px;">
<tr>
<td style="padding:32px;">
<p style="color:#096b65;font-size:12px;font-weight:bold;">
BUILD AND APPLY THROUGH US
</p>
<h1 style="font-size:28px;line-height:1.3;color:#173c32;">
Your next opportunity starts here.
</h1>
<p style="font-size:16px;line-height:1.7;">
Welcome! We're glad you're here.
</p>
<p style="font-size:16px;line-height:1.7;">
Your career journey doesn't have to be figured out all at once.
Start with one step: a clearer resume, a new skill, or your next application.
</p>
<div style="background:#eaf5ef;padding:20px;border-radius:12px;">
<strong style="color:#096b65;">Review → Learn → Build → Apply</strong>
<ul style="padding-left:20px;line-height:1.9;">
<li>Get practical feedback on your resume.</li>
<li>Explore roles supported by your experience.</li>
<li>Find learning resources and practice ideas.</li>
<li>Search for opportunities on your preferred job platforms.</li>
</ul>
</div>
<p style="font-size:17px;line-height:1.7;color:#096b65;font-weight:bold;">
Every search counts. Your life and skills are valuable.
</p>
<p style="font-size:16px;line-height:1.7;">
Your account has been created successfully.
Return to the app and sign in whenever you're ready.
</p>
<p style="line-height:1.7;">
Warm wishes,<br><strong>Build and Apply Through Us</strong>
</p>
<hr style="border:0;border-top:1px solid #dce8e1;">
<p style="font-size:12px;color:#526174;line-height:1.6;">
If you didn't create this account, you can ignore this email.
</p>
</td>
</tr>
</table>
</body>
</html>
"""


def _send_email(recipient_email, subject, text_content, html_content):
    """Return True when Brevo accepts the email for sending."""
    api_key = os.getenv("BREVO_API_KEY", "").strip()
    sender_email = os.getenv("WELCOME_SENDER_EMAIL", "").strip()
    recipient_email = (recipient_email or "").strip()

    if not api_key or not sender_email or not recipient_email:
        return False

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": api_key,
                "accept": "application/json",
                "content-type": "application/json",
            },
            json={
                "sender": {
                    "name": "Build and Apply Through Us",
                    "email": sender_email,
                },
                "to": [{"email": recipient_email}],
                "subject": subject,
                "textContent": text_content,
                "htmlContent": html_content,
            },
            timeout=(5, 15),
        )
    except requests.RequestException:
        return False

    # Acceptance does not guarantee inbox delivery.
    return response.status_code == 201


def send_welcome_email(recipient_email):
    """Attempt a welcome email; return False if sending fails."""
    return _send_email(
        recipient_email=recipient_email,
        subject="Welcome! Your next opportunity starts here",
        text_content=WELCOME_TEXT,
        html_content=WELCOME_HTML,
    )


def send_signin_code(recipient_email, code):
    """Send a six-digit sign-in code without logging it."""
    code = str(code).strip()

    if len(code) != 6 or not code.isascii() or not code.isdigit():
        return False

    text_content = (
        "Build and Apply Through Us\n\n"
        f"Your sign-in verification code is: {code}\n\n"
        "This code expires in 5 minutes. "
        "Use it only in the browser where you started signing in.\n\n"
        "Never share this code with anyone.\n\n"
        "If you didn't try to sign in, don't share or enter this code. "
        "Consider resetting your password."
    )

    html_content = f"""
<html>
<body style="margin:0;padding:24px;background:#edf5f1;
             font-family:Arial,sans-serif;color:#182230;">
<table role="presentation" style="max-width:540px;width:100%;
       margin:auto;background:#ffffff;border-radius:18px;">
<tr>
<td style="padding:32px;">
<p style="color:#096b65;font-size:12px;font-weight:bold;">
BUILD AND APPLY THROUGH US
</p>
<h1 style="font-size:26px;color:#173c32;">
Confirm your sign-in
</h1>
<p style="line-height:1.7;">
Enter this code in the browser where you started signing in:
</p>
<div style="background:#e5f4ee;border-radius:12px;padding:22px;
            text-align:center;font-size:34px;font-weight:bold;
            letter-spacing:8px;color:#096b65;">
{code}
</div>
<p style="line-height:1.7;">
This code expires in <strong>5 minutes</strong>.
Never share it with anyone.
</p>
<p style="font-size:13px;line-height:1.6;color:#526174;">
If you didn't try to sign in, don't share or enter this code.
Consider resetting your password.
</p>
</td>
</tr>
</table>
</body>
</html>
"""

    return _send_email(
        recipient_email=recipient_email,
        subject="Your sign-in verification code",
        text_content=text_content,
        html_content=html_content,
    )