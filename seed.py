from database import get_connection


SKILLS = [
    ("Python", "technical"),
    ("JavaScript", "technical"),
    ("SQL", "technical"),
    ("HTML/CSS", "technical"),
    ("Statistics", "technical"),
    ("Machine Learning", "technical"),
    ("Data Visualization", "technical"),
    ("Cloud Computing", "technical"),
    ("Linux", "technical"),
    ("Networking", "technical"),
    ("Cybersecurity Basics", "technical"),
    ("UI Design", "design"),
    ("User Research", "design"),
    ("Figma", "design"),
    ("Communication", "soft"),
    ("Problem Solving", "soft"),
    ("Project Management", "soft"),
    ("Leadership", "soft"),
    ("Writing", "soft"),
    ("Marketing Strategy", "business"),
    ("Excel", "business"),
    ("Product Thinking", "business"),
    ("REST APIs", "technical"),
    ("Git", "technical"),
    ("Public Speaking", "soft"),
]

CAREERS = [
    {
        "title": "Software Engineer",
        "category": "Technology",
        "description": "Design, build, and maintain applications that solve real problems. You will write code, review designs, and ship features with a team.",
        "avg_salary": "$90k–$160k",
        "outlook": "Very strong hiring across industries",
        "education_fit": "Computer Science, IT, Engineering, Mathematics",
        "keywords": "code,build,apps,programming,software,tech,developer",
        "skills": [
            ("Python", "core"),
            ("JavaScript", "core"),
            ("Git", "core"),
            ("SQL", "core"),
            ("REST APIs", "core"),
            ("Problem Solving", "core"),
            ("HTML/CSS", "supporting"),
            ("Communication", "supporting"),
        ],
        "roadmap": [
            (1, "Foundations", "Master programming basics, Git, and problem solving with daily practice.", "freeCodeCamp, CS50, LeetCode Easy"),
            (2, "Build small apps", "Create 3 mini projects using HTML/CSS/JS or Python and publish them on GitHub.", "GitHub, MDN, Flask/Django docs"),
            (3, "Data and APIs", "Learn SQL, REST APIs, and how apps talk to databases.", "SQLBolt, Postman Student Expert"),
            (4, "Team-ready skills", "Practice testing, code reviews, and a full-stack project.", "The Odin Project, internships"),
            (5, "Interview prep", "Study data structures, system basics, and mock interviews.", "NeetCode, Pramp"),
            (6, "Portfolio and applications", "Polish 2–3 projects, write a strong resume, and apply widely.", "LinkedIn, GitHub README guides"),
        ],
        "projects": [
            ("Campus Event Finder", "Beginner", "A web app that lists campus events with filters and a simple admin form.", "HTML/CSS, JavaScript, Git", "Shows you can ship a complete UI."),
            ("Task Tracker API", "Intermediate", "Build a REST API with authentication and a small frontend.", "Python, SQL, REST APIs", "Demonstrates backend thinking."),
            ("Team Collaboration Board", "Advanced", "Kanban-style board with users, comments, and real-time-ish updates.", "JavaScript, SQL, Git", "Portfolio centerpiece for internships."),
        ],
        "interview": [
            ("Walk me through a project you built.", "Use situation, your role, a hard decision, and the result.", "behavioral"),
            ("How do you debug a feature that works locally but fails in production?", "Talk about logs, reproduction, isolation, and rollback.", "technical"),
            ("Explain how a web request travels from browser to database.", "Keep it simple: DNS, HTTP, server, query, response.", "technical"),
        ],
    },
    {
        "title": "Data Scientist",
        "category": "Data",
        "description": "Turn messy data into decisions. You will clean datasets, build models, and explain findings to people who are not data experts.",
        "avg_salary": "$95k–$165k",
        "outlook": "High demand in product, finance, health, and research",
        "education_fit": "Statistics, Mathematics, Computer Science, Economics",
        "keywords": "data,analytics,ml,research,numbers,insights,python",
        "skills": [
            ("Python", "core"),
            ("SQL", "core"),
            ("Statistics", "core"),
            ("Machine Learning", "core"),
            ("Data Visualization", "core"),
            ("Communication", "core"),
            ("Excel", "supporting"),
            ("Problem Solving", "supporting"),
        ],
        "roadmap": [
            (1, "Stats and Python", "Review probability, pandas, and exploratory analysis.", "Kaggle Learn, StatQuest"),
            (2, "SQL fluency", "Write joins, window functions, and business questions in SQL.", "Mode SQL, LeetCode SQL"),
            (3, "Visualization", "Tell stories with charts that a manager can act on.", "Tableau Public, matplotlib"),
            (4, "Machine learning", "Train, evaluate, and avoid leaking data in classical ML models.", "scikit-learn, Google ML Crash Course"),
            (5, "End-to-end case study", "Pick a dataset, define a question, and publish a notebook + write-up.", "Kaggle competitions, Medium"),
            (6, "Stakeholder communication", "Practice presenting findings and answering “so what?” questions.", "Toastmasters, mock case interviews"),
        ],
        "projects": [
            ("Student Dropout Risk Model", "Beginner", "Predict at-risk students from academic and attendance data.", "Python, SQL, Statistics", "Shows applied ML with a social impact story."),
            ("Sales Dashboard", "Intermediate", "Interactive dashboard of monthly trends and cohort retention.", "Data Visualization, Excel, SQL", "Business-friendly portfolio piece."),
            ("NLP Ticket Classifier", "Advanced", "Classify support tickets and measure precision/recall.", "Python, Machine Learning", "Signals production-minded modeling."),
        ],
        "interview": [
            ("How do you know a model is good enough to ship?", "Discuss metrics, baselines, fairness, and business cost of errors.", "technical"),
            ("Tell me about a time data disagreed with a stakeholder’s intuition.", "Show curiosity, not confrontation, and how you verified the numbers.", "behavioral"),
            ("What is data leakage and why does it matter?", "Give a concrete example from training/test split mistakes.", "technical"),
        ],
    },
    {
        "title": "UX Designer",
        "category": "Design",
        "description": "Make products easier and more useful. You will research users, sketch flows, prototype, and test before engineers build.",
        "avg_salary": "$75k–$140k",
        "outlook": "Steady demand wherever digital products exist",
        "education_fit": "Design, Psychology, HCI, Communications, any major with a portfolio",
        "keywords": "design,users,ui,ux,creative,research,figma",
        "skills": [
            ("User Research", "core"),
            ("UI Design", "core"),
            ("Figma", "core"),
            ("Communication", "core"),
            ("Writing", "supporting"),
            ("HTML/CSS", "supporting"),
            ("Product Thinking", "supporting"),
        ],
        "roadmap": [
            (1, "Design fundamentals", "Learn hierarchy, spacing, accessibility, and visual contrast.", "Figma tutorials, Laws of UX"),
            (2, "User research", "Run 5 interviews and turn notes into personas and jobs-to-be-done.", "NN/g articles"),
            (3, "Flows and wireframes", "Map a complete user journey and low-fidelity screens.", "FigJam, Whimsical"),
            (4, "High-fidelity prototype", "Build an interactive prototype and test with 5 users.", "Figma, Maze"),
            (5, "Case study writing", "Document problem, process, decisions, and impact.", "UX Portfolio examples"),
            (6, "Apply and iterate", "Share work, join critiques, and apply to internships.", "ADPList mentorship"),
        ],
        "projects": [
            ("Campus App Redesign", "Beginner", "Redesign a confusing school portal with before/after flows.", "Figma, User Research", "Classic case study format."),
            ("Accessibility Audit", "Intermediate", "Audit a public site and propose inclusive fixes.", "UI Design, Writing", "Shows professional rigor."),
            ("Onboarding Prototype", "Advanced", "Prototype a 3-step onboarding flow and report usability findings.", "Figma, Product Thinking", "Hiring managers love measured outcomes."),
        ],
        "interview": [
            ("Walk through a design decision you changed after research.", "Show you listen to users, not just aesthetics.", "behavioral"),
            ("How do you handle conflicting stakeholder feedback?", "Talk about principles, data, and trade-offs.", "behavioral"),
            ("What makes an interface accessible?", "Mention contrast, labels, keyboard, and plain language.", "technical"),
        ],
    },
    {
        "title": "Product Manager",
        "category": "Product",
        "description": "Decide what to build and why. You will talk to users, prioritize work, and align design, engineering, and business.",
        "avg_salary": "$95k–$170k",
        "outlook": "Competitive, but strong for people who can ship outcomes",
        "education_fit": "Business, CS, Economics, any major with leadership evidence",
        "keywords": "product,strategy,users,business,leadership,roadmap",
        "skills": [
            ("Product Thinking", "core"),
            ("Communication", "core"),
            ("Leadership", "core"),
            ("Project Management", "core"),
            ("User Research", "supporting"),
            ("SQL", "supporting"),
            ("Writing", "supporting"),
        ],
        "roadmap": [
            (1, "Product sense", "Study how products win: users, value, and constraints.", "Lenny's Newsletter, Reforge essays"),
            (2, "Discovery practice", "Interview 8 users around one problem and write a PRD.", "Teresa Torres continuous discovery"),
            (3, "Prioritization", "Learn RICE/MoSCoW and defend a roadmap with trade-offs.", "Product School"),
            (4, "Analytics basics", "Track activation and retention with simple SQL or dashboards.", "Mixpanel blogs, Mode SQL"),
            (5, "Cross-functional project", "Lead a campus or club launch with a written retrospective.", "Student orgs"),
            (6, "PM interviews", "Practice product sense, estimation, and behavioral stories.", "Exponent, Lewis Lin"),
        ],
        "projects": [
            ("Feature Spec for a Campus App", "Beginner", "Write a one-pager with problem, users, metrics, and MVP.", "Writing, Product Thinking", "Shows structured thinking."),
            ("Retention Experiment Plan", "Intermediate", "Design an A/B test to improve weekly active users.", "SQL, Communication", "Signals metrics literacy."),
            ("Launch Retrospective", "Advanced", "Ship something real and document what you would do next.", "Leadership, Project Management", "Proof you can execute."),
        ],
        "interview": [
            ("How would you improve our product for students?", "Clarify goal, users, constraints, then 2–3 ideas with metrics.", "product"),
            ("Tell me about a time you said no to a popular request.", "Show prioritization and empathy.", "behavioral"),
            ("What metric would you watch after launching a new feature?", "Pick a north-star and a leading indicator.", "product"),
        ],
    },
    {
        "title": "Cybersecurity Analyst",
        "category": "Security",
        "description": "Protect systems and people from attacks. You will monitor threats, investigate incidents, and harden environments.",
        "avg_salary": "$85k–$150k",
        "outlook": "Persistent shortage of qualified analysts",
        "education_fit": "IT, Computer Science, Cybersecurity, related certifications",
        "keywords": "security,hacking,defense,networks,privacy,risk",
        "skills": [
            ("Cybersecurity Basics", "core"),
            ("Networking", "core"),
            ("Linux", "core"),
            ("Problem Solving", "core"),
            ("Communication", "supporting"),
            ("Python", "supporting"),
            ("Cloud Computing", "supporting"),
        ],
        "roadmap": [
            (1, "Security mindset", "Learn CIA triad, common attacks, and safe lab habits.", "TryHackMe pre-security"),
            (2, "Networking", "Understand TCP/IP, DNS, firewalls, and packets.", "Professor Messer, Wireshark"),
            (3, "Linux and scripting", "Get comfortable on the command line and automate small checks.", "OverTheWire Bandit"),
            (4, "SOC basics", "Practice log review, alerts, and incident notes.", "LetsDefend, Blue Team labs"),
            (5, "Cloud security intro", "Learn IAM, shared responsibility, and misconfiguration risks.", "AWS Cloud Quest / free tier docs"),
            (6, "Cert + portfolio", "Aim for Security+ or equivalent and write 2 lab write-ups.", "CompTIA, GitHub gists"),
        ],
        "projects": [
            ("Home Lab Notes", "Beginner", "Document a virtual lab and the attacks/defenses you practiced.", "Linux, Networking", "Shows hands-on learning."),
            ("Phishing Awareness Mini-site", "Intermediate", "Teach classmates how to spot social engineering.", "Writing, Communication", "Human-layer security matters."),
            ("Log Review Playbook", "Advanced", "Create a checklist for triaging failed logins and suspicious traffic.", "Cybersecurity Basics, Problem Solving", "Mirrors real SOC work."),
        ],
        "interview": [
            ("What would you do if you saw unusual login activity at 3am?", "Talk detection, containment, evidence, and communication.", "technical"),
            ("Explain a vulnerability in plain language to a non-technical manager.", "Avoid jargon; talk risk and next steps.", "behavioral"),
            ("Why is defense-in-depth important?", "Layer people, process, and technology.", "technical"),
        ],
    },
    {
        "title": "Digital Marketer",
        "category": "Marketing",
        "description": "Grow audiences and measure what works. You will run campaigns, write copy, and use data to improve conversion.",
        "avg_salary": "$55k–$120k",
        "outlook": "Broad demand in startups, agencies, and in-house teams",
        "education_fit": "Marketing, Communications, Business, Psychology",
        "keywords": "marketing,content,brand,social,growth,campaigns",
        "skills": [
            ("Marketing Strategy", "core"),
            ("Writing", "core"),
            ("Data Visualization", "supporting"),
            ("Communication", "core"),
            ("Excel", "core"),
            ("Public Speaking", "supporting"),
            ("HTML/CSS", "supporting"),
        ],
        "roadmap": [
            (1, "Positioning", "Write a simple value proposition for a campus club or brand.", "April Dunford notes, HubSpot Academy"),
            (2, "Content engine", "Publish 8 pieces across two channels and track engagement.", "Google Analytics, Canva"),
            (3, "Paid vs organic", "Learn campaign structure, targeting, and creative tests.", "Meta Blueprint, Google Skillshop"),
            (4, "Conversion basics", "Map a funnel and improve one landing page.", "CXL intro articles"),
            (5, "Analytics story", "Build a weekly report a founder would actually read.", "Looker Studio, Excel"),
            (6, "Portfolio", "Package 2 campaigns with goals, creative, and results.", "Personal site, LinkedIn"),
        ],
        "projects": [
            ("Club Growth Campaign", "Beginner", "Increase event signups with a 2-week content plan.", "Writing, Marketing Strategy", "Real-world proof."),
            ("Landing Page A/B Copy", "Intermediate", "Rewrite headlines and measure click-through.", "HTML/CSS, Excel", "Shows experimentation."),
            ("Channel Mix Report", "Advanced", "Recommend budget split using simple performance data.", "Excel, Communication", "Junior marketer signal."),
        ],
        "interview": [
            ("How would you launch a new student product with $0 budget?", "Lead with audience, channel, and a test you can run this week.", "strategy"),
            ("Tell me about content that failed. What did you change?", "Show measurement and iteration.", "behavioral"),
            ("Which metric matters more: followers or conversions?", "Tie metrics to the business goal.", "strategy"),
        ],
    },
    {
        "title": "Cloud Engineer",
        "category": "Infrastructure",
        "description": "Keep applications reliable in the cloud. You will automate infrastructure, monitoring, and deployments.",
        "avg_salary": "$100k–$170k",
        "outlook": "Strong as companies move workloads to cloud platforms",
        "education_fit": "Computer Science, IT, Engineering",
        "keywords": "cloud,aws,devops,infrastructure,linux,automation",
        "skills": [
            ("Cloud Computing", "core"),
            ("Linux", "core"),
            ("Python", "core"),
            ("Networking", "core"),
            ("Git", "core"),
            ("Problem Solving", "core"),
            ("REST APIs", "supporting"),
        ],
        "roadmap": [
            (1, "Linux fluency", "Learn files, permissions, processes, and networking tools.", "Linux Journey"),
            (2, "Cloud fundamentals", "Study compute, storage, IAM, and billing alerts.", "AWS / Azure / GCP free paths"),
            (3, "Infrastructure as code intro", "Deploy a simple app with a repeatable template.", "Terraform tutorials"),
            (4, "CI/CD", "Automate tests and deploys from Git.", "GitHub Actions docs"),
            (5, "Observability", "Add logs/metrics and practice an incident timeline.", "Prometheus/Grafana intros"),
            (6, "Cert + project", "Complete one associate-level cert path and a public architecture write-up.", "Cloud practitioner exams"),
        ],
        "projects": [
            ("Static Site on Cloud Storage", "Beginner", "Host a personal site with HTTPS and a custom domain.", "Cloud Computing, Git", "First deploy win."),
            ("Containerized Flask App", "Intermediate", "Dockerize an API and deploy with a managed service.", "Python, Linux", "Core cloud skill."),
            ("Cost and Uptime Report", "Advanced", "Document architecture, budgets, and failure modes.", "Networking, Communication", "Senior-leaning thinking."),
        ],
        "interview": [
            ("How would you design a highly available student app on a budget?", "Talk regions, backups, and what you would skip at first.", "technical"),
            ("Describe a time you automated a painful manual task.", "Quantify time saved.", "behavioral"),
            ("What is the shared responsibility model?", "Be precise about customer vs provider duties.", "technical"),
        ],
    },
    {
        "title": "Business Analyst",
        "category": "Business",
        "description": "Bridge business goals and technical delivery. You will gather requirements, model processes, and measure outcomes.",
        "avg_salary": "$70k–$130k",
        "outlook": "Stable across finance, healthcare, and operations",
        "education_fit": "Business, Economics, Information Systems, any analytical major",
        "keywords": "business,analysis,process,requirements,excel,stakeholders",
        "skills": [
            ("Excel", "core"),
            ("SQL", "core"),
            ("Communication", "core"),
            ("Writing", "core"),
            ("Problem Solving", "core"),
            ("Project Management", "supporting"),
            ("Data Visualization", "supporting"),
        ],
        "roadmap": [
            (1, "Excel power skills", "Pivot tables, lookups, and clean datasets.", "ExcelIsFun, Microsoft Learn"),
            (2, "Requirements writing", "Practice user stories and acceptance criteria.", "BABOK intro summaries"),
            (3, "Process mapping", "Document as-is vs to-be workflows for a campus process.", "Lucidchart, Miro"),
            (4, "SQL for questions", "Answer business questions from sample databases.", "SQLBolt, Mode"),
            (5, "Stakeholder interviews", "Run discovery with 5 people and reconcile conflicting needs.", "Toastmasters"),
            (6, "Case portfolio", "Publish 2 analyses with recommendations and risks.", "Personal site / Notion"),
        ],
        "projects": [
            ("Library Wait-Time Study", "Beginner", "Measure a campus bottleneck and recommend a change.", "Excel, Communication", "Shows structured analysis."),
            ("Requirements Pack", "Intermediate", "Write stories, wireframe notes, and a test checklist for a feature.", "Writing, Project Management", "BA bread and butter."),
            ("KPI Scorecard", "Advanced", "Define leading/lagging indicators for a student org.", "SQL, Data Visualization", "Decision-ready work."),
        ],
        "interview": [
            ("How do you handle incomplete requirements?", "Ask clarifying questions, document assumptions, confirm early.", "behavioral"),
            ("Walk me through analyzing a drop in weekly signups.", "Hypotheses, data, process, recommendation.", "case"),
            ("What makes a good user story?", "User, need, value, and testable acceptance.", "technical"),
        ],
    },
    {
        "title": "AI / ML Engineer",
        "category": "Artificial Intelligence",
        "description": "Build systems that learn from data and run in production. You will train models, evaluate quality, and ship APIs around them.",
        "avg_salary": "$110k–$190k",
        "outlook": "Rapid growth with high skill bar",
        "education_fit": "Computer Science, Mathematics, Engineering, Physics",
        "keywords": "ai,ml,models,deep learning,python,research,automation",
        "skills": [
            ("Python", "core"),
            ("Machine Learning", "core"),
            ("Statistics", "core"),
            ("REST APIs", "core"),
            ("Git", "core"),
            ("Problem Solving", "core"),
            ("Cloud Computing", "supporting"),
            ("SQL", "supporting"),
        ],
        "roadmap": [
            (1, "Python and math refresh", "Linear algebra intuition, probability, and clean code.", "fast.ai, 3Blue1Brown"),
            (2, "Classical ML", "Feature pipelines, validation, and error analysis.", "scikit-learn, Kaggle"),
            (3, "Deep learning intro", "Train a small neural net and understand overfitting.", "PyTorch tutorials"),
            (4, "ML as a service", "Wrap a model in an API with logging and versioning.", "FastAPI, Docker"),
            (5, "Evaluation discipline", "Build a test set you trust and document failure cases.", "Papers with Code blogs"),
            (6, "Public demo", "Ship a demo and write a technical blog of trade-offs.", "Hugging Face Spaces"),
        ],
        "projects": [
            ("Resume Skill Extractor", "Beginner", "Parse skills from text and show a simple UI.", "Python, REST APIs", "Practical NLP starter."),
            ("Image Classifier Demo", "Intermediate", "Train, evaluate, and deploy a small vision model.", "Machine Learning, Git", "Shows the full loop."),
            ("RAG Study Assistant", "Advanced", "Answer questions from course notes with citations.", "Python, Cloud Computing", "Current industry pattern."),
        ],
        "interview": [
            ("How do you prevent a model from looking great in a notebook but failing live?", "Distribution shift, monitoring, fallbacks.", "technical"),
            ("Explain bias-variance to a product manager.", "Use a simple analogy and a metric.", "communication"),
            ("When should you not use a large model?", "Cost, latency, data size, and simpler baselines.", "technical"),
        ],
    },
    {
        "title": "Full Stack Developer",
        "category": "Technology",
        "description": "Own both the interface and the server. You will ship features end-to-end and care about usability plus reliability.",
        "avg_salary": "$85k–$155k",
        "outlook": "Consistently hired at startups and product companies",
        "education_fit": "Computer Science, IT, bootcamps with a strong portfolio",
        "keywords": "fullstack,web,frontend,backend,apps,javascript,python",
        "skills": [
            ("JavaScript", "core"),
            ("HTML/CSS", "core"),
            ("Python", "core"),
            ("SQL", "core"),
            ("REST APIs", "core"),
            ("Git", "core"),
            ("UI Design", "supporting"),
            ("Problem Solving", "core"),
        ],
        "roadmap": [
            (1, "Frontend craft", "Semantic HTML, CSS layout, and accessible forms.", "MDN, frontend mentors"),
            (2, "JavaScript depth", "DOM, fetch, and state without a heavy framework first.", "javascript.info"),
            (3, "Backend with Flask", "Routes, SQLite, validation, and sessions or tokens.", "Flask mega-tutorial"),
            (4, "Full-stack feature", "Auth, CRUD, and a polished UI on one product.", "This CareerPath app as a model"),
            (5, "Quality bar", "Error handling, loading states, and basic tests.", "Playwright intro"),
            (6, "Ship publicly", "Deploy, write a README, and collect feedback.", "Render, Railway, GitHub Pages for static"),
        ],
        "projects": [
            ("Personal Knowledge Base", "Beginner", "Notes app with search and tags.", "HTML/CSS, JavaScript, SQL", "Everyday usefulness."),
            ("Marketplace Mini", "Intermediate", "Listings, users, and messaging stubs.", "Python, REST APIs", "Shows product completeness."),
            ("CareerPath Clone+", "Advanced", "Add a new recommendation signal and deploy it.", "Git, UI Design", "Meta project that employers remember."),
        ],
        "interview": [
            ("How do you split work between frontend and backend for a new feature?", "Start from user flow, then data, then APIs, then UI.", "technical"),
            ("Describe a UI bug that was actually a data problem.", "Show you debug across layers.", "behavioral"),
            ("What would you improve first on a slow web app?", "Measure, then cache, queries, assets.", "technical"),
        ],
    },
]

RESUME_ITEMS = [
    ("Clear headline", "Role you want plus 1 specialty, not a vague objective paragraph.", "header"),
    ("Contact that works", "Email, phone, LinkedIn, and GitHub/portfolio links that actually open.", "header"),
    ("Education with relevance", "Degree, school, dates, GPA if strong, plus 2 relevant courses.", "education"),
    ("Skills grouped", "Split technical vs tools vs languages. Only list skills you can discuss.", "skills"),
    ("2–4 quantified bullets per experience", "Start with verbs. Include a number, tool, or outcome.", "experience"),
    ("Projects with links", "Each project has problem, your role, stack, and a live/repo link.", "projects"),
    ("No typos or inconsistent dates", "Print to PDF and read aloud. Align months/years.", "polish"),
    ("One page if under 5 years experience", "Cut filler clubs unless they show leadership or skills.", "polish"),
    ("Keywords from target roles", "Mirror language from 2 job posts you actually want.", "polish"),
    ("Proofread by another person", "Ask a mentor to mark anything confusing.", "polish"),
]


def seed():
    conn = get_connection()
    existing = conn.execute("SELECT COUNT(*) AS c FROM careers").fetchone()["c"]
    if existing:
        conn.close()
        return

    skill_ids = {}
    for name, category in SKILLS:
        cur = conn.execute(
            "INSERT INTO skills (name, category) VALUES (?, ?)", (name, category)
        )
        skill_ids[name] = cur.lastrowid

    for career in CAREERS:
        cur = conn.execute(
            """
            INSERT INTO careers (title, category, description, avg_salary, outlook, education_fit, keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                career["title"],
                career["category"],
                career["description"],
                career["avg_salary"],
                career["outlook"],
                career["education_fit"],
                career["keywords"],
            ),
        )
        career_id = cur.lastrowid
        for skill_name, importance in career["skills"]:
            conn.execute(
                "INSERT INTO career_skills (career_id, skill_id, importance) VALUES (?, ?, ?)",
                (career_id, skill_ids[skill_name], importance),
            )
        for month, title, description, resources in career["roadmap"]:
            conn.execute(
                """
                INSERT INTO roadmap_steps (career_id, month_number, title, description, resources)
                VALUES (?, ?, ?, ?, ?)
                """,
                (career_id, month, title, description, resources),
            )
        for title, difficulty, description, skills_used, outcome in career["projects"]:
            conn.execute(
                """
                INSERT INTO projects (career_id, title, difficulty, description, skills_used, outcome)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (career_id, title, difficulty, description, skills_used, outcome),
            )
        for question, tip, category in career["interview"]:
            conn.execute(
                """
                INSERT INTO interview_questions (career_id, question, tip, category)
                VALUES (?, ?, ?, ?)
                """,
                (career_id, question, tip, category),
            )

    for title, description, section in RESUME_ITEMS:
        conn.execute(
            "INSERT INTO resume_items (title, description, section) VALUES (?, ?, ?)",
            (title, description, section),
        )

    conn.commit()
    conn.close()
