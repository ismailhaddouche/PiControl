# PiControl - Employee Time Tracking System# PiControl - Employee Time Tracking System# PiControl



A professional, web-based employee time tracking system designed for Raspberry Pi with RFID card support. Built with FastAPI and SQLite, featuring a responsive web interface for employee management and automated check-in/check-out functionality.A tailored Raspberry Pi app for worker clock-in/out registration using RFID.



## Table of ContentsA modern, web-based employee time tracking system designed for Raspberry Pi with RFID card support. Built with FastAPI and SQLite, featuring a responsive web interface for employee management and automated check-in/check-out functionality.



- [Overview](#overview)**Author:** hismardev

- [Features](#features)

- [Technology Stack](#technology-stack)## 🚀 Features

- [Requirements](#requirements)

- [Installation](#installation)## Summary

- [Configuration](#configuration)

- [Usage](#usage)### Core Functionality

- [API Documentation](#api-documentation)

- [Maintenance](#maintenance)- **RFID-based Time Tracking**: Automatic employee check-in/out using RFID cardsPiControl is a lightweight application designed to run on a Raspberry Pi and manage employee check-in/check-out

- [Testing](#testing)

- [Project Structure](#project-structure)- **Employee Management**: Complete CRUD operations for employee recordsrecords using RFID readers. It provides an administration API (FastAPI), a web interface for administrators,

- [Security](#security)

- [Contributing](#contributing)- **Real-time Dashboard**: Live view of employee status and recent activitya simulator to test check-ins without hardware, and utilities for installation and recovery on a physical device.

- [License](#license)

- [Support](#support)- **Time Reports**: Detailed work hours calculation and reporting



## Overview- **Archive System**: Soft delete functionality for employee recordsThis repository contains the server logic, data models, HTML templates, and installation scripts designed



PiControl is a lightweight application designed to run on Raspberry Pi devices and manage employee time tracking using RFID readers. It provides a complete administration API built with FastAPI, a web interface for administrators, an RFID simulator for testing, and comprehensive utilities for installation and recovery on physical devices.- **Admin Interface**: Secure web-based administration panelto deploy PiControl on a Raspberry Pi or in a local development environment.



The system automatically detects whether an RFID scan is a check-in or check-out based on the employee's last recorded activity, calculates work hours, and provides detailed reporting capabilities. All data is stored in a local SQLite database with support for archiving and restoration of employee records.



## Features### Advanced Features## Technologies and Stack Used



### Core Functionality- **Automatic Type Detection**: Smart detection of entry vs exit based on last check-in



- **RFID-based Time Tracking**: Automatic employee check-in/out using RFID cards with intelligent entry/exit detection- **Session Management**: Secure user authentication with session cookies- **Language:** Python 3.10+ / 3.11+

- **Employee Management**: Complete CRUD operations for employee records with soft delete functionality

- **Real-time Dashboard**: Live view of employee status, recent activity, and current work sessions- **Data Validation**: Comprehensive input validation and error handling- **Web framework:** FastAPI (REST endpoints, Jinja2 templates)

- **Time Reports**: Detailed work hours calculation with customizable date ranges and export capabilities

- **Archive System**: Soft delete functionality preserving historical data while removing active employee access- **Responsive Design**: Mobile-friendly interface for all devices- **ASGI Server:** Uvicorn

- **Admin Interface**: Secure web-based administration panel with session-based authentication

- **RESTful API**: Complete REST API for integration with external systems- **ORM / Models:** SQLModel (SQLAlchemy)

### Advanced Features

- **Background Cleanup**: Automated cleanup of old records and maintenance- **Database:** SQLite (`pi_control.db` file)

- **Automatic Entry/Exit Detection**: System automatically determines if an RFID scan is an entry or exit based on last check-in state

- **Session Management**: Secure user authentication using session cookies with configurable expiration- **Authentication:** Starlette sessions + password hashing (passlib pbkdf2_sha256)

- **Data Validation**: Comprehensive input validation using Pydantic models ensuring data integrity

- **Responsive Design**: Mobile-friendly interface supporting tablets and smartphones for field access## 🛠 Technology Stack- **Templates:** Jinja2

- **RESTful API**: Complete REST API with OpenAPI documentation for third-party integrations

- **Background Maintenance**: Automated cleanup utilities for old records and database optimization- **Lightweight Frontend:** HTML/CSS and JavaScript for AJAX calls

- **Manual Override**: Support for manual check-in/out entries for special cases or corrections

### Backend- **Tests:** pytest + httpx TestClient

## Technology Stack

- **Framework**: FastAPI 0.121+ (Modern, fast Python web framework)

### Backend Components

- **Database**: SQLite with SQLModel ORM (Type-safe database operations)The project avoids heavy dependencies to facilitate installation on Raspberry Pi and resource-limited environments.

- **Framework**: FastAPI 0.95+ - Modern, high-performance Python web framework with automatic API documentation

- **Database**: SQLite - Serverless, self-contained SQL database engine- **Authentication**: Session-based with secure password hashing (passlib + bcrypt)

- **ORM**: SQLModel 0.0.8+ - Type-safe database operations combining SQLAlchemy and Pydantic

- **Authentication**: Passlib with bcrypt - Industry-standard password hashing and verification- **Validation**: Pydantic models for data validation## Requirements

- **Session Management**: itsdangerous 2.1.2+ - Cryptographically signed session cookies

- **ASGI Server**: Uvicorn with standard extras - High-performance async server implementation- **ASGI Server**: Uvicorn with performance optimizations

- **Validation**: Pydantic via FastAPI - Runtime type checking and data validation

- Raspberry Pi (optional for real deployment) or any Linux for development.

### Frontend Components

### Frontend- Python 3.10+ installed.

- **Template Engine**: Jinja2 - Full-featured template engine for Python

- **CSS Framework**: Custom responsive CSS with mobile-first design principles- **Template Engine**: Jinja2 with responsive HTML templates- Root privileges access to install systemd services (if applicable).

- **JavaScript**: Vanilla JavaScript for dynamic interactions and AJAX requests

- **Forms**: HTML5 forms with client-side and server-side validation- **CSS Framework**: Custom responsive CSS with mobile-first design



### System Integration- **JavaScript**: Vanilla JS for dynamic interactions## Installation (local / development)



- **Operating System**: Raspberry Pi OS (Debian-based) or compatible Linux distributions- **Forms**: HTML5 forms with client-side validation

- **Service Management**: systemd for automatic startup and process supervision

- **Process Management**: Background task handling with proper signal management1. Clone the repository and enter the folder:

- **Security**: Machine-ID validation for administrative recovery operations

### System Integration

## Requirements

- **Operating System**: Optimized for Raspberry Pi OS (Debian-based)```bash

### Hardware Requirements

- **Service Management**: systemd service integrationgit clone https://github.com/ismailhaddouche/PiControl.git

- **Raspberry Pi**: Model 3B+ or newer (Raspberry Pi 4 recommended for optimal performance)

- **Storage**: Minimum 8GB microSD card, Class 10 or better recommended- **Process Management**: Background task handlingcd PiControl

- **RFID Reader**: USB RFID reader compatible with EM4100/EM4102 protocol cards

- **Network**: Ethernet connection or Wi-Fi module for web interface access- **Security**: Machine-ID validation for admin reset functionality```

- **Power Supply**: Official Raspberry Pi power supply (5V 3A for Pi 4, 5V 2.5A for Pi 3)



### Software Requirements

## 📋 Requirements2. Create and activate a virtual environment:

#### Operating System

- Raspberry Pi OS (Bullseye or newer)

- Debian 11+ or Ubuntu 20.04+ on compatible ARM/x86 systems

- Linux kernel 5.4+ for optimal USB device support### Hardware Requirements```bash



#### Python Environment- **Raspberry Pi**: Pi 3B+ or newer (recommended Pi 4 for better performance)python3 -m venv .venv

- Python 3.8 or newer (Python 3.11+ recommended)

- pip package manager 21.0+- **Storage**: Minimum 8GB microSD card (Class 10 recommended)source .venv/bin/activate

- venv module for virtual environment creation

- **RFID Reader**: USB RFID reader compatible with EM4100/EM4102 cards```

#### System Packages

```bash- **Network**: Ethernet or Wi-Fi connectivity

sudo apt update

sudo apt install python3-pip python3-venv git sqlite3 build-essential3. Install dependencies:

```

### Software Requirements

### Python Dependencies

- **OS**: Raspberry Pi OS (Bullseye or newer) or compatible Debian-based system```bash

Core application dependencies (automatically installed via requirements.txt):

- **Python**: 3.8+ (3.11+ recommended for optimal performance)pip install --upgrade pip

```

fastapi>=0.95.0          # Web framework and API- **System Packages**: pip install -r requirements.txt

uvicorn[standard]>=0.22.0 # ASGI server with performance extras

sqlmodel>=0.0.8          # Database ORM and models  ```bash```

passlib[bcrypt]>=1.7.4   # Password hashing with bcrypt

python-multipart         # Form data and file upload support  sudo apt update

itsdangerous>=2.1.2      # Secure session cookie signing

httpx>=0.24.0            # HTTP client for testing  sudo apt install python3-pip python3-venv git sqlite34. Initialize and start the API (in development you can use reload):

pytest>=7.0.0            # Testing framework

pytest-asyncio>=0.21.0   # Async test support  ```

```

```bash

## Installation

### Python Dependenciesuvicorn app.main:app --reload

### Automatic Installation (Recommended)

All Python dependencies are managed via `requirements.txt`:```

#### Option 1: Direct Installation from GitHub

- `fastapi>=0.95.0` - Web framework

Download and execute the automated installer script:

- `uvicorn[standard]>=0.22.0` - ASGI server5. Open the browser at `http://127.0.0.1:8000/admin` to access the administration UI.

```bash

curl -sSL https://raw.githubusercontent.com/ismailhaddouche/PiControl/main/install/install_from_github.sh | bash- `sqlmodel>=0.0.8` - Database ORM

```

- `passlib[bcrypt]>=1.7.4` - Password hashing## Raspberry Pi Installation (automatic from GitHub)

This script will:

1. Clone the repository to `/opt/picontrol`- `python-multipart` - Form data handling

2. Create a Python virtual environment

3. Install all dependencies- `itsdangerous>=2.1.2` - Session securityThe repository includes utilities to install directly from GitHub and prepare the Pi:

4. Set up the systemd service

5. Initialize the database- `httpx>=0.24.0` - HTTP client for testing

6. Create the admin user

7. Start the service automatically- `pytest>=7.0.0` - Testing framework- `install/install_from_github.sh`: clones (or updates) the repo in `/opt/picontrol`, creates a virtualenv, installs dependencies, and runs the local installer.



#### Option 2: Local Installation- `install/pi_installer.sh`: installer that saves the `machine-id`, installs scripts in `/usr/local/bin`, creates a systemd service `picontrol-firstboot.service`, and creates a `.desktop` access for the desktop user.



Clone the repository and run the installer locally:## 🔧 Installation



```bashExample usage on Raspberry Pi (run as root):

git clone https://github.com/ismailhaddouche/PiControl.git

cd PiControl### Automatic Installation (Recommended)

chmod +x install/pi_installer.sh

sudo ./install/pi_installer.sh```bash

```

#### Option 1: Direct from GitHubsudo bash install/install_from_github.sh https://github.com/ismailhaddouche/PiControl.git main --user pi

### Manual Installation

```bash```

For development environments or custom installations:

# Download and run the installer

#### Step 1: Clone Repository

curl -sSL https://raw.githubusercontent.com/ismailhaddouche/PiControl/main/install/install_from_github.sh | bashImportant notes:

```bash

git clone https://github.com/ismailhaddouche/PiControl.git```- Review the scripts before running them as root. The installer places files in `/opt`, `/usr/local/bin` and creates/activates systemd services.

cd PiControl

```- The installer saves `/etc/machine-id` to `/var/lib/picontrol/machine-id` to allow the admin reset script to only run on the same machine.



#### Step 2: Create Virtual Environment#### Option 2: Clone and Install Locally



```bash```bash## Configuration

python3 -m venv .venv

source .venv/bin/activate# Clone the repository

```

git clone https://github.com/ismailhaddouche/PiControl.git- **First boot / setup:** the project includes a setup screen (`/admin/setup`) that allows creating the first administrator user if none exists.

#### Step 3: Install Dependencies

cd PiControl- **Admin password change:** from the `Configuration` UI you can change the admin password.

```bash

pip install --upgrade pip- **Time zone:** the configuration UI allows selecting a time zone and the server attempts to apply `timedatectl` (requires privileges).

pip install -r requirements.txt

```# Run the local installer- **Export/import DB:** from the configuration you can download the `pi_control.db` file or upload a copy to replace the database (restart recommended after import).



#### Step 4: Initialize Databasechmod +x install/pi_installer.sh



```bashsudo ./install/pi_installer.shSecurity and recovery:

python scripts/init_db.py

``````- Includes `tools/picontrol-reset-admin.sh` and `tools/reset_admin.py` to recover admin access on the same Raspberry Pi. The flow verifies the saved `machine-id` to prevent resets from another device.



The database will be created at the location specified by `PICONTROL_DB_DIR` environment variable (defaults to `/var/lib/picontrol`).- The reset script generates a secure password and saves it to `/var/lib/picontrol/reset_password.txt` with permissions 600. It's recommended to rotate or delete it after use.



#### Step 5: Create Admin User### Manual Installation



```bash## Basic Usage

python tools/reset_admin.py

```1. **Clone Repository**



This creates an admin user with a randomly generated password saved to `/var/lib/picontrol/reset_password.txt`.   ```bash- Adding employees, assigning RFID, and managing check-ins is done from the administration UI (`/admin`).



#### Step 6: Configure systemd Service (Optional)   git clone https://github.com/ismailhaddouche/PiControl.git- To simulate check-ins without a physical RFID reader, run `python simulador.py` in a terminal and type the `rfid_uid` you want to simulate.



For production deployments with automatic startup:   cd PiControl



```bash   ```Common endpoints:

sudo cp install/picontrol.service /etc/systemd/system/

sudo systemctl daemon-reload

sudo systemctl enable picontrol

sudo systemctl start picontrol2. **Create Virtual Environment**- `GET /admin` — main panel (requires login)

```

   ```bash- `POST /employees/` — create new employee

## Configuration

   python3 -m venv .venv- `GET /employees/` — list all employees

### Environment Variables

   source .venv/bin/activate- `PUT /employees/{id}/rfid` — assign/update RFID

Create a `.env` file in the project root or set system environment variables:

   ```- `DELETE /employees/{id}` — delete employee (archive)

```bash

# Database Configuration- `POST /employees/{id}/restore` — restore archived employee

PICONTROL_DB_DIR=/var/lib/picontrol

3. **Install Dependencies**

# Server Configuration

PICONTROL_HOST=0.0.0.0   ```bash## Project Structure

PICONTROL_PORT=8000

PICONTROL_WORKERS=1   pip install --upgrade pip



# Security Configuration   pip install -r requirements.txtRoot of the project and purpose of the most relevant files/directories:

SECRET_KEY=your-secure-random-secret-key-here

   ```

# Backup Configuration

PICONTROL_BACKUP_DIR=/var/backups/picontrol- `app/` — main application code



# Logging Configuration4. **Initialize Database**  - `main.py` — FastAPI entry point and middleware configuration

LOG_LEVEL=INFO

LOG_FILE=/var/log/picontrol/app.log   ```bash  - `models.py` — SQLModel models (Employee, CheckIn, User, Config)



# Session Configuration   python scripts/init_db.py  - `crud.py` — data access functions and logic (create employee, check-ins, archive/restore, config)

SESSION_LIFETIME=3600  # Session timeout in seconds

```   ```  - `db.py` — SQLite connection/engine utilities



### Database Configuration  - `routers/` — organized web/API routes (employees, checkins, web)



The application uses SQLite as its database backend:5. **Create Admin User**  - `templates/` — Jinja2 templates for web interface



- **Default Location**: `/var/lib/picontrol/pi_control.db`   ```bash  - `static/` — static CSS/JS for the UI

- **Configurable via**: `PICONTROL_DB_DIR` environment variable

- **Schema**: Automatically created on first run with tables: `employee`, `checkin`, `user`, `config`, `adminaction`   python tools/reset_admin.py

- **Permissions**: Ensure the application user has read/write access to the database directory

   ```- `simulador.py` — script that simulates RFID card reading (development mode)

Database connection string format:

```- `pi_control.db` — SQLite file (generated at runtime)

sqlite:///[PICONTROL_DB_DIR]/pi_control.db

```6. **Configure Service (Optional)**- `install/` — installation scripts and systemd service



### RFID Reader Configuration   ```bash  - `install_from_github.sh` — cloner/installer from GitHub



#### Hardware Setup   sudo cp install/picontrol.service /etc/systemd/system/  - `pi_installer.sh` — local installer that configures service / scripts



1. Connect the USB RFID reader to any available USB port on the Raspberry Pi   sudo systemctl daemon-reload  - `picontrol-firstboot.service` — systemd first boot unit

2. Verify device recognition:

   ```bash   sudo systemctl enable picontrol- `tools/` — utility scripts

   lsusb

   dmesg | grep -i usb   sudo systemctl start picontrol  - `picontrol-reset-admin.sh` — wrapper that validates machine-id and launches reset

   ```

   ```  - `reset_admin.py` — Python script that creates or resets admin account

3. Test reader functionality using the included simulator:

   ```bash

   python simulador.py

   ```## ⚙️ Configuration- `tests/` — automated tests (pytest)



#### Card Assignment- `requirements.txt` — Python dependencies



RFID cards are assigned to employees through the web interface:### Environment Variables- `README.md` — this file



1. Navigate to the Employee Management sectionCreate a `.env` file in the project root:

2. Select an employee or create a new one

3. Click "Assign RFID Card"```env## Tests

4. Scan the RFID card when prompted

5. The unique identifier will be automatically captured and stored# Database Configuration



### Network ConfigurationPICONTROL_DB_DIR=/var/lib/picontrolRun tests with:



#### Local Network Access



The application listens on all network interfaces by default (`0.0.0.0:8000`). Access the web interface from any device on the same network:# Server Configuration```bash



```PICONTROL_HOST=0.0.0.0source .venv/bin/activate

http://[raspberry-pi-ip]:8000

```PICONTROL_PORT=8000pytest -q



To find your Raspberry Pi's IP address:```

```bash

hostname -I# Security Configuration

ip addr show

```SECRET_KEY=your-secure-secret-key-here## Contributing



#### Firewall Configuration



If using a firewall, ensure port 8000 is accessible:# Backup ConfigurationIf you want to contribute, open an issue or pull request. Review style conventions and add tests for relevant changes.



```bashPICONTROL_BACKUP_DIR=/var/backups/picontrol

sudo ufw allow 8000/tcp

sudo ufw reload## License

```

# Log Configuration

## Usage

LOG_LEVEL=INFOThis project is distributed under the GNU General Public License v3.0 (GPL-3.0).

### Starting the Application

```

#### Development Mode

Quick summary (does not replace reading the full text):

Start the application with auto-reload for development:

### Database Setup

```bash

source .venv/bin/activateThe application automatically creates the database on first run:- You can use, copy and distribute this software for free.

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

```- **Location**: `/var/lib/picontrol/pi_control.db` (configurable via `PICONTROL_DB_DIR`)- If you publish or distribute a modified version of the code, you must do so under the same license (GPL-3.0). This means modifications must also be available as free software under the same terms.



#### Production Mode- **Schema**: Automatically created with English table names (`employee`, `checkin`, `user`, `config`)- See the `LICENSE` file for the full text of GPL-3.0 and legal details.



Using the systemd service (recommended):- **Permissions**: Ensure the application has read/write access to the database directory



```bashIf you include this project within another product (e.g., redistributing binaries or incorporating it into an image), make sure to comply with GPL-3.0 obligations (include license notices and provide source code of modifications under GPL-3.0).

# Start service

sudo systemctl start picontrol### RFID Configuration



# Stop service1. **Connect RFID Reader**: Plug USB RFID reader into Raspberry PiSPDX: MIT -> GPL-3.0-or-later

sudo systemctl stop picontrol

2. **Test Reader**: Use the simulator to test RFID functionality:

# Restart service

sudo systemctl restart picontrol   ```bash---



# Check status   python simulador.py

sudo systemctl status picontrol

   ```If you want me to add a section with quick administration commands (e.g. how to restart the service, view logs or force migrations), let me know and I'll include it.

# View logs

sudo journalctl -u picontrol -f3. **Configure Cards**: Assign RFID cards to employees through the web interface

```

## 🚀 Usage

### Web Interface

### Starting the Application

#### Accessing the Admin Panel

#### Development Mode

1. Open a web browser and navigate to `http://[raspberry-pi-ip]:8000````bash

2. Click "Admin Login" or navigate to `/admin/login`# Activate virtual environment

3. Enter admin credentialssource .venv/bin/activate

4. Access the administration dashboard

# Start development server

#### Employee Managementuvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

```

**Creating Employees:**

1. Navigate to "Employees" section#### Production Mode (systemd service)

2. Click "Add New Employee"```bash

3. Enter employee details (ID, name)# Start the service

4. Click "Save"sudo systemctl start picontrol



**Assigning RFID Cards:**# Check status

1. Select an employee from the listsudo systemctl status picontrol

2. Click "Assign RFID"

3. Scan the RFID card# View logs

4. Confirm assignmentsudo journalctl -u picontrol -f

```

**Archiving Employees:**

1. Select an employee### Web Interface

2. Click "Archive"1. **Access**: Navigate to `http://your-pi-ip:8000`

3. Confirm action2. **Login**: Use admin credentials (created during setup)

4. Employee is soft-deleted (data preserved, access removed)3. **Employee Management**: Add employees and assign RFID cards

4. **Time Tracking**: Employees can check in/out by scanning RFID cards

#### Time Tracking

### API Usage

**Viewing Check-ins:**

1. Navigate to "Check-ins" section#### Employee Management

2. Filter by date range or employee```bash

3. View entry/exit times and calculated hours# Create employee

curl -X POST "http://localhost:8000/employees/" \

**Manual Check-in Entry:**  -H "Content-Type: application/json" \

1. Navigate to "Manual Check-in"  -d '{"document_id": "EMP001", "name": "John Doe", "rfid_uid": "0123456789"}'

2. Select employee and type (entry/exit)

3. Optionally specify custom timestamp# List all employees

4. Submit entrycurl "http://localhost:8000/employees/"



#### Reports# Assign RFID to employee

curl -X PUT "http://localhost:8000/employees/EMP001/rfid" \

**Generating Work Hours Reports:**  -H "Content-Type: application/json" \

1. Navigate to "Reports" section  -d '{"rfid_uid": "0123456789"}'

2. Select employee```

3. Choose date range

4. Click "Generate Report"#### Time Tracking

5. View or export results```bash

# Create check-in (automatic entry/exit detection)

### API Usagecurl -X POST "http://localhost:8000/checkins/" \

  -H "Content-Type: application/json" \

The application provides a complete REST API for programmatic access.  -d '{"rfid_uid": "0123456789"}'



#### Authentication# Get employee check-ins

curl "http://localhost:8000/checkins/employee/EMP001"

API endpoints under `/admin/` require session-based authentication. First authenticate via web interface or login endpoint.

# Get hours worked report

#### Employee Management Endpointscurl "http://localhost:8000/reports/hours/EMP001?start_date=2025-01-01&end_date=2025-01-31"

```

**Create Employee**

```bash## 🔧 Maintenance

curl -X POST "http://localhost:8000/employees/" \

  -H "Content-Type: application/json" \### Regular Maintenance Tasks

  -d '{

    "document_id": "EMP001",#### Database Cleanup

    "name": "John Doe",```bash

    "rfid_uid": "AB12CD34EF56"# Clean old records (older than 4 years)

  }'python tools/cleanup_old_records.py --dry-run

```

# Execute cleanup (creates backup first)

**List All Employees**python tools/cleanup_old_records.py

```bash

curl "http://localhost:8000/employees/"# Clean old records and inactive employees

```python tools/cleanup_old_records.py --delete-employees

```

**Get Employee Details**

```bash#### Security Maintenance

curl "http://localhost:8000/employees/EMP001"```bash

```# Rotate secret key

python tools/rotate_secret.py

**Assign RFID to Employee**

```bash# Reset admin password (requires physical access to Pi)

curl -X PUT "http://localhost:8000/employees/EMP001/rfid" \sudo python tools/reset_admin.py

  -H "Content-Type: application/json" \```

  -d '{"rfid_uid": "AB12CD34EF56"}'

```#### System Maintenance

```bash

**Archive Employee**# Restart service

```bashsudo systemctl restart picontrol

curl -X DELETE "http://localhost:8000/employees/EMP001"

```# Check service logs

sudo journalctl -u picontrol --since "1 hour ago"

**Restore Archived Employee**

```bash# Update application

curl -X POST "http://localhost:8000/employees/EMP001/restore"cd /opt/picontrol

```git pull origin main

sudo systemctl restart picontrol

#### Time Tracking Endpoints```



**Create Check-in** (Automatic entry/exit detection)### Backup and Recovery

```bash

curl -X POST "http://localhost:8000/checkins/" \#### Database Backup

  -H "Content-Type: application/json" \```bash

  -d '{"rfid_uid": "AB12CD34EF56"}'# Manual backup

```cp /var/lib/picontrol/pi_control.db /var/backups/picontrol/backup_$(date +%Y%m%d_%H%M%S).db



**List Check-ins**# Automated backup (via cron)

```bash# Add to crontab: 0 2 * * * /opt/picontrol/tools/backup_db.sh

curl "http://localhost:8000/checkins/?limit=50&offset=0"```

```

#### System Backup

**Get Employee Check-ins**```bash

```bash# Backup entire configuration

curl "http://localhost:8000/checkins/employee/EMP001"tar -czf picontrol_backup.tar.gz \

```  /var/lib/picontrol \

  /etc/systemd/system/picontrol.service \

**Get Hours Worked Report**  /opt/picontrol

```bash```

curl "http://localhost:8000/reports/hours/EMP001?start_date=2025-01-01&end_date=2025-01-31"

```### Monitoring and Diagnostics



### RFID Simulator#### Health Checks

```bash

For development and testing without physical RFID hardware:# Check API health

curl http://localhost:8000/

```bash

python simulador.py# Check database connectivity

```python -c "from app.db import get_session; print('Database OK')"



The simulator:# Check RFID simulator

- Accepts RFID UIDs via keyboard inputpython simulador.py

- Sends check-in requests to the API```

- Displays server responses

- Useful for testing workflows without hardware#### Log Analysis

```bash

Type `exit` or `quit` to terminate the simulator.# Application logs

sudo journalctl -u picontrol -f

## API Documentation

# System resource usage

### Interactive Documentationhtop

df -h

The application includes automatically generated interactive API documentation:free -m



- **Swagger UI**: `http://[server]:8000/docs`# Network connectivity

  - Interactive API explorationss -tulpn | grep :8000

  - Try-it-out functionality for all endpoints```

  - Request/response schema documentation

### Troubleshooting

- **ReDoc**: `http://[server]:8000/redoc`

  - Alternative documentation format#### Common Issues

  - Clean, readable interface

  - Searchable endpoint reference1. **Database Permission Errors**

   ```bash

### API Endpoint Reference   sudo chown -R picontrol:picontrol /var/lib/picontrol

   sudo chmod 755 /var/lib/picontrol

#### Employee Management   ```



| Method | Endpoint | Description | Authentication |2. **Service Won't Start**

|--------|----------|-------------|----------------|   ```bash

| POST | `/employees/` | Create new employee | No |   sudo systemctl status picontrol

| GET | `/employees/` | List all employees | No |   sudo journalctl -u picontrol --no-pager

| GET | `/employees/{id}` | Get employee details | No |   ```

| PUT | `/employees/{id}/rfid` | Assign RFID card | No |

| DELETE | `/employees/{id}` | Archive employee | No |3. **RFID Reader Not Detected**

| POST | `/employees/{id}/restore` | Restore archived employee | No |   ```bash

   lsusb | grep -i rfid

#### Time Tracking   dmesg | tail -20

   ```

| Method | Endpoint | Description | Authentication |

|--------|----------|-------------|----------------|4. **Port Already in Use**

| POST | `/checkins/` | Create check-in record | No |   ```bash

| GET | `/checkins/` | List check-in records | No |   sudo ss -tulpn | grep :8000

| GET | `/checkins/employee/{id}` | Get employee check-ins | No |   sudo systemctl stop picontrol

| GET | `/reports/hours/{id}` | Get hours worked report | No |   ```



#### Administration## 🧪 Testing



| Method | Endpoint | Description | Authentication |### Running Tests

|--------|----------|-------------|----------------|```bash

| GET | `/admin/` | Admin dashboard | Yes |# Activate virtual environment

| POST | `/admin/login` | Admin login | No |source .venv/bin/activate

| POST | `/admin/logout` | Admin logout | Yes |

| GET | `/admin/employees` | Employee management UI | Yes |# Run all tests

| POST | `/admin/employees` | Create/update employee | Yes |PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest -v

| GET | `/admin/checkins` | Check-in management UI | Yes |

| POST | `/admin/checkins/manual` | Manual check-in entry | Yes |# Run with coverage

| GET | `/admin/reports` | Reports interface | Yes |PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest --cov=app tests/

| GET | `/admin/configuration` | System configuration | Yes |

# Run specific test

## MaintenancePYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest tests/test_api.py::test_create_employee_and_checkin

```

### Regular Maintenance Tasks

### Manual Testing

#### Database Cleanup```bash

# Test RFID simulation

Remove old records to maintain optimal database performance:python simulador.py



**Preview Cleanup** (Dry run, no changes made):# Test API endpoints

```bashcurl http://localhost:8000/docs  # Swagger documentation

python tools/cleanup_old_records.py --dry-run```

```

## 📁 Project Structure

**Execute Cleanup** (Creates automatic backup):

```bash```

python tools/cleanup_old_records.pyPiControl/

```├── app/                          # Main application code

│   ├── __init__.py

**Cleanup with Employee Deletion**:│   ├── main.py                   # FastAPI application entry point

```bash│   ├── models.py                 # Database models (Employee, CheckIn, User, Config)

python tools/cleanup_old_records.py --delete-employees│   ├── crud.py                   # Database operations and business logic

```│   ├── db.py                     # Database connection and session management

│   ├── routers/                  # API route handlers

Default retention: 4 years + 1 day. Records older than this threshold are permanently deleted.│   │   ├── __init__.py

│   │   ├── employees.py          # Employee management endpoints

#### Security Maintenance│   │   ├── checkins.py           # Time tracking endpoints

│   │   └── web.py                # Web interface routes

**Rotate Secret Key**:│   ├── templates/                # Jinja2 HTML templates

```bash│   │   ├── base.html             # Base template with common layout

python tools/rotate_secret.py│   │   ├── login.html            # Admin login page

```│   │   ├── menu.html             # Main navigation menu

This generates a new secret key and updates the configuration. All users will need to re-authenticate.│   │   ├── employees.html        # Employee management interface

│   │   ├── checkins.html         # Check-in/out interface

**Reset Admin Password** (Requires physical access to Raspberry Pi):│   │   ├── reports.html          # Time reports interface

```bash│   │   └── configuration.html    # System configuration

sudo python tools/reset_admin.py│   └── static/                   # Static assets (CSS, JS)

```│       ├── style.css             # Main stylesheet

Generates a secure random password and saves it to `/var/lib/picontrol/reset_password.txt`.│       └── app.js                # JavaScript functionality

├── install/                      # Installation scripts

#### System Maintenance│   ├── install_from_github.sh    # GitHub installer

│   ├── pi_installer.sh           # Local installer

**Restart Application Service**:│   └── picontrol.service         # systemd service definition

```bash├── tools/                        # Utility scripts

sudo systemctl restart picontrol│   ├── cleanup_old_records.py    # Database cleanup utility

```│   ├── reset_admin.py            # Admin password reset

│   ├── rotate_secret.py          # Security key rotation

**View Recent Logs**:│   └── picontrol-*.sh            # System management scripts

```bash├── tests/                        # Test suite

sudo journalctl -u picontrol --since "1 hour ago"│   └── test_api.py               # API endpoint tests

```├── scripts/                      # Setup scripts

│   └── init_db.py               # Database initialization

**Update Application**:├── simulador.py                  # RFID simulator for development/testing

```bash├── requirements.txt              # Python dependencies

cd /opt/picontrol├── README.md                     # This documentation

git pull origin main├── LICENSE                       # GPL-3.0 license

source .venv/bin/activate└── SECURITY_GUIDELINES.md        # Security best practices

pip install -r requirements.txt```

sudo systemctl restart picontrol

```## 🔒 Security



### Backup and Recovery### Authentication & Authorization

- **Session-based Authentication**: Secure session cookies with CSRF protection

#### Database Backup- **Password Security**: bcrypt hashing with salt for admin accounts

- **Machine ID Validation**: Physical access required for admin reset functionality

**Manual Backup**:

```bash### Data Protection

# Create timestamped backup- **Input Validation**: All user inputs validated and sanitized

sudo cp /var/lib/picontrol/pi_control.db \- **SQL Injection Prevention**: Parameterized queries via SQLModel

  /var/backups/picontrol/backup_$(date +%Y%m%d_%H%M%S).db- **XSS Protection**: Template auto-escaping and CSP headers

```

### Network Security

**Automated Backup** (via cron):- **HTTPS Support**: SSL/TLS configuration for production deployment

```bash- **CORS Configuration**: Controlled cross-origin resource sharing

# Edit crontab- **Rate Limiting**: Built-in protection against abuse

sudo crontab -e

### System Security

# Add daily backup at 2 AM- **Service Isolation**: Dedicated user account for application service

0 2 * * * cp /var/lib/picontrol/pi_control.db /var/backups/picontrol/backup_$(date +\%Y\%m\%d).db- **File Permissions**: Restricted database and configuration file access

```- **Log Security**: Sensitive data excluded from logs



**Restore from Backup**:## 📄 API Documentation

```bash

# Stop service### Interactive Documentation

sudo systemctl stop picontrolOnce the application is running, access the interactive API documentation:

- **Swagger UI**: `http://your-server:8000/docs`

# Restore database- **ReDoc**: `http://your-server:8000/redoc`

sudo cp /var/backups/picontrol/backup_20250101.db \

  /var/lib/picontrol/pi_control.db### Key Endpoints



# Restart service#### Employee Management

sudo systemctl start picontrol- `POST /employees/` - Create new employee

```- `GET /employees/` - List all employees  

- `GET /employees/{employee_id}` - Get employee details

#### System Configuration Backup- `PUT /employees/{employee_id}/rfid` - Assign RFID card

- `DELETE /employees/{employee_id}` - Archive employee

**Complete System Backup**:- `POST /employees/{employee_id}/restore` - Restore archived employee

```bash

sudo tar -czf picontrol_backup_$(date +%Y%m%d).tar.gz \#### Time Tracking  

  /var/lib/picontrol \- `POST /checkins/` - Create check-in/out record

  /etc/systemd/system/picontrol.service \- `GET /checkins/` - List check-in records

  /opt/picontrol- `GET /checkins/employee/{employee_id}` - Get employee's check-ins

```- `GET /reports/hours/{employee_id}` - Get hours worked report



**Restore System Configuration**:#### Administration

```bash- `GET /admin/` - Admin dashboard (requires authentication)

sudo tar -xzf picontrol_backup_20250101.tar.gz -C /- `POST /admin/login` - Admin login

sudo systemctl daemon-reload- `POST /admin/logout` - Admin logout

sudo systemctl restart picontrol- `GET /admin/employees` - Employee management interface

```- `GET /admin/checkins` - Check-in management interface



### Monitoring and Diagnostics## 🤝 Contributing



#### Health ChecksWe welcome contributions to improve PiControl! Please follow these guidelines:



**Check Application Status**:### Development Setup

```bash1. Fork the repository

sudo systemctl status picontrol2. Create a feature branch: `git checkout -b feature/new-feature`

```3. Install development dependencies: `pip install -r requirements-dev.txt`

4. Make your changes and add tests

**Verify API Accessibility**:5. Run tests: `pytest`

```bash6. Submit a pull request

curl http://localhost:8000/

```### Code Standards

- **Python Style**: Follow PEP 8 guidelines

**Check Database Connectivity**:- **Type Hints**: Use type hints for all functions

```bash- **Documentation**: Update docstrings and README as needed

python -c "from app.db import get_session; next(get_session()); print('Database OK')"- **Testing**: Add tests for new functionality

```

### Reporting Issues

**Test RFID Functionality**:- Use GitHub Issues to report bugs or request features

```bash- Include system information (OS, Python version, etc.)

python simulador.py- Provide steps to reproduce the issue

```- Include relevant log output



#### Log Analysis## 📜 License



**Real-time Log Monitoring**:This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

```bash

sudo journalctl -u picontrol -f### Summary

```- ✅ **Use**: Free to use, copy, and distribute

- ✅ **Modify**: Free to modify and create derivative works  

**Search Logs for Errors**:- ✅ **Distribute**: Free to distribute original and modified versions

```bash- ⚠️ **Copyleft**: Modified versions must also be licensed under GPL-3.0

sudo journalctl -u picontrol | grep -i error- ⚠️ **Source Code**: Must provide source code when distributing

```

### Commercial Use

**Export Logs to File**:GPL-3.0 allows commercial use, but any modifications or derivative works must also be released under GPL-3.0. For commercial deployments, ensure compliance with the license terms.

```bash

sudo journalctl -u picontrol --since "7 days ago" > picontrol_logs.txtSee the [LICENSE](LICENSE) file for the complete license text.

```

## 🙏 Acknowledgments

#### System Resource Monitoring

- Built with [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

**CPU and Memory Usage**:- Database management via [SQLModel](https://sqlmodel.tiangolo.com/) - SQLAlchemy with Pydantic

```bash- Inspired by modern time tracking solutions and Raspberry Pi IoT projects

top -p $(pgrep -f "uvicorn app.main:app")- Thanks to the open-source community for the excellent tools and libraries

```

## 📞 Support

**Disk Usage**:

```bash### Community Support

df -h /var/lib/picontrol- **GitHub Issues**: [Report bugs and request features](https://github.com/ismailhaddouche/PiControl/issues)

du -sh /var/lib/picontrol/*- **Discussions**: [Community discussions and Q&A](https://github.com/ismailhaddouche/PiControl/discussions)

```

### Documentation

**Network Connections**:- **API Docs**: Available at `/docs` when application is running

```bash- **Code Documentation**: Inline docstrings and type hints throughout codebase

sudo ss -tulpn | grep :8000- **Security Guidelines**: See [SECURITY_GUIDELINES.md](SECURITY_GUIDELINES.md)

```

---

### Troubleshooting

**PiControl** - Modern employee time tracking for the Raspberry Pi era 🥧⏰
#### Common Issues and Solutions

**1. Database Permission Errors**

Symptoms: `sqlite3.OperationalError: unable to open database file`

Solution:
```bash
sudo chown -R picontrol:picontrol /var/lib/picontrol
sudo chmod 755 /var/lib/picontrol
sudo chmod 644 /var/lib/picontrol/pi_control.db
```

**2. Service Fails to Start**

Symptoms: Service shows "failed" status

Diagnosis:
```bash
sudo systemctl status picontrol
sudo journalctl -u picontrol --no-pager -n 50
```

Common causes:
- Missing dependencies: Reinstall requirements
- Port already in use: Check for conflicting processes
- Database corruption: Restore from backup

**3. RFID Reader Not Detected**

Symptoms: RFID scans not registering

Diagnosis:
```bash
lsusb | grep -i rfid
dmesg | tail -30
```

Solutions:
- Verify USB connection
- Check device permissions: `ls -l /dev/ttyUSB*`
- Test with simulator first

**4. Port Already in Use**

Symptoms: `Address already in use` error

Solution:
```bash
# Find process using port 8000
sudo lsof -i :8000
sudo ss -tulpn | grep :8000

# Stop conflicting service
sudo systemctl stop picontrol

# Or kill specific process
sudo kill -9 [PID]
```

**5. High Memory Usage**

Symptoms: System slowdown, out of memory errors

Solutions:
```bash
# Restart service to clear memory
sudo systemctl restart picontrol

# Check for database size issues
du -h /var/lib/picontrol/pi_control.db

# Run cleanup if database is large
python tools/cleanup_old_records.py
```

**6. Cannot Access Web Interface**

Symptoms: Cannot reach `http://[pi-ip]:8000`

Diagnosis:
```bash
# Check if service is running
sudo systemctl status picontrol

# Check firewall rules
sudo ufw status

# Verify network connectivity
ping [pi-ip]
```

Solutions:
- Ensure service is running: `sudo systemctl start picontrol`
- Open firewall port: `sudo ufw allow 8000/tcp`
- Verify correct IP address: `hostname -I`

## Testing

### Running Tests

#### Complete Test Suite

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests with verbose output
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest -v

# Run tests with coverage report
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest --cov=app --cov-report=html tests/

# View coverage report
open htmlcov/index.html
```

#### Specific Test Execution

```bash
# Run specific test file
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest tests/test_api.py -v

# Run specific test function
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest tests/test_api.py::test_create_employee_and_checkin -v

# Run tests matching pattern
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest -k "employee" -v
```

### Manual Testing

#### RFID Simulation Testing

```bash
# Start simulator
python simulador.py

# Test check-in flow
# 1. Enter RFID UID when prompted
# 2. Verify "entry" response
# 3. Enter same UID again
# 4. Verify "exit" response
```

#### API Endpoint Testing

**Using curl:**
```bash
# Test employee creation
curl -X POST "http://localhost:8000/employees/" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "TEST001", "name": "Test User"}'

# Test check-in
curl -X POST "http://localhost:8000/checkins/" \
  -H "Content-Type: application/json" \
  -d '{"rfid_uid": "TEST123"}'
```

**Using Interactive Documentation:**
1. Navigate to `http://localhost:8000/docs`
2. Expand endpoint sections
3. Click "Try it out"
4. Enter parameters
5. Execute and view responses

### Test Database

Tests use an isolated database to avoid affecting production data:

```bash
# Specify test database location
export PICONTROL_DB_DIR=./test_db

# Run tests
pytest

# Clean test database
rm -rf ./test_db
```

## Project Structure

```
PiControl/
│
├── app/                          # Main application code
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   ├── models.py                # SQLModel database models
│   ├── crud.py                  # Database operations and business logic
│   ├── db.py                    # Database connection management
│   │
│   ├── routers/                 # API route handlers
│   │   ├── __init__.py
│   │   ├── employees.py         # Employee management endpoints
│   │   ├── checkins.py          # Time tracking endpoints
│   │   └── web.py               # Web interface routes
│   │
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── base.html            # Base template with layout
│   │   ├── login.html           # Admin login page
│   │   ├── menu.html            # Navigation menu
│   │   ├── setup.html           # Initial setup wizard
│   │   ├── employees.html       # Employee management interface
│   │   ├── employees_archived.html  # Archived employees view
│   │   ├── employee_history.html    # Employee check-in history
│   │   ├── checkins.html        # Check-in management interface
│   │   ├── reports.html         # Reports interface
│   │   ├── reports_result.html  # Report results display
│   │   ├── configuration.html   # System configuration
│   │   └── admin_logs.html      # Admin action logs
│   │
│   └── static/                  # Static assets
│       ├── style.css            # Main stylesheet
│       └── app.js               # JavaScript functionality
│
├── install/                     # Installation scripts
│   ├── install_from_github.sh   # GitHub automated installer
│   ├── pi_installer.sh          # Local installation script
│   ├── picontrol.service        # systemd service definition
│   ├── picontrol-firstboot.service  # First boot setup service
│   ├── cleanup_picontrol.service    # Cleanup service definition
│   └── cleanup_picontrol.timer      # Cleanup timer definition
│
├── tools/                       # Utility scripts
│   ├── cleanup_old_records.py   # Database cleanup utility
│   ├── reset_admin.py           # Admin password reset
│   ├── rotate_secret.py         # Secret key rotation
│   ├── picontrol-cleanup.sh     # Cleanup wrapper script
│   ├── picontrol-firstboot.sh   # First boot setup script
│   ├── picontrol-firstboot-gui.sh   # GUI version of firstboot
│   ├── picontrol-reset-admin.sh     # Admin reset wrapper
│   ├── picontrol-reset-admin-gui.sh # GUI version of reset
│   ├── picontrol-restart.sh     # Service restart script
│   ├── picontrol-restart-gui.sh # GUI version of restart
│   ├── picontrol-rotate-secret.sh   # Secret rotation wrapper
│   └── picontrol-rotate-secret-gui.sh  # GUI version of rotate
│
├── tests/                       # Test suite
│   ├── __init__.py
│   └── test_api.py             # API endpoint tests
│
├── scripts/                     # Setup scripts
│   └── init_db.py              # Database initialization
│
├── simulador.py                 # RFID simulator for development
├── requirements.txt             # Python dependencies
├── README.md                    # This documentation
├── LICENSE                      # GPL-3.0 license
└── SECURITY_GUIDELINES.md       # Security best practices
```

### Key Components

**Application Core (`app/`)**
- `main.py`: FastAPI application setup, middleware configuration, route registration
- `models.py`: Database table definitions using SQLModel
- `crud.py`: Business logic and database operations
- `db.py`: Database engine and session management

**API Routes (`app/routers/`)**
- `employees.py`: Employee CRUD operations
- `checkins.py`: Time tracking and reporting
- `web.py`: Web interface and admin panel

**Templates (`app/templates/`)**
- Jinja2 templates for web interface
- Responsive HTML with server-side rendering
- Form handling and data display

**Installation (`install/`)**
- Automated installation scripts
- systemd service configurations
- First-boot setup utilities

**Utilities (`tools/`)**
- Maintenance and administrative scripts
- Database cleanup and optimization
- Security management tools

## Security

### Authentication and Authorization

**Session-based Authentication**
- Secure session cookies with cryptographic signing
- Configurable session timeout
- Automatic session invalidation on logout
- CSRF protection via session tokens

**Password Security**
- bcrypt hashing algorithm with salt
- Configurable work factor for hash computation
- Secure password generation for admin accounts
- Password stored only as irreversible hash

**Access Control**
- Admin panel requires authentication
- Public API endpoints for RFID check-ins
- Role-based access (admin vs. regular user)
- Physical device validation for admin reset

### Data Protection

**Input Validation**
- Pydantic model validation for all inputs
- Type checking at runtime
- Length limits on text fields
- Format validation for IDs and UIDs

**SQL Injection Prevention**
- Parameterized queries via SQLModel ORM
- No raw SQL string concatenation
- Automatic query sanitization
- Prepared statement usage

**XSS Protection**
- Jinja2 template auto-escaping
- Content Security Policy headers
- Input sanitization for display
- HTML entity encoding

### Network Security

**HTTPS Support**
- SSL/TLS certificate configuration
- Redirect HTTP to HTTPS
- Secure cookie flags (Secure, HttpOnly)
- HSTS header support

**CORS Configuration**
- Controlled cross-origin resource sharing
- Whitelist allowed origins
- Credential handling restrictions
- Preflight request validation

**Rate Limiting**
- Request throttling capabilities
- IP-based rate limits
- Protection against brute force attacks
- Automatic temporary blocking

### System Security

**Service Isolation**
- Dedicated system user for service
- Restricted file permissions
- Minimal privilege principle
- Separate database directory

**File Permissions**
- Database: 644 (read/write owner only)
- Configuration: 600 (owner access only)
- Logs: 640 (owner + group read)
- Executables: 755 (owner write, all execute)

**Audit Logging**
- Admin action logging to database
- Timestamped security events
- User authentication tracking
- Configuration change records

### Security Best Practices

1. **Change Default Credentials**: Always change the default admin password after installation
2. **Use Strong Passwords**: Generate complex passwords with sufficient entropy
3. **Regular Updates**: Keep system and dependencies updated with security patches
4. **Network Isolation**: Place on isolated network segment if possible
5. **Firewall Configuration**: Only expose necessary ports
6. **Regular Backups**: Maintain encrypted backups of database
7. **Monitor Logs**: Regularly review logs for suspicious activity
8. **Secret Rotation**: Periodically rotate secret keys and passwords
9. **Physical Security**: Restrict physical access to Raspberry Pi device
10. **HTTPS Only**: Use HTTPS in production environments

## Contributing

We welcome contributions to improve PiControl. Please follow these guidelines to ensure a smooth contribution process.

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork via GitHub web interface
   # Clone your fork
   git clone https://github.com/[your-username]/PiControl.git
   cd PiControl
   ```

2. **Create Development Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set Up Development Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Development Database**
   ```bash
   export PICONTROL_DB_DIR=./dev_db
   python scripts/init_db.py
   ```

### Making Changes

1. **Write Code**
   - Follow PEP 8 style guidelines
   - Add type hints to all functions
   - Write docstrings for modules, classes, and functions
   - Keep functions focused and concise

2. **Add Tests**
   - Write tests for new functionality
   - Ensure existing tests still pass
   - Aim for high code coverage
   - Test edge cases and error conditions

3. **Run Tests**
   ```bash
   PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest -v
   ```

4. **Update Documentation**
   - Update README if adding features
   - Add docstrings to new code
   - Update API documentation if needed
   - Include usage examples

### Code Standards

**Python Style**
- Follow PEP 8 guidelines
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use meaningful variable names
- Add comments for complex logic

**Type Hints**
```python
def create_employee(
    document_id: str,
    name: str,
    rfid_uid: Optional[str] = None
) -> Employee:
    """Create a new employee record."""
    pass
```

**Docstrings**
```python
def calculate_hours_worked(
    employee_id: str,
    start_date: datetime,
    end_date: datetime
) -> float:
    """
    Calculate total hours worked by an employee in a date range.
    
    Args:
        employee_id: Unique employee identifier
        start_date: Start of calculation period
        end_date: End of calculation period
        
    Returns:
        Total hours worked as float
        
    Raises:
        ValueError: If date range is invalid
        EmployeeNotFoundError: If employee doesn't exist
    """
    pass
```

### Submitting Changes

1. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```

2. **Push to Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Go to GitHub repository
   - Click "New Pull Request"
   - Describe changes thoroughly
   - Link related issues
   - Request review

### Pull Request Guidelines

**Title Format**
```
[Type] Brief description

Types: Feature, Fix, Docs, Refactor, Test, Chore
Example: [Feature] Add employee search functionality
```

**Description Template**
```markdown
## Description
Brief description of changes

## Changes Made
- List of specific changes
- Technical details
- Implementation notes

## Testing
- Tests added/modified
- Manual testing performed
- Edge cases considered

## Documentation
- README updates
- API documentation changes
- Code comments added

## Related Issues
Fixes #123
Related to #456
```

### Reporting Issues

Use GitHub Issues for bug reports and feature requests.

**Bug Report Template**
```markdown
## Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Raspberry Pi OS Bullseye
- Python Version: 3.11
- Application Version: 1.0.0

## Logs
Relevant log output or error messages

## Additional Context
Any other relevant information
```

**Feature Request Template**
```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?
Who would benefit?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches evaluated

## Additional Context
Mockups, examples, references
```

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

### Summary

- **Freedom to Use**: You can use this software for any purpose, including commercial use
- **Freedom to Study**: You can examine and modify the source code
- **Freedom to Share**: You can distribute copies of the original software
- **Freedom to Improve**: You can distribute modified versions

### Copyleft Requirements

- **Share Alike**: Modified versions must also be licensed under GPL-3.0
- **Source Code**: You must provide source code when distributing the software
- **License Notice**: You must include the GPL-3.0 license text
- **State Changes**: You must document significant modifications

### Commercial Use

GPL-3.0 permits commercial use with the following conditions:

1. Any modifications or derivative works must be released under GPL-3.0
2. Source code must be made available to users
3. License and copyright notices must be preserved
4. Installation information must be provided for hardware products

### Warranty Disclaimer

This software is provided "as is", without warranty of any kind, express or implied. See the LICENSE file for complete terms and conditions.

### License Text

See the [LICENSE](LICENSE) file for the complete GNU General Public License v3.0 text.

## Support

### Community Support

**GitHub Issues**
- Report bugs: [Issue Tracker](https://github.com/ismailhaddouche/PiControl/issues)
- Request features: [Feature Requests](https://github.com/ismailhaddouche/PiControl/issues/new?labels=enhancement)
- Search existing issues before creating new ones

**GitHub Discussions**
- Ask questions: [Q&A Section](https://github.com/ismailhaddouche/PiControl/discussions)
- Share ideas: [Ideas Category](https://github.com/ismailhaddouche/PiControl/discussions/categories/ideas)
- Show your setup: [Show and Tell](https://github.com/ismailhaddouche/PiControl/discussions/categories/show-and-tell)

### Documentation

**Online Documentation**
- API Documentation: Available at `/docs` when application is running
- Alternative format: Available at `/redoc` when application is running

**Code Documentation**
- Inline docstrings throughout codebase
- Type hints for all public functions
- Comments explaining complex logic

**Additional Resources**
- [SECURITY_GUIDELINES.md](SECURITY_GUIDELINES.md): Security best practices
- Installation guides in `install/` directory
- Tool documentation in `tools/` directory

### Getting Help

When seeking help, please provide:

1. **System Information**
   - Operating system and version
   - Python version
   - Application version or commit hash

2. **Problem Description**
   - What you were trying to do
   - What you expected to happen
   - What actually happened

3. **Steps to Reproduce**
   - Detailed steps to recreate the issue
   - Any relevant configuration

4. **Logs and Error Messages**
   - Complete error messages
   - Relevant log output
   - Stack traces if applicable

### Professional Support

For commercial deployments requiring professional support, customization, or consulting services, please contact the maintainers through GitHub.

---

**PiControl** - Professional Employee Time Tracking for Raspberry Pi

Copyright (C) 2025 - Licensed under GPL-3.0