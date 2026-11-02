import hashlib
import json
import os
import re
from html import escape
from time import perf_counter
from urllib.parse import urlencode
import base64
from pathlib import Path

import streamlit as st

from ai_analyzer import analyze_resume
from auth_ui import require_login
from profile_ui import show_profile
from resume_parser import extract_resume_text


BRAND = "BUILD AND APPLY THROUGH US"

st.set_page_config(
    page_title=BRAND,
    page_icon="💼",
    layout="wide",
)


# =========================================================
# LEARNING RESOURCES
# =========================================================

LEARNING_RESOURCES = {
    "Python": {
        "pattern": r"\bpython\b",
        "focus": "Functions, collections, files, and error handling.",
        "project": "Build a CSV expense tracker with category summaries.",
        "websites": {
            "Python documentation": "https://docs.python.org/3/tutorial/",
            "W3Schools": "https://www.w3schools.com/python/",
            "freeCodeCamp": "https://www.freecodecamp.org/learn/",
            "Kaggle Learn": "https://www.kaggle.com/learn/python",
        },
    },
    "SQL": {
        "pattern": r"\bsql\b|\bdatabase\b|\bjoins?\b",
        "focus": "Filtering, joins, grouping, and database design.",
        "project": "Create an orders database and answer five business questions.",
        "websites": {
            "SQLBolt": "https://sqlbolt.com/",
            "W3Schools": "https://www.w3schools.com/sql/",
            "Kaggle Learn": "https://www.kaggle.com/learn/intro-to-sql",
            "PostgreSQL": "https://www.postgresql.org/docs/current/tutorial.html",
        },
    },
    "Data Analysis": {
        "pattern": r"data analy|pandas|excel|tableau|power bi",
        "focus": "Clean data, explore patterns, and explain findings.",
        "project": "Clean a public dataset and create a dashboard with findings.",
        "websites": {
            "Kaggle Learn": "https://www.kaggle.com/learn",
            "Microsoft Learn": "https://learn.microsoft.com/en-us/training/",
            "freeCodeCamp": "https://www.freecodecamp.org/learn/",
            "pandas": "https://pandas.pydata.org/docs/getting_started/",
        },
    },
    "Machine Learning": {
        "pattern": r"machine learning|\bml\b|scikit|classification|regression",
        "focus": "Train/test splits, baseline models, and evaluation.",
        "project": "Compare two classifiers and explain their evaluation results.",
        "websites": {
            "Google ML": "https://developers.google.com/machine-learning",
            "Kaggle Learn": "https://www.kaggle.com/learn/intro-to-machine-learning",
            "scikit-learn": "https://scikit-learn.org/stable/tutorial/index.html",
            "fast.ai": "https://course.fast.ai/",
        },
    },
    "Cybersecurity": {
        "pattern": r"cyber|security|\bsoc\b|siem|network defense",
        "focus": "Networking, Linux, log analysis, and defensive security.",
        "project": "Analyze sample authentication logs and document suspicious events.",
        "websites": {
            "PortSwigger Academy": "https://portswigger.net/web-security",
            "TryHackMe": "https://tryhackme.com/",
            "Cisco Skills for All": "https://skillsforall.com/",
            "OverTheWire": "https://overthewire.org/wargames/",
        },
    },
    "Frontend Development": {
        "pattern": r"front.?end|html|css|javascript|react|typescript",
        "focus": "Accessible HTML, responsive CSS, JavaScript, and UI state.",
        "project": "Build a responsive job tracker with filtering and local storage.",
        "websites": {
            "MDN": "https://developer.mozilla.org/en-US/docs/Learn_web_development",
            "freeCodeCamp": "https://www.freecodecamp.org/learn/",
            "The Odin Project": "https://www.theodinproject.com/",
            "W3Schools": "https://www.w3schools.com/",
        },
    },
    "Backend Development": {
        "pattern": r"back.?end|\brest\b|\bapi\b|django|flask|fastapi|node",
        "focus": "APIs, validation, databases, authentication, and testing.",
        "project": "Build a task API with authenticated access and input validation.",
        "websites": {
            "FastAPI": "https://fastapi.tiangolo.com/tutorial/",
            "Django": "https://docs.djangoproject.com/en/stable/intro/",
            "MDN": (
                "https://developer.mozilla.org/en-US/docs/"
                "Learn_web_development/Extensions/Server-side"
            ),
            "freeCodeCamp": "https://www.freecodecamp.org/learn/",
        },
    },
    "Full Stack Development": {
        "pattern": r"full.?stack",
        "focus": "Connect a frontend, backend, and database.",
        "project": "Build a job tracker with accounts and saved applications.",
        "websites": {
            "Full Stack Open": "https://fullstackopen.com/en/",
            "The Odin Project": "https://www.theodinproject.com/",
            "freeCodeCamp": "https://www.freecodecamp.org/learn/",
            "MDN": "https://developer.mozilla.org/en-US/docs/Learn_web_development",
        },
    },
    "Generative AI": {
        "pattern": r"generative|\bgen.?ai\b|\bllm\b|\brag\b|prompt|embedding",
        "focus": "LLMs, retrieval, evaluation, and evidence-based responses.",
        "project": "Build a document assistant that answers with source references.",
        "websites": {
            "Hugging Face": "https://huggingface.co/learn",
            "Google AI": "https://ai.google.dev/gemini-api/docs",
            "Microsoft Learn": "https://learn.microsoft.com/en-us/training/",
            "DeepLearning.AI": "https://www.deeplearning.ai/short-courses/",
        },
    },
    "AWS": {
        "pattern": r"\baws\b|amazon web|ec2|\bs3\b|lambda",
        "focus": "IAM, storage, compute, monitoring, and cost awareness.",
        "project": "Design a web app architecture and document IAM permissions.",
        "websites": {
            "AWS Skill Builder": "https://skillbuilder.aws/",
            "AWS Workshops": "https://workshops.aws/",
            "AWS documentation": "https://docs.aws.amazon.com/",
            "freeCodeCamp": "https://www.freecodecamp.org/learn/",
        },
    },
    "Cloud Computing": {
        "pattern": r"\bcloud\b|azure|gcp|google cloud",
        "focus": "Cloud services, networking, identity, and deployment.",
        "project": "Deploy a small app and document its architecture and costs.",
        "websites": {
            "Microsoft Learn": "https://learn.microsoft.com/en-us/training/",
            "Google Cloud Skills Boost": "https://www.cloudskillsboost.google/",
            "AWS Skill Builder": "https://skillbuilder.aws/",
            "Google Cloud documentation": "https://cloud.google.com/docs",
        },
    },
    "DevOps": {
        "pattern": r"devops|docker|kubernetes|ci/cd|terraform|linux",
        "focus": "Containers, automation, CI pipelines, and deployment.",
        "project": "Containerize an app and create a pipeline that runs its checks.",
        "websites": {
            "Docker": "https://docs.docker.com/get-started/",
            "Kubernetes": "https://kubernetes.io/docs/tutorials/",
            "GitHub Actions": "https://docs.github.com/en/actions",
            "Microsoft Learn": "https://learn.microsoft.com/en-us/training/",
        },
    },
    "Git and GitHub": {
        "pattern": r"\bgit\b|\bgithub\b|version control",
        "focus": "Commits, branches, pull requests, and resolving conflicts.",
        "project": "Publish a project and complete a feature using a branch.",
        "websites": {
            "GitHub Skills": "https://skills.github.com/",
            "Git book": "https://git-scm.com/book/en/v2",
            "Learn Git Branching": "https://learngitbranching.js.org/",
            "Atlassian": "https://www.atlassian.com/git/tutorials",
        },
    },
}

US_STATES = [
    "Any location", "Remote",
    "Alabama", "Alaska", "Arizona", "Arkansas", "California",
    "Colorado", "Connecticut", "Delaware", "District of Columbia",
    "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana",
    "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
    "New Jersey", "New Mexico", "New York", "North Carolina",
    "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee",
    "Texas", "Utah", "Vermont", "Virginia", "Washington",
    "West Virginia", "Wisconsin", "Wyoming",
]


# =========================================================
# ONE CONSOLIDATED STYLESHEET
# =========================================================

APP_CSS = """
<style>
.stApp {
    background:
        radial-gradient(ellipse at 0% 0%, #edf7f2, transparent 42%),
        radial-gradient(ellipse at 100% 10%, #eef3fb, transparent 42%),
        #ffffff;
    color: #182230;
    font-family: "Segoe UI", Arial, sans-serif;
}

.block-container {
    max-width: 1150px;
    padding-top: 9rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4,
[data-testid="stWidgetLabel"],
input, textarea, button {
    font-family: "Segoe UI", Arial, sans-serif !important;
}

h1, h2, h3, h4 {
    color: #182230 !important;
}

[data-testid="stWidgetLabel"] p,
[data-testid="stMarkdownContainer"] p {
    color: #182230;
    line-height: 1.65;
}

[data-testid="stCaptionContainer"] p {
    color: #526174 !important;
}

[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="textarea"],
[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: #182230 !important;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    color: #182230 !important;
    -webkit-text-fill-color: #182230 !important;
    font-size: 16px !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #667085 !important;
    -webkit-text-fill-color: #667085 !important;
    opacity: 1;
}

[data-testid="stFileUploaderDropzone"] {
    background: #edf6f2 !important;
    border: 2px dashed #80aaa0 !important;
    border-radius: 12px;
}

[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] small {
    color: #253f38 !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background: #096b65 !important;
    border: 1px solid #096b65 !important;
}

[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploaderDropzone"] button p {
    color: #ffffff !important;
}

button[kind="primary"] {
    background: #096b65 !important;
    border: none !important;
    min-height: 46px;
    border-radius: 10px;
}

button[kind="primary"] p {
    color: #ffffff !important;
    font-weight: 600;
}

button[kind="primary"]:disabled {
    background: #dce6e2 !important;
}

button[kind="primary"]:disabled p {
    color: #526174 !important;
}

/* Brand: small, fixed, transparent, and shown once. */
.app-brand {
    position: fixed;
    top: 68px;
    left: 28px;
    z-index: 900;

    display: flex;
    align-items: center;
    gap: 9px;
    max-width: calc(100vw - 460px);

    color: #096b65;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: .7px;

    background: transparent;
    border: none;
    box-shadow: none;
}

.app-brand-icon {
    font-size: 22px;
    line-height: 1;
}

/* Account buttons stay visible while scrolling. */
.st-key-account_header {
    position: fixed;
    top: 58px;
    right: 24px;
    z-index: 900;
    width: 390px;
    max-width: calc(100vw - 32px);
    padding: 8px 10px;
    background: rgba(255, 255, 255, .96);
    border: 1px solid #e0e8e4;
    border-radius: 12px;
    box-shadow: 0 4px 14px rgba(24, 34, 48, .05);
}

.st-key-account_header [data-testid="stHorizontalBlock"] {
    align-items: center;
    gap: 8px;
}

.st-key-account_header button {
    min-height: 34px;
    padding: 5px 8px;
    border: 1px solid #d2e1da !important;
    background: #ffffff !important;
    border-radius: 8px;
}

.st-key-account_header button p {
    font-size: 13px;
    font-weight: 600;
    color: #096b65 !important;
}

.provider-name {
    font-size: 14px;
    font-weight: 600;
    color: #096b65;
    padding: 5px 0;
}

.st-key-notes_header {
    position: fixed;
    top: 122px;
    right: 24px;
    width: 150px;
    z-index: 890;
}

/* Open heading area: no surrounding card. */
.app-intro {
    position: relative;
    overflow: hidden;
    text-align: center;
    padding: 35px 80px 45px;
    margin-bottom: 20px;
}

.app-intro h1.floating-headline {
    font-family: Georgia, "Times New Roman", serif !important;
    font-size: clamp(40px, 4.8vw, 64px) !important;
    font-weight: 700 !important;
    line-height: 1.2 !important;
    letter-spacing: -0.8px !important;
    color: #183c34 !important;
    margin: 0 0 24px;
    padding: 0;
    animation: headlineFloat 6s ease-in-out infinite;
}

.app-intro p {
    font-family: "Times New Roman", Times, serif !important;
    font-size: 20px !important;
    font-weight: 400 !important;
    line-height: 1.7 !important;
    color: #52635e !important;
    margin: 0;
}

/* Decorative resume papers remain outside the form. */
.intro-paper {
    position: absolute;
    top: 25px;
    width: 52px;
    height: 72px;
    padding: 11px;
    box-sizing: border-box;
    background: #ffffff;
    border: 1px solid #c2dbcf;
    border-radius: 7px;
    box-shadow: 0 8px 18px rgba(23, 63, 55, .07);
    pointer-events: none;
    animation: paperFloat 7s ease-in-out infinite;
}

.intro-paper.left {
    left: 8px;
    rotate: -12deg;
}

.intro-paper.right {
    right: 8px;
    rotate: 12deg;
    animation-delay: -3s;
}

.paper-avatar {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #a2cbbb;
    margin-bottom: 9px;
}

.paper-line {
    height: 3px;
    border-radius: 3px;
    background: #cbded5;
    margin-top: 5px;
}

.paper-line.short {
    width: 65%;
}

@keyframes paperFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}

.job-link {
    display: block;
    text-align: center;
    padding: 11px 8px;
    margin-bottom: 10px;
    border-radius: 10px;
    font-family: "Segoe UI", Arial, sans-serif;
    font-weight: 600;
    color: #ffffff !important;
    text-decoration: none !important;
}

.job-link:hover {
    filter: brightness(.92);
}

.job-link:focus-visible {
    outline: 3px solid #182230;
    outline-offset: 3px;
}

.job-mark {
    display: inline-block;
    margin-right: 6px;
    padding: 1px 5px;
    border-radius: 4px;
    background: rgba(255, 255, 255, .18);
}

@media (max-width: 1000px) {
    .block-container {
        padding-top: 2rem;
    }

    .app-brand {
        position: relative;
        top: auto;
        left: auto;
        max-width: 100%;
        margin-bottom: 16px;
        font-size: 12px;
    }

    .st-key-account_header,
    .st-key-notes_header {
        position: relative;
        top: auto;
        right: auto;
        width: 100%;
        max-width: 100%;
        margin-bottom: 12px;
    }
}

@media (max-width: 700px) {
    .app-intro {
        padding: 25px 5px 35px;
    }

    .app-intro h1 {
        font-size: 28px !important;
    }

    .intro-paper {
        display: none;
    }
}

@media (prefers-reduced-motion: reduce) {
    .intro-paper {
        animation: none;
    }
}
/* App name at the top-left. */
.app-brand {
    position: fixed !important;
    top: 0 !important;
    left: 24px !important;
    height: 58px !important;
    display: flex !important;
    align-items: center !important;
    margin: 0 !important;
    padding: 0 !important;
    max-width: calc(100vw - 600px) !important;
    z-index: 1000000 !important;

    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

/* Account controls immediately before Streamlit's Deploy area. */
.st-key-account_header {
    position: fixed !important;
    top: 4px !important;
    right: 165px !important;
    width: 360px !important;
    max-width: none !important;
    margin: 0 !important;
    padding: 3px 8px !important;
    z-index: 1000000 !important;

    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: none !important;
}

.st-key-account_header [data-testid="stHorizontalBlock"] {
    align-items: center !important;
}

.st-key-account_header button {
    min-height: 34px !important;
}

/* Notes remain just below the top bar. */
.st-key-notes_header {
    top: 72px !important;
}

/* Stack controls on smaller screens to avoid overlap. */
@media (max-width: 1100px) {
    .app-brand {
        position: relative !important;
        top: auto !important;
        left: auto !important;
        height: auto !important;
        max-width: 100% !important;
        margin-bottom: 16px !important;
    }

    .st-key-account_header,
    .st-key-notes_header {
        position: relative !important;
        top: auto !important;
        right: auto !important;
        width: 100% !important;
        max-width: 100% !important;
        margin-bottom: 12px !important;
    }
}
/* Move My Notes closer to the right edge. */
.st-key-notes_header {
    right: 10px !important;
    width: 150px !important;
    max-width: calc(100vw - 20px);
}

/* Green button with readable white text. */
.st-key-notes_header [data-testid="stPopover"] > button {
    background: #096b45 !important;
    border: 1px solid #096b45 !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}

.st-key-notes_header [data-testid="stPopover"] > button p,
.st-key-notes_header [data-testid="stPopover"] > button svg {
    color: #ffffff !important;
}

.st-key-notes_header [data-testid="stPopover"] > button:hover {
    background: #075336 !important;
    border-color: #075336 !important;
}

@media (max-width: 1100px) {
    .st-key-notes_header {
        right: auto !important;
        margin-left: auto !important;
    }
}
</style>
"""

# =========================================================
# HELPERS
# =========================================================

def logout():
    for key in list(st.session_state):
        del st.session_state[key]
    st.rerun()


def show_items(items, empty_message="No items identified."):
    if not items:
        st.caption(empty_message)
        return

    for item in items:
        st.write(f"• {item}")


def show_learning_resource(topic, key_prefix):
    resource = LEARNING_RESOURCES[topic]

    st.write(f"**{topic}**")
    st.write(resource["focus"])

    website = st.selectbox(
        "Choose a learning website",
        list(resource["websites"]),
        key=f"{key_prefix}_website_{topic}",
    )

    st.link_button(
        f"Visit {website}",
        resource["websites"][website],
        use_container_width=True,
    )

    st.write("**Practice project**")
    st.write(resource["project"])


def show_role_learning(role, index):
    gap_text = " ".join(
        str(item) for item in role.get("skill_gaps", [])
    )

    topics = [
        topic
        for topic, resource in LEARNING_RESOURCES.items()
        if re.search(resource["pattern"], gap_text, re.IGNORECASE)
    ]

    with st.expander("Learn missing skills"):
        if not topics:
            st.caption("Choose a topic to explore learning resources.")
            topics = list(LEARNING_RESOURCES)

        topic = st.selectbox(
            "Choose a skill",
            topics,
            key=f"role_{index}_topic",
        )

        show_learning_resource(topic, f"role_{index}")


def job_links(role, location, job_type):
    suffix = {
        "All types": "",
        "Full-time": " full time",
        "Internship": " internship",
        "Contract": " contract",
    }.get(job_type, "")

    query = f"{role}{suffix}".strip()

    return {
        "LinkedIn": (
            "https://www.linkedin.com/jobs/search/?"
            + urlencode({"keywords": query, "location": location})
        ),
        "Indeed": (
            "https://www.indeed.com/jobs?"
            + urlencode({"q": query, "l": location})
        ),
        "Dice": (
            "https://www.dice.com/jobs?"
            + urlencode({"q": query, "location": location})
        ),
        "Glassdoor": (
            "https://www.glassdoor.com/Job/jobs.htm?"
            + urlencode({"sc.keyword": f"{query} {location}".strip()})
        ),
        "ZipRecruiter": (
            "https://www.ziprecruiter.com/jobs-search?"
            + urlencode({"search": query, "location": location})
        ),
    }


def show_job_buttons(links):
    styles = {
        "LinkedIn": ("in", "#0a66c2"),
        "Indeed": ("i", "#253b80"),
        "Dice": ("D", "#b82025"),
        "Glassdoor": ("G", "#087f5b"),
        "ZipRecruiter": ("Z", "#344f30"),
    }

    columns = st.columns(3)

    for index, (name, url) in enumerate(links.items()):
        mark, color = styles[name]

        with columns[index % 3]:
            st.html(
                f'<a class="job-link" '
                f'href="{escape(url, quote=True)}" '
                f'target="_blank" rel="noopener noreferrer" '
                f'style="background:{color}">'
                f'<span class="job-mark">{mark}</span>'
                f'{escape(name)}</a>'
            )


def make_report(result, notes=""):
    score = result.get("ats_score")

    lines = [
        BRAND,
        "RESUME REVIEW",
        "",
        result.get("summary", ""),
        "",
        "ESTIMATED ATS READINESS",
        (
            f"{score}/100 — {result.get('ats_label', '')}"
            if score is not None
            else "Not scored"
        ),
        "App estimate based on text, not an employer ATS score.",
        "",
    ]

    for category in result.get("score_categories", []):
        lines.extend([
            f"{category.get('name', '')}: "
            f"{category.get('rating', '')}/5",
            f"Evidence: {category.get('evidence', '')}",
            f"Improve: {category.get('improvement', '')}",
            "",
        ])

    lines.append("STRENGTHS")
    lines.extend(f"- {x}" for x in result.get("strengths", []))
    lines.extend(["", "PRIORITY IMPROVEMENTS"])

    for item in result.get("top_improvements", []):
        lines.extend([
            item.get("issue", ""),
            f"Evidence: {item.get('resume_evidence', '')}",
            f"Action: {item.get('suggested_action', '')}",
            "",
        ])

    lines.append("READABILITY AND COMPLETENESS")
    lines.extend(
        f"- {x}" for x in result.get("readability_notes", [])
    )
    lines.extend(["", "BULLET SUGGESTIONS"])

    for item in result.get("bullet_suggestions", []):
        lines.extend([
            f"Original: {item.get('original', '')}",
            f"Suggested: {item.get('improved', '')}",
            f"Clarification: {item.get('clarification_needed', '')}",
            "",
        ])

    lines.append("RECOMMENDED ROLES")

    for role in result.get("recommended_roles", []):
        lines.extend([
            f"{role.get('role', '')} — {role.get('fit', '')}",
            role.get("reason", ""),
            "Evidence:",
            *[f"- {x}" for x in role.get("resume_evidence", [])],
            "Skills to strengthen or demonstrate:",
            *[f"- {x}" for x in role.get("skill_gaps", [])],
            "",
        ])

    match = result.get("job_match", {})
    lines.extend(["JOB MATCH", match.get("summary", "")])

    for field, label in [
        ("matching_requirements", "Matching requirements"),
        ("requirements_not_shown", "Requirements not shown"),
        ("suggested_changes", "Suggested changes"),
    ]:
        lines.append(label)
        lines.extend(f"- {x}" for x in match.get(field, []))

    lines.extend(["", "MY NOTES", notes or "No notes added."])
    return "\n".join(lines)


def sample_result():
    return {
        "is_resume": True,
        "is_sample": True,
        "summary": (
            "SAMPLE PREVIEW: This fictional candidate has introductory "
            "Python, SQL, and dashboard experience. These results "
            "demonstrate the app and do not analyze your resume."
        ),
        "ats_score": 70,
        "ats_label": "Average",
        "score_categories": [
            {
                "name": "Section completeness",
                "rating": 4,
                "evidence": "Education, skills, and a project are included.",
                "improvement": "Add contact details and relevant experience.",
            },
            {
                "name": "Skills clarity",
                "rating": 4,
                "evidence": "Python, SQL, and Excel are named.",
                "improvement": "Connect each skill to a specific task.",
            },
            {
                "name": "Experience and project evidence",
                "rating": 3,
                "evidence": "A dashboard project is described briefly.",
                "improvement": "Explain the dataset and analysis performed.",
            },
            {
                "name": "Bullet clarity",
                "rating": 3,
                "evidence": "The project description identifies an output.",
                "improvement": "Describe the steps and supported findings.",
            },
        ],
        "strengths": [
            "Names relevant technical tools.",
            "Includes a practical project.",
        ],
        "top_improvements": [
            {
                "issue": "Add detail to the dashboard project.",
                "resume_evidence": "Built a dashboard using Python and CSV data.",
                "suggested_action": (
                    "Describe the data cleaning, charts, and questions answered."
                ),
            }
        ],
        "readability_notes": [
            "Use clear section headings and consistent bullet wording."
        ],
        "recommended_roles": [
            {
                "role": "Junior Data Analyst",
                "fit": "Work toward",
                "reason": (
                    "Python, SQL, and dashboard work support exploring "
                    "entry-level analytical roles."
                ),
                "resume_evidence": [
                    "Python and SQL are listed.",
                    "A dashboard project is included.",
                ],
                "skill_gaps": [
                    "SQL query examples are not shown.",
                    "Data cleaning methods are not described.",
                ],
            }
        ],
        "bullet_suggestions": [
            {
                "original": "Built a dashboard using Python and CSV data.",
                "improved": "Developed a Python dashboard to display CSV data.",
                "clarification_needed": (
                    "What questions did the dashboard help answer?"
                ),
            }
        ],
        "job_match": {
            "summary": "This sample does not compare your job description.",
            "matching_requirements": [],
            "requirements_not_shown": [],
            "suggested_changes": [],
        },
    }


def display_results(result, location, job_type):
    st.divider()
    st.header("Your resume. Your next steps.")

    if result.get("is_sample"):
        st.info("Sample preview — fictional demonstration results.")

    st.write(result.get("summary", ""))

    if not result.get("is_resume", False):
        st.warning(
            "Add a more complete resume for supported scores "
            "and role recommendations."
        )

    score_tab, improve_tab, jobs_tab, match_tab = st.tabs([
        "Readiness Score",
        "Improve My Resume",
        "Find Jobs",
        "Job Match",
    ])

    with score_tab:
        score = result.get("ats_score")

        if score is None:
            st.info("Not enough resume evidence to assign a score.")
        else:
            score_column, explanation_column = st.columns([1, 2])

            with score_column:
                st.metric("Estimated ATS Readiness", f"{score}/100")
                st.write(f"**{result.get('ats_label', '')}**")
                st.progress(max(0.0, min(float(score) / 100, 1.0)))

            with explanation_column:
                st.write(
                    "The score reflects section completeness, skills clarity, "
                    "experience and project evidence, and bullet clarity."
                )
                st.caption(
                    "This is the app's text-based estimate, not an employer's "
                    "ATS score. It does not assess visual layout or predict "
                    "hiring outcomes."
                )

            with st.expander("Score labels"):
                st.table({
                    "Score": ["0–69", "70–84", "85–90", "91–100"],
                    "Label": [
                        "Needs major improvement",
                        "Average",
                        "Good",
                        "Strong",
                    ],
                })

            for item in result.get("score_categories", []):
                with st.container(border=True):
                    st.write(
                        f"**{item.get('name', '')} · "
                        f"{item.get('rating', '')}/5**"
                    )
                    st.write(item.get("evidence", ""))
                    st.write("**How to improve**")
                    st.write(item.get("improvement", ""))

    with improve_tab:
        st.subheader("Your priority improvements")

        improvements = result.get("top_improvements", [])

        if not improvements:
            st.caption("No supported improvements were generated.")

        for index, item in enumerate(improvements, start=1):
            with st.container(border=True):
                st.write(f"**{index}. {item.get('issue', '')}**")
                st.write(item.get("suggested_action", ""))

                with st.expander("Evidence from your resume"):
                    st.write(item.get("resume_evidence", ""))

        st.subheader("What's working well")
        show_items(result.get("strengths", []))

        with st.expander("Readability and completeness"):
            show_items(result.get("readability_notes", []))

        st.subheader("Make your bullet points clearer")
        bullets = result.get("bullet_suggestions", [])

        if not bullets:
            st.caption("Not enough evidence was available for rewrites.")

        for item in bullets:
            with st.container(border=True):
                st.write("**Original**")
                st.write(item.get("original", ""))
                st.write("**Suggested wording**")
                st.write(item.get("improved", ""))

                if item.get("clarification_needed"):
                    st.info(item["clarification_needed"])

        with st.expander("Check the extracted resume text"):
            st.text_area(
                "Text read from your document",
                value=st.session_state.get("review_text", ""),
                height=250,
                disabled=True,
                key="extracted_resume_preview",
            )

    with jobs_tab:
        st.subheader("Explore roles that fit your experience")
        st.caption(
            "These buttons open keyword searches. Confirm requirements "
            "and filters on the selected platform."
        )

        roles = result.get("recommended_roles", [])

        if not roles:
            st.info("No supported role recommendations were generated.")

        for index, role in enumerate(roles):
            with st.container(border=True):
                st.subheader(role.get("role", "Suggested role"))
                st.caption(role.get("fit", ""))
                st.write(role.get("reason", ""))

                with st.expander("Evidence and next steps"):
                    st.write("**Evidence from your background**")
                    show_items(role.get("resume_evidence", []))

                    st.write("**Skills to strengthen or demonstrate**")
                    show_items(
                        role.get("skill_gaps", []),
                        "No specific gaps identified. Review each listing.",
                    )
                    st.caption(
                        "Missing evidence does not prove you lack a skill."
                    )

                show_role_learning(role, index)
                st.write("**Find openings**")
                show_job_buttons(
                    job_links(role.get("role", ""), location, job_type)
                )

        st.caption("Applications are completed on the selected website.")

    with match_tab:
        match = result.get("job_match", {})
        st.subheader("Compare with your target job")
        st.write(match.get("summary", ""))

        for field, label in [
            ("matching_requirements", "Matching requirements"),
            ("requirements_not_shown", "Requirements not shown"),
            ("suggested_changes", "Suggested changes"),
        ]:
            if match.get(field):
                st.write(f"**{label}**")
                show_items(match[field])

    st.divider()

    elapsed = result.get("elapsed_seconds")
    if isinstance(elapsed, (int, float)):
        st.caption(f"Generated in {elapsed:.1f} seconds.")

    st.download_button(
        "Download My Review",
        data=make_report(
            result,
            st.session_state.get("personal_review_notes", ""),
        ),
        file_name="Build_And_Apply_Resume_Review.txt",
        mime="text/plain",
        use_container_width=True,
    )


# =========================================================
# AUTHENTICATION
# =========================================================

require_login()

st.html(APP_CSS)


# =========================================================
# BRAND — RENDERED ONCE
# =========================================================
logo_path = Path(__file__).resolve().parent / "assets" / "logo.png"

if logo_path.is_file():
    logo_base64 = base64.b64encode(
        logo_path.read_bytes()
    ).decode("ascii")

    st.html(
        f"""
<style>
.app-brand img {{
    display: block;
    width: 250px;
    max-width: 100%;
    height: auto;
}}
</style>

<div class="app-brand">
    <img
        src="data:image/png;base64,{logo_base64}"
        alt="{escape(BRAND, quote=True)}"
    >
</div>
"""
    )
else:
    st.html(
        f'<div class="app-brand">{escape(BRAND)}</div>'
    )

# =========================================================
# ACCOUNT CONTROLS
# =========================================================

allow_ollama = (
    os.getenv("ENABLE_OLLAMA", "false").strip().lower() == "true"
)

provider_options = (
    ["Gemini", "Ollama"] if allow_ollama else ["Gemini"]
)

if st.session_state.get("selected_provider") not in provider_options:
    st.session_state["selected_provider"] = "Gemini"

with st.container(key="account_header"):
    provider_column, profile_column, logout_column = st.columns(
        [1.05, 1.35, 1.1]
    )

    with provider_column:
        if allow_ollama:
            provider = st.radio(
                "AI provider",
                provider_options,
                horizontal=True,
                label_visibility="collapsed",
                key="selected_provider",
            )
        else:
            provider = "Gemini"
            st.html('<div class="provider-name">Gemini</div>')

    with profile_column:
        if st.button(
            "My Profile",
            key="header_my_profile",
            use_container_width=True,
        ):
            show_profile()

    with logout_column:
        account = st.session_state.get("auth_account", {})
        account_label = (
            "Sign in"
            if account.get("mode") == "guest"
            else "Sign out"
        )

        if st.button(
            account_label,
            key="header_sign_out",
            use_container_width=True,
        ):
            logout()

ollama_model = "qwen2.5:3b"


# =========================================================
# NOTES
# =========================================================

with st.container(key="notes_header"):
    with st.popover("📝 My Notes"):
        st.text_area(
            "Write your notes",
            placeholder="Reminders, ideas, or your next steps...",
            height=180,
            key="personal_review_notes",
        )

        st.download_button(
            "Download notes",
            data=st.session_state.get("personal_review_notes", ""),
            file_name="My_Career_Notes.txt",
            mime="text/plain",
            key="download_notes",
            use_container_width=True,
        )

        st.caption("Notes are also included in your review download.")


# =========================================================
# MAIN HEADING — RENDERED ONCE
# =========================================================

paper = (
    '<div class="paper-avatar"></div>'
    '<div class="paper-line"></div>'
    '<div class="paper-line"></div>'
    '<div class="paper-line short"></div>'
)
st.html(
    """
<style>
.app-intro {
    text-align: center;
    padding: 40px 12px 50px;
    margin-bottom: 20px;
}

.app-intro h1.floating-headline {
    font-family: "Trebuchet MS", "Segoe UI", sans-serif !important;
    font-size: clamp(36px, 4.5vw, 56px) !important;
    font-weight: 600 !important;
    line-height: 1.2 !important;
    letter-spacing: -1px !important;
    color: #183c34 !important;
    margin: 0 0 24px;
    padding: 0;
    animation: headlineFloat 6s ease-in-out infinite;
}

.floating-headline .headline-second-line {
    display: block;
    color: #087f78;
    margin-top: 8px;
}

.floating-headline .headline-briefcase {
    display: inline-block;
    font-size: 0.75em;
    margin-left: 8px;
}

.app-intro h1.floating-headline {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif !important;
    font-size: clamp(38px, 4.5vw, 58px) !important;
    font-weight: 800 !important;
    line-height: 1.15 !important;
    letter-spacing: -1.2px !important;
    color: #183c34 !important;
    margin: 0 0 24px;
    padding: 0;
    animation: headlineFloat 6s ease-in-out infinite;
}
@keyframes headlineFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-7px); }
}

@media (max-width: 700px) {
    .app-intro h1.floating-headline {
        font-size: 36px !important;
    }

    .app-intro p {
        font-size: 15px;
    }
}

@media (prefers-reduced-motion: reduce) {
    .app-intro h1.floating-headline {
        animation: none;
    }
}
</style>

<section class="app-intro">
    <h1 class="floating-headline">
        Good Resumes Find
        <span class="headline-second-line">
            Great Roles
            <span class="headline-briefcase" aria-hidden="true">💼</span>
        </span>
    </h1>

    <p>
        Understand your experience. Build your skills.<br>
        Take your next step with confidence.
    </p>
</section>
"""
)


# =========================================================
# RESUME INPUT
# =========================================================

left, right = st.columns([1.1, 1], gap="large")

with left:
    with st.container(border=True):
        st.subheader("Start with your resume")
        st.caption("Upload a document or paste your resume text.")

        method = st.radio(
            "Resume source",
            ["Upload file", "Paste text"],
            horizontal=True,
            key="resume_source",
        )

        uploaded_file = None
        resume_text = ""

        if method == "Upload file":
            uploaded_file = st.file_uploader(
                "Choose your resume",
                type=["pdf", "docx"],
                key="resume_upload",
            )
            st.caption("Text-based PDF or DOCX · Maximum 10 MB")

        else:
            resume_text = st.text_area(
                "Paste your resume",
                height=260,
                placeholder="Education, skills, experience, projects...",
                key="resume_pasted_text",
            )

    with st.popover(
    "Add projects and courses",
    use_container_width=True,
):
        additional_projects = st.text_area(
            "Completed projects",
            placeholder=(
                "Describe projects not included in your resume. "
                "What did you build, and which tools did you use?"
            ),
            key="additional_projects",
        )

        additional_courses = st.text_area(
            "Relevant courses",
            placeholder="List courses and related hands-on work.",
            key="additional_courses",
        )


# =========================================================
# GOALS — EACH FIELD CREATED ONCE
# =========================================================
with right:
    with st.container(border=True):
        st.subheader("Where do you want to go?")
        target_role = st.text_input(
            "Target role",
            placeholder="For example: Data Analyst",
            key="goal_target_role",
        )

        selected_state = st.selectbox(
            "Preferred state",
            US_STATES,
            key="goal_state",
        )

        city = ""

        if selected_state not in ("Any location", "Remote"):
            city = st.text_input(
                "Preferred city",
                placeholder="Optional—for example: Oklahoma City",
                key="goal_city",
            ).strip()

        if selected_state == "Any location":
            location = ""
        elif selected_state == "Remote":
            location = "Remote"
        elif city:
            location = f"{city}, {selected_state}, United States"
        else:
            location = f"{selected_state}, United States"

        job_type = st.selectbox(
            "Job type",
            ["All types", "Full-time", "Internship", "Contract"],
            key="goal_job_type",
        )

        job_description = st.text_area(
            "Job description",
            height=150,
            placeholder="Paste a job description for a focused comparison.",
            key="goal_job_description",
        )


# =========================================================
# KEEP RESULTS ALIGNED WITH INPUTS
# =========================================================

file_digest = (
    hashlib.sha256(uploaded_file.getvalue()).hexdigest()
    if uploaded_file is not None
    else None
)

signature_data = {
    "method": method,
    "file": file_digest,
    "resume": resume_text,
    "target_role": target_role,
    "job_description": job_description,
    "projects": additional_projects,
    "courses": additional_courses,
    "provider": provider,
    "model": (
        ollama_model
        if provider == "Ollama"
        else os.getenv("GEMINI_MODEL", "")
    ),
    "version": 6,
}

input_signature = hashlib.sha256(
    json.dumps(signature_data, sort_keys=True).encode("utf-8")
).hexdigest()

if st.session_state.get("review_signature") != input_signature:
    st.session_state.pop("review_result", None)
    st.session_state.pop("review_text", None)
    st.session_state.pop("extracted_resume_preview", None)

    for state_key in list(st.session_state):
        if state_key.startswith("role_"):
            del st.session_state[state_key]

    st.session_state["review_signature"] = input_signature


# =========================================================
# ANALYSIS
# =========================================================

with st.expander("Privacy details"):
    if provider == "Gemini":
        st.caption(
            "Your resume, optional job description, projects, and courses "
            "are sent to Google Gemini when you click Analyze My Resume."
        )
    else:
        st.caption(
            "Your resume and optional background details are processed "
            "by Ollama on the computer running this app."
        )

    st.caption(
        "Saved profiles are stored separately in Firebase. "
        "Your saved profile is not automatically included in an AI request."
    )

has_resume = uploaded_file is not None or bool(resume_text.strip())

analyze_clicked = st.button(
    "Analyze My Resume",
    type="primary",
    use_container_width=True,
    disabled=not has_resume,
)

preview_clicked = st.button(
    "Preview Sample Results",
    use_container_width=True,
)

if preview_clicked:
    st.session_state.pop("extracted_resume_preview", None)
    st.session_state["review_text"] = (
        "Sample Candidate\n"
        "Education: Bachelor's in Computer Science\n"
        "Skills: Python, SQL, Excel\n"
        "Project: Built a dashboard using Python and CSV data."
    )
    st.session_state["review_result"] = sample_result()

if analyze_clicked:
    st.session_state.pop("review_result", None)
    st.session_state.pop("review_text", None)
    st.session_state.pop("extracted_resume_preview", None)

    try:
        if (
            uploaded_file is not None
            and uploaded_file.size > 10 * 1024 * 1024
        ):
            raise ValueError("Please upload a resume smaller than 10 MB.")

        with st.spinner("Reading your resume..."):
            text = (
                extract_resume_text(uploaded_file)
                if uploaded_file is not None
                else resume_text.strip()
            )

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                "No readable text was found. Try a text-based PDF, "
                "a DOCX document, or paste your resume."
            )

        st.session_state["review_text"] = text
        started = perf_counter()

        with st.spinner("Preparing your resume review..."):
            analysis = analyze_resume(
                resume_text=text,
                target_role=target_role.strip(),
                job_description=job_description.strip(),
                provider=provider,
                ollama_model=ollama_model,
                additional_projects=additional_projects.strip(),
                additional_courses=additional_courses.strip(),
            )

        elapsed = perf_counter() - started

        required_fields = {
            "is_resume",
            "summary",
            "ats_score",
            "ats_label",
            "score_categories",
            "strengths",
            "top_improvements",
            "readability_notes",
            "recommended_roles",
            "bullet_suggestions",
            "job_match",
        }

        if (
            not isinstance(analysis, dict)
            or not required_fields.issubset(analysis)
        ):
            raise ValueError(
                "The analyzer returned an unexpected result format. "
                "Check that ai_analyzer.py is the latest version."
            )

        analysis["elapsed_seconds"] = elapsed
        analysis["is_sample"] = False
        st.session_state["review_result"] = analysis

    except ValueError as error:
        st.error(str(error))

result = st.session_state.get("review_result")

if result:
    display_results(result, location, job_type)


# =========================================================
# LEARNING LIBRARY
# =========================================================

st.divider()

with st.expander("Browse learning resources"):
    st.write(
        "Choose a topic, select your preferred website, "
        "and explore a practice project."
    )

    topic = st.selectbox(
        "What would you like to learn?",
        list(LEARNING_RESOURCES),
        key="learning_library_topic",
    )

    show_learning_resource(topic, "library")

    st.caption(
        "Availability and pricing vary by website. "
        "Some resources include paid certificates or labs."
    )

st.caption(f"{BRAND} · Built for students and career changers")