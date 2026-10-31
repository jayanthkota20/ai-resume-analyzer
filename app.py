import hashlib
import re
from html import escape
from urllib.parse import urlencode
import os

import streamlit as st

from ai_analyzer import analyze_resume
from auth_ui import require_login
from resume_parser import extract_resume_text


BRAND = "BUILD AND APPLY THROUGH US"

st.set_page_config(
    page_title=BRAND,
    page_icon="💼",
    layout="wide",
)


# Fixed learning catalog: the AI does not generate website URLs.
LEARNING_RESOURCES = {
    "Python": {
        "pattern": r"\bpython\b",
        "focus": "Variables, functions, collections, and reading files.",
        "project": (
            "Build an expense tracker that reads and writes CSV files, "
            "groups expenses by category, and handles invalid input."
        ),
        "websites": {
            "W3Schools — Python": "https://www.w3schools.com/python/",
        },
    },
    "SQL": {
        "pattern": r"\bsql\b|\bjoins?\b|\bdatabase\b",
        "focus": "Filtering, joins, grouping, and aggregate functions.",
        "project": (
            "Create customers, products, and orders tables in SQLite. "
            "Use joins and GROUP BY to answer five business questions "
            "and document your queries."
        ),
        "websites": {
            "W3Schools — SQL": "https://www.w3schools.com/sql/",
        },
    },
    "Data Analysis": {
        "pattern": (
            r"\bpandas\b|data clean|data analy|"
            r"visuali[sz]|dashboard"
        ),
        "focus": (
            "Reading tables, cleaning data, calculating summary "
            "statistics, combining tables, and creating plots."
        ),
        "project": (
            "Analyze a public CSV dataset. Check missing values and "
            "duplicates, explain your cleaning decisions, create three "
            "charts, and document three findings."
        ),
        "websites": {
            "pandas — Getting started": (
                "https://pandas.pydata.org/docs/"
                "getting_started/intro_tutorials/"
            ),
        },
    },
    "Machine Learning": {
        "pattern": (
            r"machine learning|scikit|model evaluation|"
            r"cross.validation|\bclassification\b|\bregression\b"
        ),
        "focus": (
            "Preprocessing, model fitting, train/test splits, "
            "and evaluation. Basic Python and ML knowledge helps."
        ),
        "project": (
            "Compare a baseline with a trained model on a public dataset. "
            "Separate training and test data, avoid data leakage, and "
            "explain the evaluation metrics and limitations."
        ),
        "websites": {
            "scikit-learn — Getting started": (
                "https://scikit-learn.org/stable/getting_started.html"
            ),
        },
    },
    "Statistics": {
        "pattern": r"statistic|probability|hypothesis",
        "focus": (
            "Descriptive statistics, probability, sampling, "
            "and interpreting uncertainty."
        ),
        "project": (
            "Explore a public dataset. Compare two groups, visualize "
            "their distributions, and explain why an observed "
            "relationship does not prove causation."
        ),
        "websites": {
            "Khan Academy — Statistics and probability": (
                "https://www.khanacademy.org/math/statistics-probability"
            ),
        },
    },
    "Cybersecurity": {
        "pattern": (
            r"cyber.?security|information security|security operations|"
            r"\bsoc\b|incident response|threat detection|network security"
        ),
        "focus": (
            "Security fundamentals, common threats, network protection, "
            "and incident response concepts."
        ),
        "project": (
            "Use sample security logs in a local lab to identify suspicious "
            "activity. Write an incident timeline, explain the evidence, "
            "and suggest defensive actions."
        ),
        "websites": {
            "Cisco Networking Academy": (
                "https://www.netacad.com/courses/"
                "introduction-to-cybersecurity"
            ),
            "W3Schools — Cybersecurity": (
                "https://www.w3schools.com/cybersecurity/"
            ),
            "PortSwigger — Web security labs": (
                "https://portswigger.net/web-security"
            ),
        },
    },
    "Web Security": {
        "pattern": (
            r"web security|application security|\bowasp\b|"
            r"\bxss\b|sql injection"
        ),
        "focus": (
            "Web vulnerabilities, authentication weaknesses, "
            "and defensive fixes using training labs."
        ),
        "project": (
            "Complete beginner labs in a provided training environment. "
            "Write a report explaining the vulnerability, the evidence "
            "observed, and a defensive fix."
        ),
        "websites": {
            "PortSwigger — Web Security Academy": (
                "https://portswigger.net/web-security"
            ),
            "W3Schools — Cybersecurity foundations": (
                "https://www.w3schools.com/cybersecurity/"
            ),
        },
    },
    "Frontend Development": {
        "pattern": (
            r"front.?end|\bhtml\b|\bcss\b|\bjavascript\b|"
            r"\breact\b|responsive design|accessibility"
        ),
        "focus": (
            "HTML, CSS, JavaScript, responsive layouts, "
            "accessible forms, and browser interactions."
        ),
        "project": (
            "Build a responsive job-search interface with filters, saved "
            "job cards, and accessible forms. Test keyboard navigation "
            "and layouts on different screen sizes."
        ),
        "websites": {
            "MDN Web Docs": (
                "https://developer.mozilla.org/en-US/docs/"
                "Learn_web_development"
            ),
            "W3Schools — HTML": "https://www.w3schools.com/html/",
            "W3Schools — JavaScript": "https://www.w3schools.com/js/",
            "The Odin Project": "https://www.theodinproject.com/paths",
        },
    },
    "Backend Development": {
        "pattern": (
            r"back.?end|server.?side|rest(?:ful)? api|"
            r"\bnode\.?js\b|\bdjango\b|\bflask\b|\bfastapi\b"
        ),
        "focus": (
            "HTTP, API design, server-side validation, databases, "
            "authentication, and error handling."
        ),
        "project": (
            "Build a task-management API with a database. Add input "
            "validation, authentication, checks that users can access "
            "only their own tasks, and tests for rejected requests."
        ),
        "websites": {
            "MDN — Server-side development": (
                "https://developer.mozilla.org/en-US/docs/"
                "Learn_web_development/Extensions/Server-side"
            ),
            "The Odin Project": "https://www.theodinproject.com/paths",
            "Full Stack Open": "https://fullstackopen.com/en/",
        },
    },
    "Full Stack Development": {
        "pattern": r"full.?stack|end.to.end web|\bmern\b|mean stack",
        "focus": (
            "Connecting a frontend, backend API, database, "
            "authentication, and deployment."
        ),
        "project": (
            "Build a job-application tracker with a frontend, backend, "
            "and database. Let users manage their own applications, "
            "filter by status, and view application totals."
        ),
        "websites": {
            "The Odin Project": "https://www.theodinproject.com/paths",
            "Full Stack Open": "https://fullstackopen.com/en/",
            "MDN Web Docs": (
                "https://developer.mozilla.org/en-US/docs/"
                "Learn_web_development"
            ),
        },
    },
    "Generative AI": {
        "pattern": (
            r"generative ai|\bgen\s?ai\b|\bllms?\b|\brag\b|"
            r"retrieval.augmented|prompt engineering|"
            r"\bembeddings?\b|transformers"
        ),
        "focus": (
            "Language models, prompting, embeddings, retrieval, "
            "response evaluation, and application limitations."
        ),
        "project": (
            "Build a question-answering tool over a small set of public "
            "documents. Show source references and test whether it "
            "declines questions the documents cannot answer."
        ),
        "websites": {
            "Microsoft — Generative AI for Beginners": (
                "https://microsoft.github.io/"
                "generative-ai-for-beginners/"
            ),
            "Hugging Face — LLM Course": (
                "https://huggingface.co/learn/llm-course/chapter1/1"
            ),
        },
    },
    "AWS": {
        "pattern": (
            r"\baws\b|amazon web services|\bec2\b|"
            r"\bs3\b|cloudwatch|aws lambda"
        ),
        "focus": (
            "AWS services, IAM, compute, storage, networking, "
            "monitoring, and cost management."
        ),
        "project": (
            "Design an AWS architecture for a small web application. "
            "Explain service choices, access controls, monitoring, and "
            "estimated costs. A diagram and design document can be "
            "completed without deploying paid resources."
        ),
        "websites": {
            "AWS Skill Builder": "https://skillbuilder.aws/",
            "W3Schools — AWS fundamentals": (
                "https://www.w3schools.com/aws/"
            ),
        },
    },
    "Cloud Computing": {
        "pattern": (
            r"\bcloud\b|\bazure\b|\bgcp\b|"
            r"google cloud|cloud architecture"
        ),
        "focus": (
            "Cloud service models, identity, networking, availability, "
            "shared responsibility, and cost awareness."
        ),
        "project": (
            "Compare two cloud deployment designs for a small application. "
            "Document availability, security controls, backup strategy, "
            "and cost tradeoffs."
        ),
        "websites": {
            "Microsoft Learn — Azure": (
                "https://learn.microsoft.com/en-us/training/azure/"
            ),
            "AWS Skill Builder": "https://skillbuilder.aws/",
            "W3Schools — AWS fundamentals": (
                "https://www.w3schools.com/aws/"
            ),
        },
    },
}
# Give every learning topic at least three website choices.
LEARNING_WEBSITES = {
    "Python": {
        "W3Schools — Python": (
            "https://www.w3schools.com/python/"
        ),
        "Google — Python Class": (
            "https://developers.google.com/edu/python"
        ),
        "Python.org — Official Tutorial": (
            "https://docs.python.org/3/tutorial/"
        ),
    },

    "SQL": {
        "W3Schools — SQL": (
            "https://www.w3schools.com/sql/"
        ),
        "SQLBolt — Interactive Lessons": (
            "https://sqlbolt.com/"
        ),
        "SQLZoo — Tutorials and Exercises": (
            "https://sqlzoo.net/wiki/SQL_Tutorial"
        ),
    },

    "Data Analysis": {
        "pandas — Official Tutorials": (
            "https://pandas.pydata.org/docs/"
            "getting_started/intro_tutorials/"
        ),
        "Kaggle — Pandas": (
            "https://www.kaggle.com/learn/pandas"
        ),
        "W3Schools — Pandas": (
            "https://www.w3schools.com/python/pandas/"
        ),
    },

    "Machine Learning": {
        "Google — Machine Learning Crash Course": (
            "https://developers.google.com/"
            "machine-learning/crash-course"
        ),
        "Kaggle — Intro to Machine Learning": (
            "https://www.kaggle.com/learn/intro-to-machine-learning"
        ),
        "scikit-learn — Official Guide": (
            "https://scikit-learn.org/stable/getting_started.html"
        ),
    },

    "Statistics": {
        "Khan Academy — Statistics and Probability": (
            "https://www.khanacademy.org/math/statistics-probability"
        ),
        "OpenStax — Introductory Statistics": (
            "https://openstax.org/details/books/"
            "introductory-statistics-2e"
        ),
        "OpenIntro — Statistics": (
            "https://www.openintro.org/book/os/"
        ),
    },

    "Cybersecurity": {
        "Cisco — Introduction to Cybersecurity": (
            "https://www.netacad.com/courses/"
            "introduction-to-cybersecurity"
        ),
        "W3Schools — Cybersecurity": (
            "https://www.w3schools.com/cybersecurity/"
        ),
        "PortSwigger — Web Security Academy": (
            "https://portswigger.net/web-security"
        ),
        "OWASP — Web Security Testing Guide": (
            "https://owasp.org/projects/web-security-testing-guide"
        ),
    },

    "Web Security": {
        "PortSwigger — Web Security Academy": (
            "https://portswigger.net/web-security"
        ),
        "OWASP — Web Security Testing Guide": (
            "https://owasp.org/projects/web-security-testing-guide"
        ),
        "W3Schools — Security Foundations": (
            "https://www.w3schools.com/cybersecurity/"
        ),
    },

    "Frontend Development": {
        "MDN — Web Development": (
            "https://developer.mozilla.org/en-US/docs/"
            "Learn_web_development"
        ),
        "W3Schools — HTML": (
            "https://www.w3schools.com/html/"
        ),
        "The Odin Project — Learning Paths": (
            "https://www.theodinproject.com/paths"
        ),
        "Full Stack Open — React and Web Development": (
            "https://fullstackopen.com/en/"
        ),
    },

    "Backend Development": {
        "MDN — Server-side Development": (
            "https://developer.mozilla.org/en-US/docs/"
            "Learn_web_development/Extensions/Server-side"
        ),
        "The Odin Project — Learning Paths": (
            "https://www.theodinproject.com/paths"
        ),
        "Full Stack Open — Backend and APIs": (
            "https://fullstackopen.com/en/"
        ),
    },

    "Full Stack Development": {
        "The Odin Project — Full Stack Paths": (
            "https://www.theodinproject.com/paths"
        ),
        "Full Stack Open": (
            "https://fullstackopen.com/en/"
        ),
        "MDN — Web Development": (
            "https://developer.mozilla.org/en-US/docs/"
            "Learn_web_development"
        ),
    },

    "Generative AI": {
        "Microsoft — Generative AI for Beginners": (
            "https://microsoft.github.io/"
            "generative-ai-for-beginners/"
        ),
        "Hugging Face — LLM Course": (
            "https://huggingface.co/learn/llm-course/chapter1/1"
        ),
        "Google — Introduction to LLMs": (
            "https://developers.google.com/"
            "machine-learning/crash-course/llm"
        ),
    },

    "AWS": {
        "AWS — Skill Builder": (
            "https://skillbuilder.aws/"
        ),
        "W3Schools — AWS Fundamentals": (
            "https://www.w3schools.com/aws/"
        ),
        "freeCodeCamp — Cloud Practitioner Video Course": (
            "https://www.freecodecamp.org/news/"
            "aws-certified-cloud-practitioner-study-course-"
            "pass-the-exam-with-this-free-13-hour-course"
        ),
    },

    "Cloud Computing": {
        "Microsoft Learn — Azure": (
            "https://learn.microsoft.com/en-us/training/azure/"
        ),
        "AWS — Skill Builder": (
            "https://skillbuilder.aws/"
        ),
        "Google Cloud — Training": (
            "https://cloud.google.com/learn/training"
        ),
        "W3Schools — AWS Fundamentals": (
            "https://www.w3schools.com/aws/"
        ),
    },
}

for topic_name, websites in LEARNING_WEBSITES.items():
    LEARNING_RESOURCES[topic_name]["websites"] = websites

PLATFORM_STYLES = {
    "LinkedIn": ("job-linkedin", "in"),
    "Indeed": ("job-indeed", "I"),
    "Dice": ("job-dice", "D"),
    "Glassdoor": ("job-glassdoor", "G"),
    "ZipRecruiter": ("job-ziprecruiter", "Z"),
}


st.markdown(
    """
<style>
.stApp {
    background: #ffffff;
    color: #182230;
}

[data-testid="stHeader"] {
    background: #ffffff !important;
}

.block-container {
    max-width: 1150px;
    padding-top: 6rem !important;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #182230 !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stWidgetLabel"] p {
    color: #182230;
    line-height: 1.65;
}

[data-testid="stCaptionContainer"] p {
    color: #526174 !important;
}

/* Fixed brand */
.brand {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    box-sizing: border-box;
    z-index: 999999;
    background: #ffffff;
    color: #096b65;
    padding: 20px 240px 20px 24px;
    border-bottom: 1px solid #e3e9ed;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 1.5px;
    box-shadow: 0 2px 8px rgba(24, 34, 48, 0.04);
}

/* AI selector */
.st-key-provider_header {
    position: fixed;
    top: 12px;
    right: 24px;
    z-index: 1000000;
    width: auto;
    background: #ffffff;
    padding: 4px 10px;
    border-radius: 10px;
}

.st-key-provider_header [data-testid="stRadio"] > div {
    gap: 14px;
}

.st-key-provider_header label p {
    color: #182230 !important;
    font-size: 14px !important;
    font-weight: 600;
}

/* Notes button */
.st-key-notes_header {
    position: fixed;
    top: 70px;
    right: 24px;
    z-index: 999998;
    width: auto;
}

.st-key-notes_header button {
    background: #096b65 !important;
    color: #ffffff !important;
    border: 1px solid #096b65 !important;
    border-radius: 10px !important;
}

.st-key-notes_header button p {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    font-weight: 700 !important;
}

/* Main heading */
.hero {
    text-align: center;
    padding: 30px 12px;
}

.eyebrow {
    color: #096b65;
    font-size: 13px;
    letter-spacing: 2px;
    font-weight: 700;
}

.hero h1 {
    font-family: "Segoe UI", Arial, sans-serif !important;
    font-size: clamp(30px, 4.5vw, 52px);
    line-height: 1.14;
    max-width: 850px;
    margin: 14px auto;
    font-weight: 800;
    letter-spacing: -1px;
    animation: headline-float 4s ease-in-out infinite;
}

.hero h1 .highlight {
    color: #096b65;
}

.hero h1 .briefcase {
    display: inline-block;
    animation: briefcase-float 3s ease-in-out infinite;
}

.hero p {
    color: #526174;
    font-size: 18px;
}

@keyframes headline-float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
}

@keyframes briefcase-float {
    0%, 100% { transform: translateY(0) rotate(-4deg); }
    50% { transform: translateY(-6px) rotate(4deg); }
}

/* Motivation cards */
.motivation-strip {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 10px;
    margin: 8px auto 24px;
}

.motivation-card {
    color: #123e38 !important;
    background: #e5f4ee !important;
    border: 1px solid #a6d2c2 !important;
    border-radius: 14px;
    padding: 10px 15px;
    font-family: "Segoe UI", Arial, sans-serif !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: 0.2px;
    animation: gentle-float 4s ease-in-out infinite alternate;
}

.motivation-card:nth-child(2n) {
    animation-delay: -2s;
}

@keyframes gentle-float {
    from { transform: translateY(0); }
    to { transform: translateY(-7px); }
}

.journey {
    background: #f1f8f6;
    border: 1px solid #d9eae5;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 24px;
    text-align: center;
    color: #23483f;
    font-size: 16px;
    line-height: 1.8;
}

/* Input fields */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    color: #182230 !important;
    -webkit-text-fill-color: #182230 !important;
    font-size: 16px !important;
    border: 1px solid #aebbc7 !important;
    border-radius: 8px;
}

input::placeholder,
textarea::placeholder {
    color: #667085 !important;
    -webkit-text-fill-color: #667085 !important;
    opacity: 1;
}

/* Resume upload */
[data-testid="stFileUploaderDropzone"] {
    background: #f7faf9;
    color: #182230;
    border: 1px dashed #8aaba2;
    border-radius: 12px;
}

[data-testid="stFileUploader"] button {
    background: #096b65 !important;
    color: #ffffff !important;
    border: 1px solid #096b65 !important;
    border-radius: 10px !important;
    min-height: 48px;
    padding: 12px 24px !important;
}

[data-testid="stFileUploader"] button *,
[data-testid="stFileUploader"] button p,
[data-testid="stFileUploader"] button svg {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

[data-testid="stFileUploader"] button:hover {
    background: #07534e !important;
}

[data-testid="stFileUploader"] button:focus-visible {
    outline: 3px solid #80cbc4 !important;
    outline-offset: 3px;
}

/* Primary and secondary buttons */
.stButton button[kind="primary"] {
    background: #096b65;
    border: none;
    border-radius: 10px;
    min-height: 48px;
}

.stButton button[kind="primary"] p {
    color: #ffffff !important;
    font-weight: 700;
}

.stButton button[kind="primary"]:hover {
    background: #07534e;
}

.stButton button[kind="primary"]:disabled {
    background: #e4e7ec;
    opacity: 1;
}

.stButton button[kind="primary"]:disabled p {
    color: #526174 !important;
}

div.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #182230 !important;
    border: 2px solid #096b65 !important;
    border-radius: 10px !important;
    min-height: 48px;
}

div.stButton > button[kind="secondary"] p {
    color: #182230 !important;
    -webkit-text-fill-color: #182230 !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

div.stButton > button[kind="secondary"]:hover {
    background: #e5f4f0 !important;
}

[data-testid="stLinkButton"] a,
[data-testid="stDownloadButton"] button {
    background: #ffffff;
    color: #182230;
    border: 1px solid #bac8d0;
    border-radius: 8px;
}

[data-testid="stLinkButton"] a p,
[data-testid="stDownloadButton"] button p {
    color: #182230 !important;
}

[data-testid="stMetricValue"] {
    color: #096b65;
}

/* Expandable sections */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #b8c9c3 !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary {
    background: #e8f4ef !important;
    color: #182230 !important;
    border-radius: 10px !important;
}

[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary svg {
    color: #182230 !important;
    -webkit-text-fill-color: #182230 !important;
}

[data-testid="stExpander"] summary:hover {
    background: #d9ede5 !important;
}

/* Notes popup */
[data-testid="stPopoverBody"] {
    background: #ffffff !important;
    color: #182230 !important;
    border: 1px solid #b8c9c3 !important;
    border-radius: 12px !important;
}

[data-testid="stPopoverBody"] p,
[data-testid="stPopoverBody"] label,
[data-testid="stPopoverBody"] span {
    color: #182230 !important;
    -webkit-text-fill-color: #182230 !important;
}

[data-testid="stPopoverBody"] textarea {
    background: #ffffff !important;
    color: #182230 !important;
    -webkit-text-fill-color: #182230 !important;
}

/* Job platform buttons */
.job-platform {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    min-height: 56px;
    padding: 10px 14px;
    border-radius: 12px;
    color: #ffffff !important;
    text-decoration: none !important;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 15px;
    font-weight: 700;
    box-shadow: 0 3px 8px rgba(24, 34, 48, 0.12);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.job-platform:hover {
    color: #ffffff !important;
    transform: translateY(-3px);
    box-shadow: 0 6px 14px rgba(24, 34, 48, 0.2);
}

.job-platform:focus-visible {
    outline: 3px solid #182230;
    outline-offset: 3px;
}

.job-platform-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    flex-shrink: 0;
    border-radius: 7px;
    background: #ffffff;
    font-size: 13px;
    font-weight: 800;
}

.job-linkedin { background: #0a66c2; }
.job-indeed { background: #164081; }
.job-dice { background: #ad2029; }
.job-glassdoor { background: #087a50; }
.job-ziprecruiter { background: #426b10; }

.job-linkedin .job-platform-icon { color: #0a66c2; }
.job-indeed .job-platform-icon { color: #164081; }
.job-dice .job-platform-icon { color: #ad2029; }
.job-glassdoor .job-platform-icon { color: #087a50; }
.job-ziprecruiter .job-platform-icon { color: #426b10; }

/* Learning topic badge */
.learning-topic {
    display: inline-block;
    padding: 5px 11px;
    border-radius: 20px;
    background: #e5f4ee;
    color: #096b65;
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 10px;
}

@media (max-width: 600px) {
    .brand {
        padding: 18px 175px 18px 14px !important;
        font-size: 11px !important;
        letter-spacing: 0.4px !important;
    }

    .st-key-provider_header {
        top: 10px;
        right: 8px;
        padding: 4px;
    }

    .st-key-provider_header [data-testid="stRadio"] > div {
        gap: 6px;
    }

    .st-key-provider_header label p {
        font-size: 12px !important;
    }

    .st-key-notes_header {
        top: 75px;
        right: 10px;
    }

    .hero { padding-top: 16px; }
    .journey { font-size: 14px; }
}

@media (prefers-reduced-motion: reduce) {
    .motivation-card,
    .hero h1,
    .hero h1 .briefcase {
        animation: none;
    }

    .job-platform {
        transition: none;
    }

    .job-platform:hover {
        transform: none;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


def show_items(items, empty_message="No items identified."):
    if not items:
        st.caption(empty_message)

    for item in items:
        st.write(f"• {item}")


def learning_widget_key(topic, key_prefix):
    return f"{key_prefix}_website_{topic}"


def matched_learning_resources(skill_gaps):
    """Match review feedback to topics in the fixed learning catalog."""
    matches = []

    for topic, resource in LEARNING_RESOURCES.items():
        matching_gaps = [
            gap
            for gap in skill_gaps
            if re.search(
                resource["pattern"],
                gap,
                re.IGNORECASE,
            )
        ]

        if matching_gaps:
            matches.append((topic, resource, matching_gaps))

    return matches


def selected_learning_website(topic, resource, key_prefix):
    websites = resource["websites"]

    selected = st.session_state.get(
        learning_widget_key(topic, key_prefix)
    )

    if selected not in websites:
        selected = next(iter(websites))

    return selected, websites[selected]


def show_learning_resource(
    topic,
    resource,
    matching_gaps=None,
    key_prefix="library",
):
    st.markdown(
        f'<div class="learning-topic">{escape(topic)}</div>',
        unsafe_allow_html=True,
    )

    if matching_gaps:
        st.write("**Why this was suggested**")
        show_items(matching_gaps)

    st.write("**What to study**")
    st.write(resource["focus"])

    websites = resource["websites"]

    chosen_website = st.selectbox(
        "Choose a learning website",
        options=list(websites),
        key=learning_widget_key(topic, key_prefix),
    )

    st.link_button(
        f"Open {chosen_website} ↗",
        websites[chosen_website],
        use_container_width=True,
    )

    st.write("**Practice project idea**")
    st.write(resource["project"])

    st.caption(
        "After completing the work, add your actual contribution, "
        "tools, and results to your resume, then analyze it again."
    )


def show_role_learning(role, role_index):
    with st.expander("Learn missing skills"):
        st.caption(
            "These suggestions relate to evidence not demonstrated clearly "
            "in your resume. You may already know the skill."
        )

        matches = matched_learning_resources(
            role.get("skill_gaps", [])
        )

        if not matches:
            st.write(
                "No matching topic was found in the current learning "
                "library. Use Browse learning resources below to "
                "choose a topic."
            )
            return

        for index, (topic, resource, gaps) in enumerate(matches):
            if index:
                st.divider()

            show_learning_resource(
                topic,
                resource,
                matching_gaps=gaps,
                key_prefix=f"role_{role_index}",
            )


def job_links(role, location, job_type):
    suffix = {
        "All types": "",
        "Full-time": " full time",
        "Internship": " internship",
        "Contract": " contract",
    }[job_type]

    query = role + suffix

    return {
        "LinkedIn": (
            "https://www.linkedin.com/jobs/search/?"
            + urlencode({
                "keywords": query,
                "location": location,
            })
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
            + urlencode({
                "sc.keyword": " ".join(
                    filter(None, [query, location])
                )
            })
        ),
        "ZipRecruiter": (
            "https://www.ziprecruiter.com/jobs-search?"
            + urlencode({
                "search": query,
                "location": location,
            })
        ),
    }


def show_job_buttons(links):
    for names in [
        ["LinkedIn", "Indeed", "Dice"],
        ["Glassdoor", "ZipRecruiter"],
    ]:
        columns = st.columns(len(names))

        for column, name in zip(columns, names):
            css_class, icon = PLATFORM_STYLES[name]

            with column:
                st.markdown(
                    f'<a class="job-platform {css_class}" '
                    f'href="{escape(links[name], quote=True)}" '
                    f'target="_blank" rel="noopener noreferrer">'
                    f'<span class="job-platform-icon">{icon}</span>'
                    f'<span>Search {name}</span>'
                    f'</a>',
                    unsafe_allow_html=True,
                )


def make_report(result, notes=""):
    score = result["ats_score"]

    score_text = (
        f"{score}/100"
        if score is not None
        else "Not assessed"
    )

    lines = [
        BRAND,
        "RESUME REVIEW",
        "",
        result["summary"],
        "",
        "ESTIMATED ATS READINESS — TEXT ONLY",
        f"Score: {score_text}",
        f"Rating: {result['ats_label']}",
        "App-defined estimate; not an employer's ATS score.",
        "",
    ]

    for item in result["score_categories"]:
        lines.extend([
            f"{item['name']}: {item['rating']}/5",
            f"Evidence: {item['evidence']}",
            f"Improve: {item['improvement']}",
            "",
        ])

    lines.append("PRIORITY IMPROVEMENTS")

    for item in result["top_improvements"]:
        lines.extend([
            item["issue"],
            f"Evidence: {item['resume_evidence']}",
            f"Action: {item['suggested_action']}",
            "",
        ])

    for title, field in [
        ("STRENGTHS", "strengths"),
        ("READABILITY", "readability_notes"),
    ]:
        lines.append(title)
        lines.extend(f"- {item}" for item in result[field])
        lines.append("")

    lines.append("BULLET SUGGESTIONS")

    for item in result["bullet_suggestions"]:
        lines.extend([
            f"Original: {item['original']}",
            f"Suggested: {item['improved']}",
            f"Clarification: {item['clarification_needed'] or 'None'}",
            "",
        ])

    lines.append("ROLES TO EXPLORE")

    for role_index, role in enumerate(result["recommended_roles"]):
        lines.extend([
            f"{role['role']} — {role['fit']}",
            role["reason"],
            "Evidence: " + "; ".join(role["resume_evidence"]),
            "Skills to strengthen or demonstrate: "
            + "; ".join(role["skill_gaps"]),
            "",
        ])

        matches = matched_learning_resources(role["skill_gaps"])

        if matches:
            lines.append("LEARN AND BUILD")

        for topic, resource, gaps in matches:
            website_name, website_url = selected_learning_website(
                topic,
                resource,
                key_prefix=f"role_{role_index}",
            )

            lines.extend([
                f"Topic: {topic}",
                "Related feedback: " + "; ".join(gaps),
                f"Study: {resource['focus']}",
                f"Selected website: {website_name}",
                f"Link: {website_url}",
                f"Practice idea: {resource['project']}",
                "",
            ])

    match = result["job_match"]

    lines.extend([
        "JOB COMPARISON",
        match["summary"],
    ])

    for title, field in [
        ("Matches", "matching_requirements"),
        ("Not shown", "requirements_not_shown"),
        ("Suggested changes", "suggested_changes"),
    ]:
        lines.append(title)
        lines.extend(f"- {item}" for item in match[field])
        lines.append("")

    lines.extend([
        "Review AI suggestions for accuracy before using them.",
        "Visual formatting and actual ATS behavior were not assessed.",
        "Learning topics are matched to review text using a fixed catalog.",
        "Practice ideas are suggestions, not completed achievements.",
    ])

    if notes.strip():
        lines.extend([
            "",
            "MY NOTES",
            notes.strip(),
        ])

    return "\n".join(lines)


def display_results(result, location, job_type, job_description):
    st.divider()
    st.header("Your resume. Your next steps.")
    st.write(result["summary"])

    if not result["is_resume"]:
        st.warning(
            "Add a more complete resume to receive a score "
            "and role suggestions."
        )

    score_tab, improve_tab, apply_tab, match_tab = st.tabs([
        "Readiness Score",
        "Improve My Resume",
        "Find Jobs",
        "Job Match",
    ])

    with score_tab:
        score = result["ats_score"]

        if score is None:
            st.info(
                "Not enough resume evidence to assign a score."
            )

        else:
            score_col, explanation_col = st.columns([1, 2])

            with score_col:
                st.metric(
                    "Estimated ATS Readiness",
                    f"{score}/100",
                )

                st.write(f"**{result['ats_label']}**")

                st.progress(
                    max(0.0, min(float(score) / 100, 1.0))
                )

            with explanation_col:
                st.write(
                    "Your score reflects resume completeness, skills clarity, "
                    "experience and project evidence, and bullet clarity."
                )

                with st.expander("About this score"):
                    st.caption(
                        "This is our app's text-based estimate, not an "
                        "employer's ATS score. Visual layout is not assessed. "
                        "AI ratings can vary between runs."
                    )

                    st.write(
                        "Four categories are rated 0–5. "
                        "Each contributes up to 25 points."
                    )

                    st.table({
                        "Score": [
                            "0–69",
                            "70–84",
                            "85–90",
                            "91–100",
                        ],
                        "Label": [
                            "Needs major improvement",
                            "Average",
                            "Good",
                            "Strong",
                        ],
                    })

            for item in result["score_categories"]:
                with st.container(border=True):
                    st.write(
                        f"**{item['name']} · {item['rating']}/5**"
                    )
                    st.write(item["evidence"])
                    st.write("**How to improve**")
                    st.write(item["improvement"])

    with improve_tab:
        st.subheader("Your priority improvements")

        for index, item in enumerate(
            result["top_improvements"],
            start=1,
        ):
            with st.container(border=True):
                st.write(f"**{index}. {item['issue']}**")
                st.write(item["suggested_action"])

                with st.expander("Evidence from your resume"):
                    st.write(item["resume_evidence"])

        st.subheader("What’s working well")
        show_items(result["strengths"])

        with st.expander("Readability and completeness"):
            show_items(result["readability_notes"])

        st.subheader("Make your bullet points clearer")

        if not result["bullet_suggestions"]:
            st.caption(
                "Not enough detail was available for bullet rewrites."
            )

        for item in result["bullet_suggestions"]:
            with st.container(border=True):
                st.write("**Original**")
                st.write(item["original"])

                st.write("**Suggested wording**")
                st.write(item["improved"])

                if item["clarification_needed"]:
                    st.info(item["clarification_needed"])

        with st.expander("Check the extracted resume text"):
            st.text_area(
                "Text read from your document",
                value=st.session_state.get("review_text", ""),
                height=250,
                disabled=True,
            )

    with apply_tab:
        st.subheader("Explore roles that fit your experience")
        st.caption(
            "Review your next steps, build skills, and search for openings."
        )

        with st.expander("Search tips"):
            st.write(
                "Change location or job type above without generating "
                "the review again. These buttons open keyword searches; "
                "confirm filters and requirements on each platform."
            )

        for role_index, role in enumerate(
            result["recommended_roles"]
        ):
            with st.container(border=True):
                st.subheader(role["role"])
                st.caption(role["fit"])
                st.write(role["reason"])

                with st.expander("Evidence and next steps"):
                    st.write("**Evidence from your resume**")
                    show_items(role["resume_evidence"])

                    st.write(
                        "**Skills or experience to strengthen "
                        "or demonstrate**"
                    )

                    show_items(
                        role["skill_gaps"],
                        "No specific gaps identified; review each listing.",
                    )

                show_role_learning(role, role_index)

                st.write("**Find openings**")

                links = job_links(
                    role["role"],
                    location.strip(),
                    job_type,
                )

                show_job_buttons(links)

        if not result["recommended_roles"]:
            st.info(
                "No supported role recommendations were generated."
            )

        st.caption(
            "Applications are completed on the selected platform."
        )

    with match_tab:
        match = result["job_match"]

        st.subheader("Compare with your target job")
        st.write(match["summary"])

        if job_description.strip():
            st.write("**Matching requirements**")
            show_items(match["matching_requirements"])

            st.write(
                "**Requirements not shown in the resume**"
            )

            st.caption(
                "Missing evidence does not prove you lack the skill."
            )

            show_items(match["requirements_not_shown"])

            st.write("**Suggested changes**")
            show_items(match["suggested_changes"])

    st.divider()

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


def sample_result():
    return {
        "is_resume": True,
        "summary": (
            "SAMPLE PREVIEW: This example shows how a resume review, "
            "role suggestions, and learning resources will appear."
        ),
        "ats_score": 70,
        "ats_label": "Average",
        "score_categories": [
            {
                "name": "Section completeness",
                "rating": 3,
                "evidence": (
                    "The sample includes education, skills, and a project."
                ),
                "improvement": (
                    "Add contact information and more project details."
                ),
            },
            {
                "name": "Skills clarity",
                "rating": 4,
                "evidence": (
                    "Python, SQL, and Excel are listed clearly."
                ),
                "improvement": (
                    "Explain how these skills were used in a project."
                ),
            },
            {
                "name": "Experience and project evidence",
                "rating": 3,
                "evidence": (
                    "The sample mentions building a Python dashboard."
                ),
                "improvement": (
                    "Describe what the dashboard analyzed and your role."
                ),
            },
            {
                "name": "Bullet clarity",
                "rating": 4,
                "evidence": (
                    "The project description identifies an action and tools."
                ),
                "improvement": (
                    "Add the purpose of the dashboard if known."
                ),
            },
        ],
        "strengths": [
            "Lists relevant data skills: Python, SQL, and Excel.",
            "Includes a hands-on dashboard project.",
        ],
        "top_improvements": [
            {
                "issue": "Describe the dashboard in more detail",
                "resume_evidence": (
                    "Built a dashboard using Python and CSV data."
                ),
                "suggested_action": (
                    "Explain what the dashboard displayed and how you "
                    "prepared the data. Add outcomes only if they are true."
                ),
            },
            {
                "issue": "Add contact information",
                "resume_evidence": (
                    "No contact details are shown in the sample."
                ),
                "suggested_action": (
                    "Add a professional email and a LinkedIn or "
                    "portfolio link if available."
                ),
            },
        ],
        "readability_notes": [
            "Use clear section headings such as Education, Skills, and Projects."
        ],
        "recommended_roles": [
            {
                "role": "Junior Data Analyst",
                "fit": "Target now",
                "reason": (
                    "Python, SQL, Excel, and the dashboard project "
                    "provide a starting point for entry-level roles."
                ),
                "resume_evidence": [
                    "Python, SQL, and Excel",
                    "Dashboard project using CSV data",
                ],
                "skill_gaps": [
                    "Add more detail about data cleaning and analysis.",
                    "Demonstrate SQL joins in a completed project.",
                ],
            },
            {
                "role": "Data Scientist",
                "fit": "Work toward",
                "reason": (
                    "The sample shows a computing and data foundation. "
                    "More evidence of statistics and machine learning "
                    "would help."
                ),
                "resume_evidence": [
                    "Computer Science education",
                    "Python project",
                ],
                "skill_gaps": [
                    "Build a project that demonstrates model evaluation.",
                    "Show applied statistics experience.",
                ],
            },
        ],
        "bullet_suggestions": [
            {
                "original": (
                    "Built a dashboard using Python and CSV data."
                ),
                "improved": (
                    "Built a dashboard using Python to display "
                    "information from CSV data."
                ),
                "clarification_needed": (
                    "What information did the dashboard show?"
                ),
            }
        ],
        "job_match": {
            "summary": (
                "Sample preview: paste a job description "
                "for an actual comparison."
            ),
            "matching_requirements": [],
            "requirements_not_shown": [],
            "suggested_changes": [],
        },
    }


# Show the analyzer only after sign-in or guest access.
require_login()


st.markdown(
    f'<div class="brand">{BRAND}</div>',
    unsafe_allow_html=True,
)

# Ollama is disabled unless explicitly enabled for local development.
allow_ollama = (
    os.getenv("ENABLE_OLLAMA", "false").strip().lower()
    == "true"
)

provider_options = (
    ["Gemini", "Ollama"]
    if allow_ollama
    else ["Gemini"]
)

# Clear an older Ollama selection when it is unavailable.
if st.session_state.get("selected_provider") not in provider_options:
    st.session_state["selected_provider"] = "Gemini"

with st.container(key="provider_header"):
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
        st.markdown("**Gemini**")

ollama_model = "qwen2.5:3b"


with st.container(key="notes_header"):
    with st.popover("📝 My Notes"):
        st.text_area(
            "Write your notes",
            placeholder=(
                "Write reminders, ideas, or next steps here..."
            ),
            height=160,
            key="personal_review_notes",
        )

        st.caption(
            "Your notes will be included when you download your review."
        )


st.markdown(
    """
<div class="hero">
<div class="eyebrow">YOUR NEXT CHAPTER STARTS HERE</div>
<h1>GOOD RESUME FINDS <span class="highlight">GREAT ROLES</span> <span class="briefcase">💼</span></h1>
<p>Build a stronger resume and explore your next opportunity.</p>
</div>
<div class="motivation-strip" aria-label="Motivation">
<div class="motivation-card">It's still day one</div>
<div class="motivation-card">Every search counts</div>
<div class="motivation-card">Never give up</div>
<div class="motivation-card">Your search matters</div>
<div class="motivation-card">Your life and skills are valuable</div>
<div class="motivation-card">Every rejection can lead to a better opportunity</div>
<div class="motivation-card">Success isn't always an easy journey</div>
</div>
<div class="journey">
<strong>01 · Review</strong> &nbsp; / &nbsp;
<strong>02 · Learn</strong> &nbsp; / &nbsp;
<strong>03 · Build</strong> &nbsp; / &nbsp;
<strong>04 · Apply</strong>
</div>
""",
    unsafe_allow_html=True,
)


left, right = st.columns([1.1, 1], gap="large")


with left:
    with st.container(border=True):
        st.subheader("Start with your resume")

        st.caption(
            "Upload a PDF or Word document, or paste the text."
        )

        method = st.radio(
            "Resume source",
            ["Upload file", "Paste text"],
            horizontal=True,
        )

        uploaded_file = None
        resume_text = ""

        if method == "Upload file":
            uploaded_file = st.file_uploader(
                "Choose your resume",
                type=["pdf", "docx"],
            )

            st.caption(
                "Accepted files: text-based PDF or DOCX · Maximum 10 MB"
            )

        else:
            resume_text = st.text_area(
                "Paste your resume",
                height=260,
                placeholder=(
                    "Education, skills, experience, projects..."
                ),
            )

    with st.expander("Tell us more about your background"):
        additional_projects = st.text_area(
            "Completed projects",
            placeholder=(
                "Describe projects not included in your resume. "
                "What did you build, and which tools did you use?"
            ),
        )

        additional_courses = st.text_area(
            "Relevant courses",
            placeholder=(
                "List your courses and any related hands-on work."
            ),
        )


with right:
    with st.container(border=True):
        st.subheader("Where do you want to go?")
        st.caption("These details are optional.")

        target_role = st.text_input(
            "Target role",
            placeholder="For example: Data Analyst",
        )

        location = st.text_input(
            "Preferred location",
            placeholder="For example: Oklahoma City or Remote",
        )

        job_type = st.selectbox(
            "Job type",
            [
                "All types",
                "Full-time",
                "Internship",
                "Contract",
            ],
        )

        job_description = st.text_area(
            "Job description",
            height=120,
            placeholder=(
                "Paste a job description to compare requirements."
            ),
        )


file_digest = (
    hashlib.sha256(uploaded_file.getvalue()).hexdigest()
    if uploaded_file is not None
    else None
)

input_signature = (
    method,
    file_digest,
    resume_text,
    target_role,
    job_description,
    additional_projects,
    additional_courses,
)

review_version = 4

if (
    st.session_state.get("review_signature") != input_signature
    or st.session_state.get("review_version") != review_version
):
    st.session_state.pop("review_result", None)
    st.session_state.pop("review_text", None)

    # Clear learning selections belonging to the previous review.
    for state_key in list(st.session_state):
        if state_key.startswith("role_") and "_website_" in state_key:
            del st.session_state[state_key]

    st.session_state["review_signature"] = input_signature
    st.session_state["review_version"] = review_version


has_resume = (
    uploaded_file is not None
    or bool(resume_text.strip())
)


with st.expander("Privacy details"):
    if provider == "Gemini":
        st.caption(
            "Your resume, optional job details, projects, and courses "
            "are sent to Google Gemini for analysis."
        )
    else:
        st.caption(
            "Your resume, optional job details, projects, and courses "
            "are processed by Ollama on the computer running this app."
        )


clicked = st.button(
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
    st.session_state["review_text"] = (
        "Sample Candidate\n"
        "Education: Bachelor's in Computer Science\n"
        "Skills: Python, SQL, Excel\n"
        "Project: Built a dashboard using Python and CSV data."
    )

    st.session_state["review_result"] = sample_result()


if clicked:
    st.session_state.pop("review_result", None)
    st.session_state.pop("review_text", None)

    try:
        if (
            uploaded_file is not None
            and uploaded_file.size > 10 * 1024 * 1024
        ):
            raise ValueError(
                "Please upload a resume smaller than 10 MB."
            )

        with st.spinner("Reading your resume..."):
            text = (
                extract_resume_text(uploaded_file)
                if uploaded_file is not None
                else resume_text.strip()
            )

        if not text or not text.strip():
            raise ValueError(
                "Please upload a readable resume or paste its text."
            )

        st.session_state["review_text"] = text

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

        required_fields = {
            "summary",
            "is_resume",
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
                "The analyzer returned an older result format. "
                "Save the latest ai_analyzer.py and restart Streamlit."
            )

        st.session_state["review_result"] = analysis

    except ValueError as error:
        st.error(str(error))


result = st.session_state.get("review_result")

if result:
    display_results(
        result,
        location,
        job_type,
        job_description,
    )


st.divider()


with st.expander("Browse learning resources"):
    st.write(
        "Choose a topic, select your preferred learning website, "
        "and explore a practice project."
    )

    topic = st.selectbox(
        "What would you like to learn?",
        options=list(LEARNING_RESOURCES),
        key="learning_library_topic",
    )

    show_learning_resource(
        topic,
        LEARNING_RESOURCES[topic],
        key_prefix="library",
    )

    st.caption(
        "Some websites also offer paid certificates or labs. "
        "Check the selected resource before enrolling."
    )


st.caption(
    f"{BRAND} · Built for students and career changers"
)