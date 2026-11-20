# Build and Apply Through Us

An AI resume analyzer for students and career changers. Upload a resume, get feedback on how to improve it, and explore job roles and learning resources based on your experience.

[Open the deployed Streamlit app](https://ai-resume-analyzer-3qhzffaih7kb9pdj6sbdkz.streamlit.app/)

## Try it

1. Sign in or continue as a guest.
2. Upload a text-based PDF or DOCX (up to 10 MB), or paste your resume text.
3. Optionally add a target role, job description, projects, or courses.
4. Select **Analyze My Resume**. To see the results layout without uploading anything or calling a model, select **Preview Sample Results**.

The app provides resume strengths, prioritized improvements, suggested bullet rewrites, and role recommendations backed by the information you enter. A job description enables a comparison with its stated requirements. The **Find Jobs** tab opens searches on LinkedIn, Indeed, Dice, Glassdoor, and ZipRecruiter, with location and job-type preferences. Applications are completed on those sites.

You can explore courses and practice projects, take notes, and download your review with those notes included. Verified users can separately save their applicant profile.

## How the score works

The app rates four areas from 0 to 5: section completeness, skills clarity, experience and project evidence, and bullet clarity. The sum is multiplied by five for a score out of 100.

| Score | Label |
| --- | --- |
| 0–69 | Needs major improvement |
| 70–84 | Average |
| 85–90 | Good |
| 91–100 | Strong |

This is an AI estimate based on extracted text. It does not measure visual layout, predict hiring outcomes, or reproduce an employer's ATS. Review suggested rewrites before using them.

## Run locally

From PowerShell:

```powershell
git clone https://github.com/jayanthkota20/ai-resume-analyzer.git
cd ai-resume-analyzer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

To configure live features, add the applicable values to a local `.env` file beside `app.py`. Use the deployed app's Secrets settings for hosted configuration. Keep credentials out of Git.

| Setting | Purpose |
| --- | --- |
| `GEMINI_API_KEY` | Live Gemini analysis |
| `GEMINI_MODEL` | Optional Gemini model override |
| `FIREBASE_API_KEY` | Firebase email/password authentication |
| `FIREBASE_PROJECT_ID` | Firestore project for saved profiles |
| `BREVO_API_KEY`, `WELCOME_SENDER_EMAIL` | Optional welcome email |
| `ENABLE_OLLAMA` | Set to `true` locally to show the Ollama option |

For local Ollama analysis, run Ollama on the machine hosting Streamlit and pull the model the app uses:

```powershell
ollama pull qwen2.5:3b
```

For saved profiles, enable Firestore in the same Firebase project as Authentication. Configure rules so only verified users can access their own `applicant_profiles/{uid}` document.

## Project structure

| File | Purpose |
| --- | --- |
| `app.py` | Streamlit interface, results, job links, learning resources, and downloads |
| `resume_parser.py` | PDF and DOCX text extraction |
| `ai_analyzer.py` | Gemini and local Ollama integration, result validation, and scoring |
| `auth_ui.py`, `firebase_auth.py` | Sign-in, email verification, and session handling |
| `profile_ui.py` | Saved applicant profiles in Firestore |
| `email_service.py` | Optional welcome email via Brevo |

## Data handling

When you choose Gemini, the app sends the extracted resume text and optional analysis inputs to Gemini. When you choose Ollama, those inputs are processed on the machine running the app. Saved profiles are stored separately in Firestore and are not automatically sent to either model. Reviews and notes are kept in the current session; download them to keep a copy.
