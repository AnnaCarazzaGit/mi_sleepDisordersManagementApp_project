# A²E³S Medical Informatics Project

Desktop medical-informatics prototype for sleep-health monitoring, patient self-management, appointment scheduling and administrative supervision.

The project includes two main graphical applications and an experimental facial-recognition login prototype:

- a **patient application** for profile management, digital sleep diaries, appointment booking and sleep-data visualization;
- a **manager application** for simulated user, sensor and system-status management;
- an optional **Face ID prototype** based on a webcam, OpenCV, `face_recognition` and `dlib`.

> **Academic prototype:** the physiological and sleep data displayed by the application are simulated. This software is not a medical device and is not intended for diagnosis, treatment or clinical decision-making.

## Main features

### Patient application

- Credential-based authentication
- Login-attempt control and password reset
- Patient profile visualization and editing
- Digital sleep diary with local JSON storage
- Appointment booking, modification and cancellation
- Calendar-based selection of available visits
- Visualization of simulated sleep and physiological parameters
- Multiple analysis periods: one night, seven days, one month and six months
- Help-desk interface

### Manager application

- Manager authentication
- Simulated patient and specialist management
- Simulated sensor inventory
- System-status check and progress visualization

### Experimental Face ID prototype

- Webcam-based face enrollment
- Local storage of reference images
- Face comparison during login
- Standard password login retained as an alternative

The Face ID module is experimental and is not designed as a production-grade biometric authentication system.

## Suggested project structure

```text
medical-informatics-project/
├── README.md
├── requirements.txt
├── requirements-faceid.txt
├── .python-version
├── .gitignore
│
├── src/
│   ├── patient_app.py
│   └── manager_app.py
│
├── prototypes/
│   └── face_id_prototype.py
│
├── archive/
│   └── legacy_patient_app.py
│
├── data/
│   └── example_diary_answers.json
│
└── assets/
```

## Python version

Use **Python 3.10.x**. The repository includes a `.python-version` file that pins Python **3.10.20**.

Python 3.10 is used to provide a stable environment for the older `face_recognition` package and its compiled `dlib` dependency. Using a newer interpreter may work, but it is not the recommended configuration for reproducing this project.

Check the active version with:

```bash
python3.10 --version
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd medical-informatics-project
```

Replace `<repository-url>` with the URL of your GitHub repository.

### 2. Install Python 3.10 and Tkinter on macOS

On macOS with Homebrew:

```bash
brew install python@3.10 python-tk@3.10
```

The Face ID module also requires the Apple command-line development tools because `dlib` contains compiled C++ components:

```bash
xcode-select --install
```

### 3. Create a virtual environment

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with:

```powershell
.venv\Scripts\activate
```

### 4. Upgrade the packaging tools

```bash
python -m pip install --upgrade pip setuptools wheel
```

### 5. Install the main application

```bash
python -m pip install -r requirements.txt
```

This installs only the packages needed by the patient and manager applications.

## Optional Face ID installation

The Face ID prototype requires additional computer-vision packages and a local compilation of `dlib`.

Install the pinned CMake version first:

```bash
python -m pip install cmake==3.31.6
```

Then install the Face ID dependencies:

```bash
python -m pip install -r requirements-faceid.txt
```

Confirm that the main modules are available:

```bash
python -c "import cv2, dlib, face_recognition; print('Face ID dependencies installed correctly')"
```

## Running the applications

### Patient application

```bash
python src/patient_app.py
```

Demonstration credentials:

```text
ID: emma
Password: emma
```

### Manager application

```bash
python src/manager_app.py
```

Demonstration manager code:

```text
admin
```

### Face ID prototype

```bash
python prototypes/face_id_prototype.py
```

To enable Face ID:

1. Log in using the standard patient credentials.
2. Accept the request to enable Face ID.
3. Allow the application to access the webcam.
4. A reference image is stored locally in `captured_faces/`.
5. On the next login, enter the patient ID and select **Use Face ID**.

If the webcam does not open, locate `cv2.VideoCapture(1)` in the `capture_face_image()` function and try:

```python
cv2.VideoCapture(0)
```

The correct camera index depends on the computer and connected cameras.

## Local data and privacy

The application stores prototype data locally. The following files and folders should not be committed to GitHub:

```text
captured_faces/
data/diary_answers.json
```

Only anonymous demonstration data should be included in the public repository. Do not upload real patient information, credentials or facial images.

## Technology stack

- Python 3.10
- CustomTkinter and Tkinter
- Tkcalendar
- NumPy and pandas
- Matplotlib
- OpenCV
- face_recognition
- dlib
- JSON-based local data storage

## Current limitations

- User accounts and demonstration credentials are hard-coded.
- Data persistence is limited to local JSON files.
- Physiological and sleep measurements are simulated.
- Manager data and system checks are simulated.
- Facial images are stored locally rather than in a secure biometric database.
- The Face ID implementation does not include liveness detection or anti-spoofing.
- The application has not undergone clinical, cybersecurity or usability validation.

## Future developments

- Integration with a secure relational database
- Password hashing and role-based access control
- Secure handling of biometric templates
- Integration with real wearable-sensor data
- Improved appointment persistence and synchronization
- Export of sleep reports for healthcare professionals
- Automated testing and modular code organization
- Clinical and usability validation
