# Lab Dictionary

A full-stack Django web application developed for the Yale Clinical & Translational Research Accelerator (CTRA) to streamline the process of creating standardized clinical data requests.

Instead of requiring researchers to manually browse thousands of medications, laboratory tests, procedures, observations, and encounter settings, this application provides an interactive web interface that allows users to search, filter, preview, and submit standardized OMOP-compatible data requests.

The application was designed for deployment on an internal Yale server and is intended for authenticated research staff rather than the general public.

---

## Overview

Clinical researchers often need to request large sets of standardized OMOP concepts before data extraction can begin.

Prior to this application, the workflow required researchers to manually obtain reference spreadsheets, search through them externally, and communicate selections through email.

Lab Dictionary centralizes this entire workflow into a single web application by allowing users to:

- Select medications
- Select laboratory measurements
- Select observations (flowsheets)
- Select procedures
- Select ICD/CPT procedure mappings
- Configure encounter settings
- Automatically generate standardized CSV files
- Submit requests directly to the CTRA team through automated email

---

## Features

### Settings

Allows researchers to configure dataset-wide filters before requesting data.

Features include:

- Department selection
- Encounter type selection
- Age range
- Visit date range
- Detailed mode toggle
- Automatic generation of `omop_settings.csv`
- Summary generation included in email submissions

---

### Medications

Provides searchable access to standardized medication concepts.

Features include:

- Live search
- Multi-selection
- Dynamic filtering
- CSV preview generation
- Standardized medication export

---

### Labs

Allows users to build laboratory and observation requests simultaneously.

Features include:

- Dual synchronized tables
- Live search
- Multi-selection
- Custom Observation (Flowsheet) capture columns
- Automatic preview generation
- Separate Observation and Custom Observation exports

---

### Procedures

Allows users to request both procedure concepts and ICD/CPT mappings.

Features include:

- Independent Procedure and ICD/CPT tables
- Live searching
- Multi-selection
- Preview generation
- Separate procedure exports

---

### Data Submission

After completing selections, users submit a single request.

The application automatically:

- Generates all required CSV files
- Generates OMOP settings
- Builds a request summary
- Sends confirmation email to the requester
- Sends internal email (with attachments) to the CTRA team

---

## Technical Highlights

### Backend

- Python
- Django
- Django Templates
- SMTP email integration
- Environment-based configuration
- CSV parsing
- Dynamic CSV generation
- Automatic attachment generation

### Frontend

- HTML
- CSS
- Bootstrap 5
- Vanilla JavaScript
- Dynamic DOM rendering
- Live searching
- Debounced search inputs
- Responsive layout

### Data Processing

The application loads standardized monthly datasets for:

- Medications
- Measurements
- Observations
- Procedures
- ICD/CPT mappings
- Department references
- Encounter references

These datasets are cached in memory and loaded lazily by tab to improve responsiveness.

---

## Performance Optimizations

Several optimizations were implemented during development:

- Lazy-loading datasets by tab
- Debounced live searching
- Client-side filtering
- Reduced DOM updates
- Optimized table rendering
- Removal of unnecessary dataset columns
- Memory-conscious rendering of large datasets
- Preserving selections during dynamic filtering

These improvements significantly reduced rendering time for datasets containing tens of thousands of records.

---

## CSV Output

The application generates standardized CSV files including:

- med_YYYYMMDD_HHMMSS.csv
- lab_YYYYMMDD_HHMMSS.csv
- observation_YYYYMMDD_HHMMSS.csv
- custom_observation_YYYYMMDD_HHMMSS.csv
- procedure_YYYYMMDD_HHMMSS.csv
- procedure_cpt_YYYYMMDD_HHMMSS.csv
- omop_settings.csv

These files are automatically attached to internal submission emails.

---

## Email Workflow

Upon submission:

1. User receives a confirmation email.
2. CTRA team receives:
   - Submission summary
   - User information
   - OMOP settings summary
   - All generated CSV attachments

SMTP credentials are stored using environment variables and are not committed to the repository.

---

## Security

Sensitive configuration is managed using environment variables.

Examples include:

- Django `SECRET_KEY`
- SMTP credentials
- Email backend configuration

No secrets are stored in source control.

---

## Project Structure

```
Lab Dictionary/
│
├── dictionaries/
│   ├── templates/
│   │   └── dictionaries/
│   │       ├── base.html
│   │       ├── tab0.html
│   │       ├── tab1.html
│   │       ├── tab2.html
│   │       ├── tab3.html
│   │       └── tab4.html
│   │
│   ├── static/
│   ├── data/
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── labdictionary/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── manage.py
└── requirements.txt
```

---

## Running Locally

Clone the repository.

Create a virtual environment.

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file containing the required configuration:

```text
SECRET_KEY=...

EMAIL_BACKEND=...
EMAIL_HOST=...
EMAIL_PORT=...
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=...
```

Run Django:

```bash
python manage.py runserver
```

---

## Skills Demonstrated

This project demonstrates experience with:

- Full-stack web development
- Django
- Python
- JavaScript
- HTML/CSS
- Bootstrap
- REST-style AJAX communication
- Dynamic DOM manipulation
- Client-side performance optimization
- Lazy loading
- Debouncing
- CSV processing
- Email automation (SMTP)
- Environment configuration
- Git & GitHub
- UX/UI iteration based on stakeholder feedback
- Building internal research tools
- Working directly with clinical research workflows

---

## Development Notes

This application was developed iteratively in collaboration with researchers at the Yale Clinical & Translational Research Accelerator (CTRA). Requirements evolved throughout development based on user testing and feedback, resulting in multiple rounds of UI refinement, workflow improvements, and performance optimizations.

The project serves as an example of designing and implementing an internal research application that bridges backend data processing with an intuitive user interface while emphasizing maintainability, usability, and real-world deployment considerations.