# CCCS105: Parking Management System

**Student Names:** Visitacion, Princess Shayla B. & Villazer, Devine Grace S.

**Project:** LEONS Final Project Submission

---

## Project Overview
This is a web-based parking management system built using the Flask framework and MySQL. The application enables administrators to efficiently manage a registry of vehicles, monitor the real-time status of 50 parking slots across 10 academic buildings, and track active reservations.

---

## Project Structure
This repository is organized according to professional standards:
*   **src/**: Contains the main application logic (app.py) and the templates/ directory.
*   **database/**: Contains SQL scripts (schema.sql and initial_data.sql) for environment setup.
*   **docs/diagrams/**: Stores visual documentation (ERD and Relational Model).
*   **README.md**: Project documentation and setup guide.

---

## Features
1. **Admin Dashboard**: Real-time overview of total registered vehicles and available parking slots.
2. **Vehicle Management**: Add new vehicles, view the complete registry, and delete records.
3. **Slot Monitoring**: Visual status tracking (Available vs. Occupied) for all parking zones.
4. **Reservation Tracking**: Detailed logs including time-in and time-out timestamps.
5. **Data Export**: Capability to export the vehicle database to a CSV file.

---

## Installation and Setup

### 1. Database Configuration
1. Open XAMPP and start the Apache and MySQL modules.
2. Import database/schema.sql to create the CCCS105 database structure.
3. Import database/initial_data.sql to populate the system with admin accounts and test data.

### 2. Install Dependencies
Run the following command in your terminal:
bash pip install flask mysql-connector-python

### 3. Run the Application
Navigate to the source directory and run:
python src/app.py

### 4. Access the System
Open your web browser and go to:
http://127.0.0.1:5000/
username: admin
password: admin123

### Deliverables
ERD and Relational Model: Located in the /docs/diagrams/ folder.

### Video Presentation: 
https://drive.google.com/drive/folders/1Ij8wmjkUJDWxwLDOLyjvlsjSeGhlstEe?usp=drive_link




