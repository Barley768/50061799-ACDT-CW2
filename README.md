# Advanced Cloud Development Technologies Coursework 1

This project is being developed to meet the following criteria:
    
    Outcomes – No. & Title 
    A2: Identify and relate the various stages required to implement a Cloud based DevOps solution. A3: Compare and justify source control solutions.
    B2: Design and implement an effective DevOps solution.
    C1 – Construct and relay technical information to technical, management, user and academic audiences
    C2 – Using case studies evaluate and assess the repercussions of a poorly structured Cloud environment.
    C3 – Design and develop effective solutions to practical problems individually and as a member of Team.
    C4 – Improve presentation and communicate skills via reports and/or presentations.
    C5 – Develop the ability to learn independently and to find/integrate information from different sources required in solving real-life problems.
    D1 – Learn effectively in various situations making use of information retrieval skills and learning resources.
    D2 – Communicate effectively, using a range of media and with a variety of audiences. D3 – Work effectively under guidance or supervision, independently and as part of a team
    D4 – Manage one’s own learning and development including time management, organisational skills and awareness of entrepreneurship issues.
    D5 – Demonstrate continued professional development in recognition of the need for life-long learning


This assessment has two components:
    
    • Part 1 (60%) – Technical Build: Design and implement a production-ready Python tool that screens customer identifiers against breach-intelligence sources via APIs; produce actionable outputs, testing artefacts, and professional documentation.

    • Part 2 (40%) – Professional Report: A management-ready DevOps report that explains API-driven automation practices and makes policy/tooling recommendations for Antrim Logistics Company (ALC).

The work targets Level-6 performance by requiring justification of design decisions, evaluation of trade-offs, evidence of testing, professional communication, and ethical/legal awareness.


# Instructions
    Antrim Logistics Company (ALC) is growing its online services and maintains client contact details and login credentials. ALC requires a prototype risk-assessment tool to screen new and existing clients for potential exposure in known data breaches and to inform mitigation actions.

    Objective
    Build a Python application that consumes breach-intelligence APIs to check a list of customer email addresses (minimum) and optionally other identifiers for evidence of exposure in known breaches. Generate structured outputs for analysts and management.

    Approved data sources
        • You may use Intelligence X (free tier) as the primary sample provider; alternatively, you may justify another reputable source that offers a free or student-accessible tier.
        • If you change provider(s), document the rationale, capabilities, limits, and ethics.
        • Respect all usage limits and terms. Do not submit any API keys.

# Functional Requirements
    • Input: CSV file email_list.csv with a header and one email per row.
    • Processing: Query the selected API(s) for each email; handle rate limits, timeouts, and transient errors robustly (retry/backoff); log all requests and outcomes at an appropriate level (INFO/ERROR).
    • Output: CSV output_result.csv with columns email_address, breached (boolean), site_where_breached (semicolon-separated list). Include a concise analyst summary (counts by breach domain, top sources) in the README or an optional Markdown report.

# Non-Functional & “Production-Ready” Expectations
    • Config & Secrets: Use environment variables or a .env exemplar for API keys; never commit secrets. Support a configuration file (e.g., config.yaml) for API endpoints, rate limits, and timeouts.
    • Architecture & Code Quality: Modular structure (separate I/O, API client, core logic); PEP8 conformance; meaningful docstrings and type hints; include a lightweight architecture diagram.
    • Testing: Include unit tests for core functions (response parsing, CSV I/O, retry logic); provide a small synthetic test dataset and document expected outcomes; demonstrate error handling (invalid email, API 429, network error).
    • Logging & Observability: Emit structured logs (timestamped; include correlation where appropriate); clear separation between user messages and diagnostics.
    • Documentation: README.md covering problem, setup, configuration, run instructions, limitations, and ethics (authorisation to test, GDPR awareness).

# Stretch Features (optional for higher marks)
    • Asynchronous requests to improve throughput.
    • Containerisation with a minimal Dockerfile and run instructions.
    • Simple CI (e.g., GitHub Actions) for lint/test.
    • Data visualisation: a small chart summarising breaches.
    • Extensible design to plug in additional providers.


# Deliverables (Part 1)
    • Source code (Python) without secrets.
    • email_list.csv (example input; synthetic) and output_result.csv (example output; synthetic).
    • README.md with usage, configuration, assumptions, limitations, and ethics.
    • Unit tests and brief test evidence (e.g., test log/screenshot).
    • Optional: Dockerfile; CI workflow; architecture diagram.


## Application Description


## APIs Used:
1. IntelligenceX Search API - https://help.intelx.io/docs/api/

## To get setup:
1. Clone the Repo: git clone 
2. Create virtual environment:
        python -m venv .venv
        .venv\Scripts\activate
3. Install dependencies: `pip install -r requirements.txt`

## To run the script:
1. Navigate to the project root in terminal
2. Activate venv:
        .venv\Scripts\activate
3. run main.py (pass argument --dry-run to test without using API credits)

Examples:
1. Test without using API credits:
        python -m src.main --dry-run
2. Run process using API credits:
        python -m src.main