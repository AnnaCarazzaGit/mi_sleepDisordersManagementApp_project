# Advanced Sleep Evaluation (ASE)

![ASE logo](logoASE.png)

Python desktop application developed as an academic medical-informatics prototype for the management of sleep-disorder care pathways. The application combines role-based graphical interfaces, patient self-management tools, appointment scheduling, digital sleep diaries, simulated physiological and sleep-data visualization, prescription management and administrative functions.

> **Academic prototype and simulated data:** the application is intended exclusively for academic, demonstration and educational purposes. **All data included in the repository are entirely simulated and do not refer to real individuals.** This includes user profiles, names, identifiers, login credentials, appointments, clinical information, prescriptions, sleep-diary entries, physiological measurements and sleep data. No real patient data, personal data or sensitive health information are included. This software is not a medical device and is not intended for diagnosis, treatment or clinical decision-making.

## Application roles

### Patient

- Credential-based login and password reset
- Personal profile visualization and editing
- Booking, modification and cancellation of visits and psychological consultations
- Digital sleep diary with SQLite persistence
- Visualization of sleep and physiological data
- Analysis over one night, the last 7 days, the last month or the last 6 months
- Help-desk messaging interface

### Sleep specialist / doctor

- Role-based login and personal profile management
- Patient lookup by patient ID
- Review of patient diary scores
- Visualization of sleep and physiological parameters
- Prescription creation, editing and deletion
- Weekly appointment calendar

### Psychologist

- Role-based login and personal profile management
- Patient lookup and consultation overview
- Review of patient diary scores
- Session-note interface
- Weekly consultation calendar

### Application manager

- PIN-based manager access
- Patient and specialist management
- Sensor inventory and patient-sensor association management
- Help-desk message handling
- Demonstration system-status interface

## Sleep and physiological data visualization

The specialist interface visualizes simulated sleep data stored at nightly and minute-level resolution. Available parameters include:

- total sleep time;
- sleep versus wake percentage;
- sleep-stage distribution;
- heart rate;
- respiratory rate;
- SpO2;
- snoring alerts;
- skin temperature.

Plots are generated with Matplotlib and can be displayed for a single night or aggregated over longer time windows.

## Data layer

The prototype uses four local SQLite databases:

- `insomnia_management.db` — users, roles, personal information, patients, doctors, psychologists, visits, consultations, prescriptions, sensors and sensor associations;
- `sleep_data.db` — nightly sleep summaries and minute-level physiological data;
- `diary_responses.db` — patient sleep-diary scores;
- `helpdesk.db` — patient help-desk messages.

The databases included in this public repository contain **fully synthetic demonstration data** created solely to reproduce the application interface and workflow. All identities, credentials, appointments, clinical records, diary responses and physiological or sleep measurements are fictional and do not correspond to real patients, healthcare professionals or other individuals.

## Project structure

```text
mi_sleepDisordersManagementApp_project/
├── App/
│   ├── main.py
│   └── ui/
│       ├── database_controller.py
│       ├── login_manager.py
│       ├── login_page.py
│       ├── login_patient.py
│       ├── login_selector.py
│       ├── main_window.py
│       ├── style_ctk.py
│       ├── manager/
│       │   └── appmanager.py
│       ├── patient/
│       │   └── patient.py
│       ├── specialist/
│       │   ├── calendar_page.py
│       │   ├── diary_page.py
│       │   ├── home_page.py
│       │   ├── patient_page.py
│       │   ├── prescription_page.py
│       │   ├── profile_page.py
│       │   └── sensor_data_page.py
│       └── psychologist/
│           ├── calendar_page.py
│           ├── diary_page.py
│           ├── home_page.py
│           ├── note_page.py
│           ├── patient_page.py
│           └── profile_page.py
├── diary_responses.db
├── helpdesk.db
├── insomnia_management.db
├── sleep_data.db
├── logoASE.png
├── requirements.txt
├── .gitignore
└── README.md
```

The SQLite databases and logo remain in the repository root because the current application accesses these resources through root-relative paths.

## Installation

Python 3.12 is recommended.

### 1. Clone the repository

```bash
git clone https://github.com/AnnaCarazzaGit/mi_sleepDisordersManagementApp_project.git
cd mi_sleepDisordersManagementApp_project
```

### 2. Create and activate a virtual environment

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install the dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Tkinter must also be available in the local Python installation because the graphical interface is built on Tk/CustomTkinter.

## Running the application

Run the application from the repository root:

```bash
python App/main.py
```

Running the program from the repository root is important because the current version loads the logo and SQLite databases using relative paths.

## Demonstration credentials

The public demonstration database contains fictional, non-production credentials created solely for interface testing. They are part of the simulated dataset and are not associated with real users or accounts.

| Role | ID / PIN | Password |
|---|---|---|
| Patient | `ROSMAR020808M` | `DemoPatient01!` |
| Sleep specialist | `doctor_01` | `DemoDoctor01!` |
| Psychologist | `psychologist_01` | `DemoPsychologist01!` |
| Application manager | PIN `admin` | — |

## Technology stack

- Python
- CustomTkinter / Tkinter
- SQLite
- NumPy
- pandas
- Matplotlib
- Tkcalendar
- Pillow

## Current limitations

- The project is an academic desktop prototype rather than a production clinical system.
- Authentication is implemented locally and the fictional demonstration passwords are stored in plaintext in the SQLite database; this approach is suitable only for the academic prototype and not for production deployment.
- All user, clinical, physiological and sleep-related data are simulated and included solely for demonstration purposes.
- The manager system-status check is a graphical demonstration and does not perform real infrastructure monitoring.
- Psychologist notes are currently maintained in application memory rather than persisted in the database.
- Face ID-related code is present only as commented experimental code and is not an active application feature.
- The project has not undergone clinical, cybersecurity or usability validation for real-world medical deployment.

## Academic context

This repository demonstrates the design of a multi-role medical-informatics application integrating graphical user interfaces, local relational data management, healthcare workflow logic and physiological-data visualization in the context of sleep-disorder management.
