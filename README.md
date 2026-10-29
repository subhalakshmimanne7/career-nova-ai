# Career Nova AI — Intelligent Career Guidance Platform

> **A full-stack, college-level AI/ML career platform** designed for engineering students to identify suitable career roles, analyze technical skill gaps with transparent mathematical scoring, optimize resumes for ATS screening, and execute personalized 30, 60, and 90-day learning roadmaps.

---

## 🚀 Key Features

1. **AI Career Recommendation System**
   - Uses **Scikit-learn TF-IDF Vectorization** and **Cosine Similarity** to compute semantic document matching between the student's profile and industry standards.
   - Combines TF-IDF scores with **NumPy-weighted skill vector coverage** to generate honest match percentages.
   - Provides clear algorithmic disclaimers separating match estimates from guaranteed employment outcomes.

2. **AI Skill Gap Analyzer (Flagship Feature)**
   - Allows students to select any target tech career (e.g., *Machine Learning Engineer, Data Scientist, Full Stack Developer, Cybersecurity Analyst*).
   - Identifies and categorizes:
     - **Mastered Skills** (demonstrated in profile)
     - **Needs Improvement** (beginner / foundational skills)
     - **Missing Skills** (complete gaps)
     - **Priority Skills to Learn First** (high-weight skills >= 4)
     - **Suggested Hands-on Capstone Projects** with estimated completion hours.
   - Transparent scoring formula:
     $$\text{Skill Coverage Score} = \left( \frac{\sum \text{Demonstrated Weighted Points}}{\sum \text{Required Weighted Points}} \right) \times 100$$

3. **Personalized 30, 60, and 90-Day Roadmaps**
   - Dynamic phase-wise breakdown: Sprint (30-day), Deep Dive (60-day), or Mastery (90-day).
   - Weekly tasks, focus topics, milestone benchmarks, and **curated official documentation links** (Python.org, MDN, Scikit-learn docs, PyTorch, FreeCodeCamp).
   - **Interactive checkboxes** with live database persistence of completion percentages.

4. **ATS Resume Analyzer**
   - Untrusted file upload supporting `.pdf` (via `pypdf`) and `.docx` (via `python-docx`) up to 5MB.
   - Automated text extraction, contact detection, section completeness analysis, action verb frequency, and quantifiable impact checks.
   - Role keyword comparison against the `career_skills.csv` dataset with targeted bullet revision recommendations.

5. **Company Readiness Dashboard**
   - Configurable benchmarks for **Google**, **Microsoft**, **Amazon**, and **Top Tech Startups**.
   - Calculates an indicative preparation score using NumPy.
   - Provides culture alignment notes and preparation checklists.

6. **Student Analytics Dashboard**
   - Interactive data visualizations with **Recharts** (Radar Chart for domain category coverage, Bar Chart for matched vs. total skills).
   - Live KPI widgets: Skill Coverage %, Identified Skills, Active Roadmap Progress %, Remaining Gaps.

7. **Pandas & NumPy Dataset Analytics Demonstration**
   - Dedicated demonstration page powered by `analytics.py`.
   - Real-time dataset statistics: total roles, total unique skills, average skills per role, top 10 most in-demand skills, and NumPy histogram weight distributions.
   - Universal missing skill calculator identifying the most widely needed tech skills.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, Vite, Tailwind CSS, Lucide React Icons, Recharts |
| **Backend API** | Python 3.14 / 3.11+, Flask REST API, Flask-CORS, Flask-SQLAlchemy |
| **Data Science & ML** | NumPy (matrix & vectorized math), Pandas (data wrangling & aggregation), Scikit-learn (TF-IDF & Cosine Similarity) |
| **Document Parsers** | PyPDF (`pypdf`), Python-Docx (`python-docx`), Regex |
| **Database** | SQLite3 (zero-configuration local fallback) / MySQL (production-ready via SQLAlchemy) |
| **AI Integration** | Optional Gemini / OpenAI API integration with built-in rule-based expert engine fallback |

---

## 📂 Project Folder Structure

```
career-nova-ai final/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx               # Navigation bar with responsive mobile menu
│   │   │   ├── Sidebar.jsx              # Dashboard sidebar navigation
│   │   │   ├── Footer.jsx               # Footer with links, tech stack, and disclosures
│   │   │   └── DisclaimerBanner.jsx     # Algorithmic transparency notice
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx          # Public landing page with hero and features
│   │   │   ├── LoginPage.jsx            # Sign in with 1-Click Demo student login
│   │   │   ├── RegisterPage.jsx         # Student registration & skill profiling
│   │   │   ├── DashboardPage.jsx        # Personalized dashboard with Recharts
│   │   │   ├── CareerRecommendationPage.jsx # Scikit-learn TF-IDF matching
│   │   │   ├── SkillGapPage.jsx         # NumPy-weighted skill gap analyzer
│   │   │   ├── RoadmapPage.jsx          # 30/60/90-day interactive roadmaps
│   │   │   ├── ResumeAnalyzerPage.jsx   # PDF & DOCX ATS resume evaluator
│   │   │   ├── CompanyReadinessPage.jsx # Target company benchmarks
│   │   │   ├── DatasetAnalyticsPage.jsx # Pandas/NumPy dataset demonstration
│   │   │   └── ProfilePage.jsx          # Student profile management
│   │   ├── services/
│   │   │   └── api.js                   # Centralized REST API client
│   │   ├── App.jsx                      # App root router and state
│   │   ├── main.jsx                     # Vite entry point
│   │   └── index.css                    # Tailwind CSS directives
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   ├── .env.example
│   └── .env
│
├── backend/
│   ├── app.py                           # Flask app factory, CORS, demo seeding
│   ├── config.py                        # Configuration and database URI fallback
│   ├── models.py                        # SQLAlchemy User, Assessment, Roadmap models
│   ├── analytics.py                     # Dedicated Pandas & NumPy analytics module
│   ├── career_matcher.py                # Scikit-learn TF-IDF & Cosine Similarity engine
│   ├── resume_analyzer.py               # PDF/DOCX resume parser & ATS scoring
│   ├── roadmap_generator.py             # 30/60/90-day learning curriculum generator
│   ├── services/
│   │   └── llm_service.py               # Optional LLM integration & expert rule fallback
│   ├── routes/
│   │   ├── auth_routes.py               # Register, login, profile endpoints
│   │   ├── career_routes.py             # Roles, recommendations, skill gap, companies
│   │   ├── roadmap_routes.py            # Generate, retrieve, toggle tasks
│   │   ├── resume_routes.py             # Upload, parse, ATS evaluation
│   │   └── analytics_routes.py          # Summary, gap distributions, dashboard stats
│   ├── datasets/
│   │   └── career_skills.csv            # Structured dataset of 10+ career roles & skills
│   ├── tests/
│   │   ├── run_tests.py                 # Standard test runner (unittest)
│   │   └── test_analytics.py            # Comprehensive unit tests
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
└── README.md
```

---

## ⚡ Quick Start Guide (Windows)

### Prerequisites
- **Python 3.10+** (tested and verified with Python 3.14.2)
- **Node.js 18+** (installed LTS version: v24.22.1)

---

### Step 1: Start the Backend Server

Open PowerShell in the project directory:

```powershell
# Navigate to backend directory
cd backend

# (Optional) Verify backend unit tests
py tests/run_tests.py

# Run the Flask backend server
py app.py
```

*The Flask backend will start on **`http://127.0.0.1:5000`**.*
*On initial startup, it automatically creates the SQLite database `career_nova.db` and seeds a demo account.*

---

### Step 2: Start the Frontend Application

Open a **second PowerShell terminal** in the project root:

```powershell
# Navigate to frontend directory
cd frontend

# Start the Vite development server
npm run dev
```

*Open your browser and navigate to: **`http://localhost:5173`**.*

---

## 🔑 Pre-Seeded Demo Student Account

For immediate testing and project demonstrations without filling forms:

- **Email:** `demo@careernova.ai`
- **Password:** `Password123!`
- *Or simply click the **"Quick 1-Click Demo Student Login"** button on the Sign In page.*

Pre-seeded profile skills include:
`Python, SQL, Pandas, NumPy, Git & Version Control, REST APIs, HTML5 & CSS3`

---

## 🧪 Running Unit Tests

To run the automated backend test suite verifying NumPy and Pandas analytics, TF-IDF career matching, resume extraction, and roadmap generation:

```powershell
py backend/tests/run_tests.py
```

Expected output:
```
test_calculate_skill_coverage_and_readiness ... ok
test_career_matcher_recommendations ... ok
test_clean_skill_data ... ok
test_compare_student_skills ... ok
test_convert_skills_to_numerical ... ok
test_generate_analytics_summary ... ok
test_load_and_validate_dataset ... ok
test_resume_analyzer_text ... ok
test_roadmap_generator ... ok
test_summarize_missing_skills_across_roles ... ok
----------------------------------------------------------------------
Ran 10 tests in 0.12s
OK
```

---

## 📡 REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/health` | `GET` | System health check and database status |
| `/api/auth/register` | `POST` | Register a new student account |
| `/api/auth/login` | `POST` | Student login with password hashing check |
| `/api/auth/profile/<id>` | `GET` / `PUT` | Retrieve or update student profile |
| `/api/careers/roles` | `GET` | List all 10+ standardized career roles |
| `/api/careers/recommend` | `POST` | TF-IDF & Cosine Similarity career recommendations |
| `/api/careers/skill-gap` | `POST` | NumPy-weighted skill gap analysis with formula breakdown |
| `/api/careers/company-readiness`| `POST` | Google, Microsoft, Amazon preparation evaluation |
| `/api/roadmap/generate` | `POST` | Generate 30/60/90-day phase-wise roadmaps |
| `/api/roadmap/toggle-task` | `POST` | Mark/unmark tasks as complete (DB persistence) |
| `/api/resume/upload` | `POST` | Upload `.pdf` or `.docx` resume for ATS evaluation |
| `/api/analytics/summary` | `GET` | Pandas summary metrics for dataset demo page |
| `/api/analytics/student-dashboard/<id>` | `GET` | Personalized student analytics and chart metrics |

---

## 🔒 Security & Reliability

- **Password Security:** Salted and hashed using Werkzeug (`scrypt` / `pbkdf2:sha256`). Plaintext passwords are never stored.
- **Untrusted File Validation:** Restricts uploads strictly to `.pdf` and `.docx`, enforcing a 5MB size limit. Files are parsed securely and temporary uploads are safely deleted.
- **CORS Protection:** Configurable origin whitelisting via environment variables.
- **Offline Reliability:** Operates completely without external cloud APIs. When an optional LLM API key (`GEMINI_API_KEY`) is not provided, the intelligent rule-based expert system generates complete advice with zero errors.

---

## 🎓 Academic Demonstration Notes (B.Tech CSE)

1. **Why NumPy?**
   Vectorized boolean masking and sum reductions (`np.sum`, `np.clip`, `np.histogram`) are used to compute weighted readiness scores and statistical binning in microseconds.
2. **Why Pandas?**
   Loads, cleans, deduplicates, and pivots tabular datasets (`pd.pivot_table`, `groupby`, `value_counts`).
3. **Why Scikit-learn?**
   `TfidfVectorizer` and `cosine_similarity` transform natural language skill sets into high-dimensional numerical vectors to discover semantic alignment beyond naive string matching.
