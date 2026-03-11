# Advanced Cloud Development Technologies Coursework 2

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

This is a python CLI (Command Line Interface) application developed for use by ALC (Antrim Logistics Company).
The goal of this application is to screen ALC customer email addresses for any known data breaches they may have been a part of. 
This application reads in a single "email_list.csv" file which holds the email addresses to be screened, and by using the Intelligence X "search" API endpoint, returns any known breach records and writes it to a "output_result.csv" file. A real time summary of the results is printed within the terminal as the application processes the email addresses within email_list.csv, and provides summary statistics once finished, including a count of emails screened, the rate of breaches, and top identified breach sources.

This application is designed with production use in mind, making use of docker containerisation and GitHub CI pipeline for automated testing on commits to the source control repository.

## Architecture

    ┌─────────────────────────────────────────────────────┐
    |                   Entry Points                      |
    |              CLI (python -m src.main)               |
    │               Docker (docker run )                  |
    └────────────────────┬────────────────────────────────┘
                         |
    ┌─────────────────────────────────────────────────────┐
    |                   main.py                           |                    
    |   Handle Arguments - Loading Config - Logging       |
    └───────┬──────────────────────────────┬──────────────┘
            |                              |
    ┌────────────────┐              ┌────────────────────┐
    |   io_handler   |              |   breach_checker   |
    |   read csv     |              |     Controller     |
    |   write csv    |              |  Email Validation  |
    └───────┬────────┘              └───────┬────────────┘
            |                               |
            |                               |
            |                  ┌──────────────────────────┐     
            |                  |     API Client Layer     |
            |                  |                          |
            |                  |    IntelligenceXClient   |
            |                  |     (Live API Calls)     |
            |                  |           OR             |
            |                  |  example (dry-run/test)  |
            |                  └────────────┬─────────────┘
            |                               |
    ┌────────────────┐              ┌────────────────────┐
    | email_list.csv |              |   Intelligence X   |
    |     (input)    |              |   Search API       |
    └───────┬────────┘              |   free.intelx.io   |
            |                       └────────────────────┘
    ┌───────────────────┐               
    | output_result.csv |
    |     (output)      |
    └───────────────────┘

## APIs Used:
1. IntelligenceX Search API - https://help.intelx.io/docs/api/

Intelligence X was chosen for the API as it provides a free tier for accounts for prototyping / testing purposes, lowering cost and barrier to entry. 
This has allowed for agile rapid development, quickly developing, testing and iterating upon the application as required. 
Additionally, for future scoping, Intelligence X is known for searching beyond just breach-specific data sources, such as web archives, document sharing platforms and the darknet. 
As a result, should this application be brought forward to production the implementation for Intelligence X is already in place for the free tier, and can be easily updated for the premium plan. 
This API is a standard REST API, meaning that it is easy to implement and uses a simple header-based API Key authentication. 
Intelligence X also keeps high quality documentation available to help with the development and understanding. 
Ideally on the premium plan we would switch from using "search" endpoint, and use the premium exclusive "phonebook" endpoint, as this returns cleaner, more focused data.

Another API was considered for use, being Have I Been Pwned (HIBP). While this API returns more focused data, it does not include a free tier. 
it was decided that for future proofing, Intelligence X was preferred at this stage. 
Ideally, both API's will be used to cross reference results and get a more robust search by making use of various independant searching APIs.

### Extensible Design
This application was designed to decouple the core logic from the API controller. By making use of the "search_email()" class, any future breach intelligence APIs/providers can be added without updating any of the existing logic. 
By creating a new client class for the new API, implementing search_email(), when running this in main, we can pass through which API client should be used.
By adding a --provider flag in main.py, at runtime users can decide if they want to scan via Intelligence X or another API. 
No changes to any other files would be required.

## To get setup:
1. Clone the latest master branch from the GitHub Repo: git clone https://github.com/Barley768/50061799-ACDT-CW2
2. Create virtual environment:
        python -m venv .venv
        .venv\Scripts\activate
3. Install dependencies: `pip install -r requirements.txt`
4. Create a copy of the .env.example:
        copy .env.example .env
5. Replace the dummy IX_API_KEY in .env with your actual API key

## Configuration
| Setting        | Value                    | Description                                   |
| -------------- |--------------------------| ----------------------------------------------|
| base_url       | free.intelx.io           | API endpoint used for screening               |
| timeout        | 15                       | Seconds per request                           |
| max_retries    | 5                        | Max number of retry attempts in case of error |
| backoff_factor | 2                        | Delay between retry attempts                  |
| request_delay  | 1                        | Delay between request calls                   |
| input          | email_list.csv           | Name of input file                            |
| output         | output/output_result.csv | Output location for results file              |
| logging.level  | INFO                     | DEBUG / INFO / WARNING / ERROR                |

## Running the Application:
### Running Locally
1. Navigate to the project root in terminal (This is important for CSV and config paths within the code running from project root)
2. Activate venv:
        .venv\Scripts\activate
3. run main.py (pass argument --dry-run to test without using API credits)

Examples:
1. Test without using API credits:
        python -m src.main --dry-run
2. Run process using API credits:
        python -m src.main

### Running via Docker:
1. Ensure docker is installed on local machine
2. Navigate to whatever folder you want the output saved to
3. In terminal, run the following to load the image:
        docker load -i 50061799-acdt-cw2.tar
4. (OPTIONAL) To check loaded docker images, run the following:
        docker images
5. Run the docker image.
        For dry run without output file, use:
            docker run -v ${PWD}/output:/app/output 50061799-acdt-cw2 --dry-run
        
        for main run, you need to pass in an argument for your IntelligenceX API key, and an argument for an output folder. Below creates a folder "output" in whatever directory the terminal is currently in:
            docker run -e IX_API_KEY=<YOUR API KEY> -v ${PWD}/output:/app/output 50061799-acdt-cw2

## Testing
To run test scripts, use the following:
        python -m unittest tests/test_bt.py -v

### Test coverage
Test Classes:
- TestEmailValidation           - Tests valid and invalid email addresses
- TestReadEmailCsv              - Tests reading csv files, checks for columns, blank rows, missing file, empty file
- TestWriteResultsCsv           - Tests output csv files, checks for columns, separator
- TestBreachCheckerHappyPath    - Tests API results, checks for breached results, clean results, empty results
- TestBreachCheckerErrors       - Tests API error handling, checks for partial failures
- TestSummaryStats              - Tests summary results, checks for breach rates, dividing by zero errors
- TestAPIClientRetry            - Tests API results for retry on 429 rate limiting, 403 authentication error raises APIError, timing out returns None
- TestEndToEnd                  - Tests full process from reading input csv, checking results and writing to output csv

### Test evidence
Test evidence will be attached in .zip in txt format, with all tests passing on final execution

## Output Format
Output is formatted as a csv with the following headers:
- email_address
- breached
- site_where_breached

### Analyst Summary
Once the application is complete, a summary analysis will be printed in the terminal. Below is the example result:
        ============================================================
        ALC BREACH SCREENING - ANALYST SUMMARY
        ============================================================
        Total checked  : 11
        Breached       : 4
        Clean          : 4
        Invalid        : 3
        Breach rate    : 50.0%

        Top 10 breach sources:
        4  facebook.com-2025
        2  twitter.com-2018
        1  serebii.com-2012
        1  github.com-2022
        1  instagram.com-2024
        1  tesco.co.uk-2017
        1  nikon.com-2006
        1  dnd3-5.wikidot.com-2026
        1  foundryvtt.com-2025
        1  foundryvtt.com-2026
        ============================================================

## Limitations
Within this project, we make use of the free "search" Intelligence X endpoint, which returns less structured, clean data as opposed to the premium "phonebook" endpoint.
This project was originally planned around the usage of the phonebook endpoint, until issues were encountered when testing. As a result, we return a wider selection of data than exclusively breach data. These results should be treated as warning points requiring further analysis, and not an outright confirmation of a breach. 

Using the free tier of Intelligence X, we have limited credits to use for API calls. This has been considered for by the use of request_delay, and the dry-run option for functionality testing, however large email lists input could use all available free credits for the current time period.

Test data provided is entirely fictional and does not represent any real records

There is currently no handling for any deduplication within the email_list.csv file, meaning if the same email address is provided multiple times, API calls will be wasted returning the same dataset additional times

This tool exclusively checks against Intelligence X data, cross referencing multiple breach data sources should be considered for a final production application for higher accuracy in results

## Assumptions
This application assumes that the input file will be called "email_list.csv", and will have the one following header:
- email

The project is being executed from the project root directory, ensuring relative paths for Configuration and CSV files resolve without error

IX_API_KEY is set correctly within .env, or passed through from an established environment variable when running on a live production environment. Without this API key, the application will exit unless explicitly running with the --dry-run arguement

The application is being run on a machine with access to the internet to reach the free.intelx.io API

python 3.11 or higher is installed for local machine runs, or docker is installed for running from the docker image

ALC has the legal authority to be using and screening the email addresses included in the email_list.csv file

## Ethics and GDPR
This application should only ever be used to screen email addresses that the company ALC has legal reason to screen. This application should not be run against unauthorised email addresses.

ALC has a lawful basis for processing this PII under the GDPR Article 6: "Lawfulness of processing".

Under the GDPR Article 33, if there is a significant breach rate, ALC may be required to notify the Information Commissioner's Office (ICO) within 72 hours of becoming aware of the breach.

This application only processes the email addresses to minimise the PII (Personally Identifiable Information) being processed or stored.

ALC should define a clear data retention policy in line with each country's data retention periods for which the company holds data from. This data should be held no longer than needed.

By using Intelligence X to screen email addresses, ALC is sharing PII with a third party, and should have a DPA (Data Processing Agreement) in place with Intelligence X that ALC customers are informed of.

API keys should never be commited to version control or shared within any docker images. .env should be included within the .gitignore to avoid accidentally exposing API keys

## License
Copyright @ 2026 Neil Beattie. All rights reserved.
Produced as coursework for my Advanced Cloud Development Technologies module at Belfast Metropolitan College.