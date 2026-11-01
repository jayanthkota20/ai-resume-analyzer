import os
import time
from pathlib import Path
from urllib.parse import quote

import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv(
    Path(__file__).resolve().parent / ".env",
    encoding="utf-8-sig",
)


PROFILE_FIELDS = [
    ("full_name", "Full name", 200),
    ("phone", "Phone number", 100),
    ("address", "Street address", 500),
    ("city", "City", 200),
    ("region", "State or region", 200),
    ("postal_code", "Postal code", 50),
    ("country", "Country", 200),
    ("linkedin", "LinkedIn URL", 500),
    ("portfolio", "Portfolio or GitHub URL", 500),
    ("education", "Education", 10000),
    ("experience", "Work experience", 10000),
    ("skills", "Skills", 10000),
    ("projects", "Projects", 10000),
    ("courses", "Courses and certifications", 10000),
    ("preferences", "Job preferences", 10000),
]

FIELD_LIMITS = {
    name: maximum
    for name, _, maximum in PROFILE_FIELDS
}

LONG_FIELDS = {
    "education",
    "experience",
    "skills",
    "projects",
    "courses",
    "preferences",
}


def _account():
    account = st.session_state.get("auth_account", {})

    if (
        account.get("mode") != "signed_in"
        or account.get("email_verified") is not True
        or not account.get("uid")
        or not account.get("id_token")
    ):
        raise ValueError(
            "Please sign out and sign in again "
            "to access your saved profile."
        )

    if time.time() >= account.get("expires_at", 0):
        raise ValueError(
            "Your session expired. Please sign in again."
        )

    return account


def _document_url():
    account = _account()
    project_id = os.getenv(
        "FIREBASE_PROJECT_ID", ""
    ).strip()

    if not project_id:
        raise ValueError(
            "FIREBASE_PROJECT_ID is missing. "
            "Add it to Streamlit Secrets or your local .env."
        )

    return (
        "https://firestore.googleapis.com/v1/projects/"
        f"{quote(project_id, safe='')}"
        "/databases/(default)/documents/applicant_profiles/"
        f"{quote(account['uid'], safe='')}"
    )


def _request(method, payload=None, params=None):
    account = _account()
    url = _document_url()

    try:
        response = requests.request(
            method,
            url,
            headers={
                "Authorization": (
                    f"Bearer {account['id_token']}"
                ),
                "Content-Type": "application/json",
            },
            json=payload,
            params=params,
            timeout=(5, 20),
        )
    except requests.RequestException:
        raise ValueError(
            "Could not connect to your saved profile. "
            "Your edits have not been confirmed saved."
        ) from None

    try:
        data = response.json() if response.content else {}
    except ValueError:
        raise ValueError(
            "The profile service returned an unexpected response."
        ) from None

    if not isinstance(data, dict):
        raise ValueError(
            "The profile service returned an unexpected response."
        )

    if response.status_code == 404 and method == "GET":
        error_message = str(
            data.get("error", {}).get("message", "")
        ).lower()

        if "database" in error_message:
            raise ValueError(
                "The Firestore database was not found. "
                "Check the project ID and create the "
                "default database in that project."
            )

        # An account without a saved profile starts empty.
        return None

    if not response.ok:
        if response.status_code == 401:
            message = (
                "Your profile session expired. "
                "Please sign out and sign in again."
            )
        elif response.status_code == 403:
            message = (
                "Profile access was denied. "
                "Check your Firestore rules, project ID, "
                "and verified account."
            )
        elif response.status_code in (409, 412):
            message = (
                "Your saved profile changed in another session. "
                "Reload the saved profile before saving again."
            )
        elif response.status_code == 429:
            message = (
                "The profile service received too many requests. "
                "Please wait before trying again."
            )
        else:
            message = (
                f"The profile request failed "
                f"(HTTP {response.status_code}). "
                "Please try again."
            )

        raise ValueError(message)

    return data


def _load_profile():
    document = _request("GET")

    if document is None:
        return {}, None

    values = document.get("fields", {})

    profile = {
        name: values.get(name, {}).get("stringValue", "")
        for name, _, _ in PROFILE_FIELDS
    }

    return profile, document.get("updateTime")


def _save_profile(profile, version):
    cleaned = {}

    for name, _, maximum in PROFILE_FIELDS:
        value = profile.get(name, "").strip()

        if len(value) > maximum:
            raise ValueError(
                f"{name.replace('_', ' ').title()} "
                f"must be at most {maximum:,} characters."
            )

        cleaned[name] = value

    # Prevent silently overwriting a newer saved version.
    params = (
        {"currentDocument.updateTime": version}
        if version
        else {"currentDocument.exists": "false"}
    )

    document = _request(
        "PATCH",
        payload={
            "fields": {
                name: {"stringValue": value}
                for name, value in cleaned.items()
            }
        },
        params=params,
    )

    return cleaned, document.get("updateTime")


def _clear_profile_widgets():
    for name, _, _ in PROFILE_FIELDS:
        st.session_state.pop(f"profile_field_{name}", None)


def _profile_text(profile, email):
    lines = [
        "BUILD AND APPLY THROUGH US",
        "Applicant profile",
        "",
        f"Account email: {email}",
        "",
    ]

    for name, label, _ in PROFILE_FIELDS:
        lines.extend([
            label,
            profile.get(name, "") or "Not provided",
            "",
        ])

    return "\n".join(lines)


def show_profile():
    account = st.session_state.get("auth_account", {})

    with st.expander("My Profile", expanded=False):
        if account.get("mode") != "signed_in":
            st.info(
                "Sign in to save a profile and load it "
                "again on your next visit."
            )
            return

        st.caption(
            "Save your details once and update them when needed. "
            "Changes are stored when you click Save profile."
        )

        st.caption(
            "These details are separate from your resume review. "
            "Saving them does not submit a job application."
        )

        if st.session_state.get(
            "profile_loaded_uid"
        ) != account.get("uid"):
            try:
                with st.spinner("Loading your profile..."):
                    profile, version = _load_profile()

                _clear_profile_widgets()

                st.session_state["saved_profile"] = profile
                st.session_state["profile_version"] = version
                st.session_state[
                    "profile_loaded_uid"
                ] = account["uid"]

            except ValueError as error:
                st.error(str(error))
                return

        notice = st.session_state.pop(
            "profile_notice", None
        )

        if notice:
            st.success(notice)

        saved = st.session_state.get(
            "saved_profile", {}
        )

        st.write(f"Account email: {account['email']}")

        with st.form("applicant_profile_form"):
            draft = {}

            for name, label, maximum in PROFILE_FIELDS:
                widget_key = f"profile_field_{name}"

                if name in LONG_FIELDS:
                    draft[name] = st.text_area(
                        label,
                        value=saved.get(name, ""),
                        max_chars=maximum,
                        height=110,
                        key=widget_key,
                    )
                else:
                    draft[name] = st.text_input(
                        label,
                        value=saved.get(name, ""),
                        max_chars=maximum,
                        key=widget_key,
                    )

            save_clicked = st.form_submit_button(
                "Save profile",
                type="primary",
                use_container_width=True,
            )

        if save_clicked:
            try:
                with st.spinner("Saving your profile..."):
                    profile, version = _save_profile(
                        draft,
                        st.session_state.get(
                            "profile_version"
                        ),
                    )

                st.session_state[
                    "saved_profile"
                ] = profile

                st.session_state[
                    "profile_version"
                ] = version

                st.session_state["profile_notice"] = (
                    "Your profile has been saved."
                )

                st.rerun()

            except ValueError as error:
                st.error(str(error))

        if st.button(
            "Reload saved profile",
            key="reload_saved_profile",
            use_container_width=True,
        ):
            try:
                with st.spinner("Reloading your profile..."):
                    profile, version = _load_profile()

                _clear_profile_widgets()

                st.session_state[
                    "saved_profile"
                ] = profile

                st.session_state[
                    "profile_version"
                ] = version

                st.session_state["profile_notice"] = (
                    "Saved profile loaded. "
                    "Unsaved edits were discarded."
                )

                st.rerun()

            except ValueError as error:
                st.error(str(error))

        st.download_button(
            "Download saved profile",
            data=_profile_text(
                st.session_state.get(
                    "saved_profile", {}
                ),
                account["email"],
            ),
            file_name="applicant_profile.txt",
            mime="text/plain",
            key="download_saved_profile",
            use_container_width=True,
        )

        st.divider()

        confirm_delete = st.checkbox(
            "I want to delete my saved profile",
            key="confirm_profile_delete",
        )

        if st.button(
            "Delete saved profile",
            key="delete_saved_profile",
            disabled=not confirm_delete,
            use_container_width=True,
        ):
            try:
                version = st.session_state.get(
                    "profile_version"
                )

                params = (
                    {"currentDocument.updateTime": version}
                    if version
                    else None
                )

                with st.spinner(
                    "Deleting your saved profile..."
                ):
                    _request("DELETE", params=params)

                _clear_profile_widgets()

                st.session_state[
                    "saved_profile"
                ] = {}

                st.session_state[
                    "profile_version"
                ] = None

                st.session_state.pop(
                    "confirm_profile_delete", None
                )

                st.session_state["profile_notice"] = (
                    "Your saved profile was deleted. "
                    "Your sign-in account is unchanged."
                )

                st.rerun()

            except ValueError as error:
                st.error(str(error))