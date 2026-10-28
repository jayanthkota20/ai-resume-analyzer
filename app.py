import hashlib
from urllib.parse import urlencode
from html import escape

import streamlit as st

from ai_analyzer import analyze_resume
from resume_parser import extract_resume_text


BRAND = "BUILD AND APPLY THROUGH US"

st.set_page_config(
    page_title=BRAND,
    page_icon="💼",
    layout="wide",
)


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

    /* Fixed app name */

    .brand {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        box-sizing: border-box;
        z-index: 999999;
        background: #ffffff;
        color: #096b65;
        padding: 20px 24px;
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

    /* Floating notes button */

    .st-key-notes_header {
        position: fixed;
        top: 70px;
        right: 24px;
        z-index: 999998;
        width: auto;
    }

    .st-key-notes_header button {
        background-color: #096b65 !important;
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
        0%, 100% {
            transform: translateY(0);
        }

        50% {
            transform: translateY(-6px);
        }
    }

    @keyframes briefcase-float {
        0%, 100% {
            transform: translateY(0) rotate(-4deg);
        }

        50% {
            transform: translateY(-6px) rotate(4deg);
        }
    }

    /* Motivational messages */

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
        from {
            transform: translateY(0);
        }

        to {
            transform: translateY(-7px);
        }
    }

    @media (prefers-reduced-motion: reduce) {
        .motivation-card,
        .hero h1,
        .hero h1 .briefcase {
            animation: none;
        }
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
    [data-testid="stFileUploader"] button p {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    [data-testid="stFileUploader"] button svg {
        color: #ffffff !important;
    }

    [data-testid="stFileUploader"] button:hover {
        background: #07534e !important;
    }

    [data-testid="stFileUploader"] button:focus-visible {
        outline: 3px solid #80cbc4 !important;
        outline-offset: 3px;
    }

    /* Buttons */

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
        background-color: #ffffff !important;
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
        background-color: #e5f4f0 !important;
        border-color: #07534e !important;
    }

    [data-testid="stLinkButton"] a,
    [data-testid="stDownloadButton"] button {
        background: #ffffff;
        color: #182230;
        border: 1px solid #bac8d0;
        border-radius: 8px;
    }

    [data-testid="stMetricValue"] {
        color: #096b65;
    }

    /* Expandable sections */

    [data-testid="stExpander"] {
        background-color: #ffffff !important;
        border: 1px solid #b8c9c3 !important;
        border-radius: 12px !important;
    }

    [data-testid="stExpander"] summary {
        background-color: #e8f4ef !important;
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
        background-color: #d9ede5 !important;
    }

    /* Smaller screens */

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

        .hero {
            padding-top: 16px;
        }

        .journey {
            font-size: 14px;
        }
    }
    /* Make the My Notes popup readable */
[data-testid="stPopoverBody"] {
    background-color: #ffffff !important;
    color: #182230 !important;
    border: 1px solid #b8c9c3 !important;
    border-radius: 12px !important;
}

/* Notes label and helper text */
[data-testid="stPopoverBody"] p,
[data-testid="stPopoverBody"] label,
[data-testid="stPopoverBody"] span {
    color: #182230 !important;
    -webkit-text-fill-color: #182230 !important;
}

/* Notes writing area */
[data-testid="stPopoverBody"] textarea {
    background-color: #ffffff !important;
    color: #182230 !important;
    -webkit-text-fill-color: #182230 !important;
    border: 1px solid #98a2b3 !important;
}

[data-testid="stPopoverBody"] textarea::placeholder {
    color: #526174 !important;
    -webkit-text-fill-color: #526174 !important;
}
/* Job search buttons */
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

.job-linkedin {
    background: #0a66c2;
}

.job-indeed {
    background: #164081;
}

.job-dice {
    background: #ad2029;
}

.job-glassdoor {
    background: #087a50;
}

.job-ziprecruiter {
    background: #426b10;
}

.job-linkedin .job-platform-icon {
    color: #0a66c2;
}

.job-indeed .job-platform-icon {
    color: #164081;
}

.job-dice .job-platform-icon {
    color: #ad2029;
}

.job-glassdoor .job-platform-icon {
    color: #087a50;
}

.job-ziprecruiter .job-platform-icon {
    color: #426b10;
}

@media (prefers-reduced-motion: reduce) {
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
            + urlencode({
                "q": query,
                "l": location,
            })
        ),
        "Dice": (
            "https://www.dice.com/jobs?"
            + urlencode({
                "q": query,
                "location": location,
            })
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


def make_report(result, notes=""):
    score = result["ats_score"]

    if score is not None:
        score_text = f"{score}/100"
    else:
        score_text = "Not assessed"

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

    for role in result["recommended_roles"]:
        lines.extend([
            f"{role['role']} — {role['fit']}",
            role["reason"],
            "Evidence: " + "; ".join(role["resume_evidence"]),
            "Gaps: " + "; ".join(role["skill_gaps"]),
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

        if score is not None:
            score_col, explanation_col = st.columns([1, 2])

            with score_col:
                st.metric(
                    "Estimated ATS Readiness",
                    f"{score}/100",
                )

                st.write(f"**{result['ats_label']}**")
                st.progress(score / 100)

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

        else:
            st.info(
                "Not enough resume evidence to assign a score."
            )

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
            "Choose a platform to find openings and apply."
        )

        with st.expander("Search tips"):
            st.write(
                "Change location or job type above without generating "
                "the review again. These buttons open keyword searches; "
                "confirm the filters and requirements on each platform. "
                "Some platforms may require sign-in."
            )

        for role in result["recommended_roles"]:
            with st.container(border=True):
                st.subheader(role["role"])
                st.caption(role["fit"])
                st.write(role["reason"])

                with st.expander("Evidence and next steps"):
                    st.write("**Evidence from your resume**")
                    show_items(role["resume_evidence"])

                    st.write(
                        "**Skills or experience to strengthen**"
                    )

                    show_items(
                        role["skill_gaps"],
                        "No specific gaps identified; review each listing.",
                    )

                links = job_links(
                    role["role"],
                    location.strip(),
                    job_type,
                )

            platform_styles = {
            "LinkedIn": ("job-linkedin", "in"),
            "Indeed": ("job-indeed", "I"),
            "Dice": ("job-dice", "D"),
            "Glassdoor": ("job-glassdoor", "G"),
            "ZipRecruiter": ("job-ziprecruiter", "Z"),
            }

            for names in [
            ["LinkedIn", "Indeed", "Dice"],
            ["Glassdoor", "ZipRecruiter"],
            ]:
             columns = st.columns(len(names))

    for column, name in zip(columns, names):
        css_class, icon = platform_styles[name]

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

    notes = st.session_state.get(
        "personal_review_notes",
        "",
    )

    st.download_button(
        "Download My Review",
        data=make_report(result, notes),
        file_name="Build_And_Apply_Resume_Review.txt",
        mime="text/plain",
        use_container_width=True,
    )


# Fixed brand name and AI provider selector

st.markdown(
    f'<div class="brand">{BRAND}</div>',
    unsafe_allow_html=True,
)

with st.container(key="provider_header"):
    provider = st.radio(
        "AI provider",
        ["Ollama", "Gemini"],
        horizontal=True,
        label_visibility="collapsed",
        key="selected_provider",
    )

ollama_model = "qwen2.5:3b"


# Notes button stays visible while scrolling

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


# Hero and motivation cards

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
        <strong>01 · Add your resume</strong>
        &nbsp; / &nbsp;
        <strong>02 · Understand your strengths</strong>
        &nbsp; / &nbsp;
        <strong>03 · Find opportunities</strong>
    </div>
    """,
    unsafe_allow_html=True,
)


left, right = st.columns([1.1, 1], gap="large")


# Resume and background

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
                "Describe projects that are not included in your resume. "
                "What did you build, and which tools did you use?"
            ),
        )

        additional_courses = st.text_area(
            "Relevant courses",
            placeholder=(
                "List your courses and any related hands-on work."
            ),
        )


# Career goals

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


# Reset old results when resume-related inputs change

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

review_version = 2

if (
    st.session_state.get("review_signature") != input_signature
    or st.session_state.get("review_version") != review_version
):
    st.session_state.pop("review_result", None)
    st.session_state.pop("review_text", None)

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
            "are processed by Ollama on this computer."
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


# Sample preview

if preview_clicked:
    st.session_state["review_text"] = (
        "Sample Candidate\n"
        "Education: Bachelor's in Computer Science\n"
        "Skills: Python, SQL, Excel\n"
        "Project: Built a dashboard using Python and CSV data."
    )

    st.session_state["review_result"] = {
        "is_resume": True,

        "summary": (
            "SAMPLE PREVIEW: This example shows how a resume review "
            "and role suggestions will appear."
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
                    "Check individual job requirements for visualization tools.",
                ],
            },
            {
                "role": "Data Scientist",
                "fit": "Work toward",
                "reason": (
                    "The sample shows a computing and data foundation. "
                    "More evidence of statistics and machine learning would help."
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
                    "Built a dashboard using Python to display information "
                    "from CSV data."
                ),
                "clarification_needed": (
                    "What information did the dashboard show?"
                ),
            }
        ],

        "job_match": {
            "summary": (
                "Sample preview: paste a job description for an actual "
                "comparison."
            ),
            "matching_requirements": [],
            "requirements_not_shown": [],
            "suggested_changes": [],
        },
    }


# Analyze the user's resume

if clicked:
    st.session_state.pop("review_result", None)
    st.session_state.pop("review_text", None)

    try:
        with st.spinner("Reading your resume..."):
            if uploaded_file is not None:
                text = extract_resume_text(uploaded_file)
            else:
                text = resume_text.strip()

        if not text:
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

st.caption(
    f"{BRAND} · Built for students and career changers"
)