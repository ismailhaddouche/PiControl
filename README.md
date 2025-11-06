# PiControl

**Professional Employee Time Tracking System for Raspberry Pi**

A modern, web-based time tracking solution designed for Raspberry Pi with RFID card support. Built with FastAPI and SQLite, featuring a responsive administration interface and automated check-in/check-out functionality.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-00a393.svg)](https://fastapi.tiangolo.com)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Components](#system-components)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Maintenance](#maintenance)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## Overview

PiControl is a lightweight employee time tracking application optimized for Raspberry Pi devices. It uses RFID technology for contactless check-in/check-out operations and provides a comprehensive web-based administration panel for employee management, reporting, and system configuration.

The system automatically determines whether an RFID scan represents an entry or exit based on the employee's last recorded activity, calculates work hours across complex scenarios (including midnight crossings), and provides detailed reporting capabilities. All data is stored locally in SQLite with support for archiving, restoration, and data export.

**Key Highlights:**
- Zero-touch check-in/out via RFID cards
- Intelligent automatic entry/exit detection
- Real-time dashboard with live activity feed
- Comprehensive time reporting with daily breakdowns
- Secure admin panel with session-based authentication
- Complete REST API for third-party integrations
- Raspberry Pi optimized with minimal dependencies

---

## Features

### Core Functionality

- **RFID-Based Time Tracking**: Automatic employee check-in/out using RFID cards with intelligent entry/exit detection
- **Employee Management**: Complete CRUD operations for employee records with soft delete functionality
- **Real-Time Dashboard**: Live view of employee status, recent activity, and current work sessions
- **Time Reports**: Detailed work hours calculation with customizable date ranges and per-day breakdowns
- **Archive System**: Soft delete functionality preserving historical data while removing active employee access
- **Admin Interface**: Secure web-based administration panel with session-based authentication

### Advanced Capabilities

- **Automatic Entry/Exit Detection**: System determines if an RFID scan is an entry or exit based on last check-in state
- **Midnight Crossing Calculations**: Accurate hour calculations for shifts that span multiple days
- **Manual Override**: Support for manual check-in/out entries for corrections or special cases
- **Session Management**: Secure user authentication using cryptographically signed session cookies
- **Data Validation**: Comprehensive input validation using Pydantic models ensuring data integrity
- **Responsive Design**: Mobile-friendly interface supporting tablets and smartphones
- **RESTful API**: Complete REST API with OpenAPI documentation for third-party integrations
- **Background Maintenance**: Automated cleanup utilities for old records and database optimization
- **Admin Audit Logs**: Comprehensive logging of administrative actions for accountability
- **RFID Simulator**: Development tool for testing workflows without physical hardware

---

## Technology Stack

### Backend Components

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.95+ | Modern async web framework with automatic API documentation |
| **Database** | SQLite | 3.x | Serverless, self-contained SQL database |
| **ORM** | SQLModel | 0.0.8+ | Type-safe database operations combining SQLAlchemy and Pydantic |
| **ASGI Server** | Uvicorn | 0.22+ | High-performance async server with standard extras |
| **Authentication** | Passlib | 1.7.4+ | Industry-standard password hashing with bcrypt |
| **Sessions** | itsdangerous | 2.1.2+ | Cryptographically signed session cookies |
| **Validation** | Pydantic | via FastAPI | Runtime type checking and data validation |

### Frontend Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Template Engine** | Jinja2 | Server-side HTML rendering |
| **CSS** | Custom Responsive CSS | Mobile-first design with responsive layouts |
| **JavaScript** | Vanilla JavaScript | Dynamic interactions and AJAX requests |
| **Forms** | HTML5 Forms | Client-side and server-side validation |

### System Integration

| Component | Purpose |
|-----------|---------|
| **Operating System** | Raspberry Pi OS (Debian-based) or compatible Linux |
| **Service Management** | systemd for automatic startup and supervision |
| **Process Management** | Background task handling with signal management |
| **Security** | Machine-ID validation for administrative recovery |
| **RFID Hardware** | USB RFID readers (EM4100/EM4102 compatible) |

---

## System Components

### Application Structure

```
PiControl/
├── app/                          # Main application code
│   ├── main.py                   # FastAPI application entry point
│   ├── models.py                 # Database models (Employee, CheckIn, User, Config, AdminAction)
│   ├── crud.py                   # Database operations and business logic
│   ├── db.py                     # Database connection and session management
│   ├── routers/                  # API route handlers
│   │   ├── employees.py          # Employee management endpoints
│   │   ├── checkins.py           # Time tracking endpoints
│   │   └── web.py                # Web interface routes and admin panel
│   ├── templates/                # Jinja2 HTML templates
│   └── static/                   # CSS and JavaScript assets
├── install/                      # Installation scripts and systemd services
├── tools/                        # Utility scripts for maintenance and recovery
├── scripts/                      # Database initialization scripts
├── tests/                        # Test suite
└── simulador.py                  # RFID simulator for development
```

### Key Scripts and Tools

#### Installation Scripts (`install/`)
- **`install_from_github.sh`**: Automated installer that clones repository and runs local installer
- **`pi_installer.sh`**: Main installation script that sets up virtual environment, systemd services, and system integration
- **`picontrol.service`**: systemd service definition for automatic startup
- **`cleanup_picontrol.service`** & **`cleanup_picontrol.timer`**: Automated database cleanup service

#### Maintenance Tools (`tools/`)
- **`cleanup_old_records.py`**: Database cleanup utility for removing old records (default: 4 years retention)
- **`reset_admin.py`**: Admin password reset tool (requires physical access to device)
- **`rotate_secret.py`**: Secret key rotation for enhanced security
- **`picontrol-restart.sh`**: Service restart wrapper with proper privilege handling
- **GUI variants**: Desktop-friendly versions of maintenance tools with graphical feedback

#### Database Scripts (`scripts/`)
- **`init_db.py`**: Database initialization and schema creation

---

## Requirements

### Hardware Requirements

| Component | Specification | Notes |
|-----------|---------------|-------|
| **Raspberry Pi** | Pi 3B+ or newer | Pi 4 recommended for optimal performance |
| **Storage** | 8GB+ microSD card | Class 10 or UHS-I recommended |
| **RFID Reader** | USB RFID reader | EM4100/EM4102 protocol compatible |
| **Network** | Ethernet or Wi-Fi | For web interface access |
| **Power Supply** | Official Pi PSU | 5V 3A for Pi 4, 5V 2.5A for Pi 3 |

### Software Requirements

#### Operating System
- Raspberry Pi OS (Bullseye or newer)
- Debian 11+ or Ubuntu 20.04+ on compatible ARM/x86 systems
- Linux kernel 5.4+ recommended for optimal USB support

#### Python Environment
- Python 3.8 or newer (Python 3.11+ recommended)
- pip package manager 21.0+
- venv module for virtual environments

#### System Packages
```bash
sudo apt update
sudo apt install python3-pip python3-venv git sqlite3 build-essential
```

### Python Dependencies

Core dependencies (automatically installed via `requirements.txt`):

```
fastapi>=0.95.0          # Web framework and API
uvicorn[standard]>=0.22.0 # ASGI server with performance extras
sqlmodel>=0.0.8          # Database ORM and models
passlib[bcrypt]>=1.7.4   # Password hashing with bcrypt
python-multipart         # Form data and file upload support
itsdangerous>=2.1.2      # Secure session cookie signing
httpx>=0.24.0            # HTTP client for testing
pytest>=7.0.0            # Testing framework
pytest-asyncio>=0.21.0   # Async test support
jinja2>=3.1.0            # Template engine
evdev>=1.6.0             # Event device handling
gpiozero>=1.7.0          # GPIO interface (Raspberry Pi)
mfrc522                  # RC522 RFID module support
```

---

## Installation

### Automatic Installation (Recommended)

#### Option 1: Direct Installation from GitHub

Download and execute the automated installer:

```bash
curl -sSL https://raw.githubusercontent.com/ismailhaddouche/PiControl/main/install/install_from_github.sh | bash
```

This script will:
1. Clone the repository to `/opt/picontrol`
2. Create a Python virtual environment
3. Install all dependencies
4. Set up systemd service for automatic startup
5. Initialize the database
6. Prompt for admin user creation
7. Start the service automatically

#### Option 2: Local Installation

Clone the repository and run the installer locally:

```bash
# Clone repository
git clone https://github.com/ismailhaddouche/PiControl.git
cd PiControl

# Make installer executable and run
chmod +x install/pi_installer.sh
sudo ./install/pi_installer.sh
```

### Manual Installation (Development)

For development environments or custom installations:

#### Step 1: Clone Repository

```bash
git clone https://github.com/ismailhaddouche/PiControl.git
cd PiControl
```

#### Step 2: Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Initialize Database

```bash
python scripts/init_db.py
```

The database will be created at the location specified by the `PICONTROL_DB_DIR` environment variable (defaults to `/var/lib/picontrol`).

#### Step 5: Create Admin User

```bash
python tools/reset_admin.py
```

This creates an admin user with a randomly generated password saved to `/var/lib/picontrol/reset_password.txt`.

#### Step 6: Start Application

**Development mode (with auto-reload):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Production mode (with systemd):**
```bash
sudo cp install/picontrol.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable picontrol
sudo systemctl start picontrol
```

---

## Configuration

### Environment Variables

Create a `.env` file in the project root or set system environment variables:

```bash
# Database Configuration
PICONTROL_DB_DIR=/var/lib/picontrol

# Server Configuration
PICONTROL_HOST=0.0.0.0
PICONTROL_PORT=8000
PICONTROL_WORKERS=1

# Security Configuration
SECRET_KEY=your-secure-random-secret-key-here

# Backup Configuration
PICONTROL_BACKUP_DIR=/var/backups/picontrol

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/picontrol/app.log

# Session Configuration
SESSION_LIFETIME=3600  # Session timeout in seconds
```

### Database Configuration

- **Location**: `/var/lib/picontrol/pi_control.db` (default)
- **Configurable via**: `PICONTROL_DB_DIR` environment variable
- **Schema**: Automatically created with tables: `employee`, `checkin`, `user`, `config`, `adminaction`
- **Permissions**: Ensure application user has read/write access

Database connection string format:
```
sqlite:///[PICONTROL_DB_DIR]/pi_control.db
```

### RFID Reader Configuration

#### Hardware Setup

1. Connect USB RFID reader to any available USB port
2. Verify device recognition:
   ```bash
   lsusb
   dmesg | grep -i usb
   ```
3. Test reader functionality using the simulator:
   ```bash
   python simulador.py
   ```

#### Card Assignment

RFID cards are assigned to employees through the web interface:
1. Navigate to Employee Management section
2. Select an employee or create a new one
3. Click "Assign RFID Card"
4. Scan the RFID card when prompted
5. The unique identifier will be captured and stored automatically

### Network Configuration

#### Local Network Access

The application listens on all network interfaces by default (`0.0.0.0:8000`). Access from any device on the same network:

```
http://[raspberry-pi-ip]:8000
```

To find your Raspberry Pi's IP address:
```bash
hostname -I
ip addr show
```

#### Firewall Configuration

If using a firewall, ensure port 8000 is accessible:

```bash
sudo ufw allow 8000/tcp
sudo ufw reload
```

For production deployments, use a reverse proxy (nginx/Apache) with HTTPS.

---

## Usage Guide

### Starting the Application

#### Development Mode

Start with auto-reload for development:

```bash
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Production Mode (systemd)

Manage the service using systemd:

```bash
# Start service
sudo systemctl start picontrol

# Stop service
sudo systemctl stop picontrol

# Restart service
sudo systemctl restart picontrol

# Check status
sudo systemctl status picontrol

# View logs
sudo journalctl -u picontrol -f
```

### Web Interface

#### Initial Setup

1. Navigate to `http://[raspberry-pi-ip]:8000/admin/setup`
2. Create the first admin user
3. Set a strong password
4. Click "Create Admin"

#### Accessing the Admin Panel

1. Open `http://[raspberry-pi-ip]:8000/admin`
2. Enter admin credentials
3. Access the administration dashboard

#### Employee Management

**Creating Employees:**
1. Navigate to "Employees" section
2. Click "Add New Employee"
3. Enter employee details (Document ID, Name)
4. Optionally assign RFID card immediately
5. Click "Save"

**Assigning RFID Cards:**
1. Select an employee from the list
2. Click "Assign RFID"
3. Scan the RFID card
4. Confirm assignment

**Archiving Employees:**
1. Select an employee
2. Click "Archive"
3. Confirm action
4. Employee is soft-deleted (data preserved, access removed)

**Restoring Archived Employees:**
1. Navigate to "Archived Employees"
2. Select employee to restore
3. Click "Restore"
4. Employee becomes active again

#### Time Tracking

**Viewing Check-ins:**
1. Navigate to "Check-ins" section
2. Filter by date range or employee
3. View entry/exit times and calculated hours

**Manual Check-in Entry:**
1. Navigate to "Manual Check-in"
2. Select employee
3. Optionally specify custom timestamp
4. Submit entry (system auto-detects entry or exit)

#### Reports

**Generating Work Hours Reports:**
1. Navigate to "Reports" section
2. Select employee
3. Choose date range
4. Click "Generate Report"
5. View per-day breakdown and total hours
6. Export if needed

### API Usage

The application provides a complete REST API for programmatic access.

#### Employee Management

**Create Employee:**
```bash
curl -X POST "http://localhost:8000/employees/" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "EMP001", "name": "John Doe", "rfid_uid": "0123456789"}'
```

**List All Employees:**
```bash
curl "http://localhost:8000/employees/"
```

**Assign RFID to Employee:**
```bash
curl -X PUT "http://localhost:8000/employees/EMP001/rfid" \
  -H "Content-Type: application/json" \
  -d '{"rfid_uid": "0123456789"}'
```

#### Time Tracking

**Create Check-in (automatic entry/exit detection):**
```bash
curl -X POST "http://localhost:8000/checkins/" \
  -H "Content-Type: application/json" \
  -d '{"rfid_uid": "0123456789"}'
```

**Get Employee Check-ins:**
```bash
curl "http://localhost:8000/checkins/employee/EMP001"
```

**Get Hours Worked Report:**
```bash
curl "http://localhost:8000/reports/hours/EMP001?start_date=2025-01-01&end_date=2025-01-31"
```

### RFID Simulator

For development and testing without physical RFID hardware:

```bash
python simulador.py
```

The simulator:
- Accepts RFID UIDs via keyboard input
- Sends check-in requests to the API
- Displays server responses
- Useful for testing workflows without hardware

Type `exit` or `quit` to terminate the simulator.

---

## API Documentation

### Interactive Documentation

The application includes automatically generated interactive API documentation:

- **Swagger UI**: `http://[server]:8000/docs`
  - Interactive API exploration
  - Try-it-out functionality for all endpoints
  - Request/response schema documentation

- **ReDoc**: `http://[server]:8000/redoc`
  - Alternative documentation format
  - Clean, readable interface
  - Searchable endpoint reference

### API Endpoint Reference

#### Employee Management

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/employees/` | Create new employee | No |
| GET | `/employees/` | List all active employees | No |
| GET | `/employees/{id}` | Get employee details | No |
| PUT | `/employees/{id}/rfid` | Assign RFID card | No |
| DELETE | `/employees/{id}` | Archive employee | No |
| POST | `/employees/{id}/restore` | Restore archived employee | No |

#### Time Tracking

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/checkins/` | Create check-in record (auto-detect entry/exit) | No |
| GET | `/checkins/` | List check-in records | No |
| GET | `/checkins/employee/{id}` | Get employee check-ins | No |
| GET | `/reports/hours/{id}` | Get hours worked report | No |

#### Administration

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/admin/` | Admin dashboard | Yes |
| POST | `/admin/login` | Admin login | No |
| POST | `/admin/logout` | Admin logout | Yes |
| GET | `/admin/employees` | Employee management UI | Yes |
| POST | `/admin/employees` | Create/update employee | Yes |
| GET | `/admin/checkins` | Check-in management UI | Yes |
| POST | `/admin/checkins/manual` | Manual check-in entry | Yes |
| GET | `/admin/reports` | Reports interface | Yes |
| GET | `/admin/configuration` | System configuration | Yes |
| GET | `/admin/logs` | Admin audit logs | Yes |

---

## Testing

### Running Tests

#### Complete Test Suite

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest -v

# Run with coverage
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest --cov=app --cov-report=html tests/
```

#### Specific Test Execution

```bash
# Run specific test file
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest tests/test_api.py -v

# Run specific test function
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest tests/test_api.py::test_create_employee_and_checkin -v
```

### Manual Testing

#### Using Interactive Documentation

1. Navigate to `http://localhost:8000/docs`
2. Expand endpoint sections
3. Click "Try it out"
4. Enter parameters
5. Execute and view responses

---

## Maintenance

### Regular Maintenance Tasks

#### Database Cleanup

Remove old records to maintain optimal performance:

```bash
# Preview cleanup (dry run)
python tools/cleanup_old_records.py --dry-run

# Execute cleanup (creates automatic backup)
python tools/cleanup_old_records.py

# Cleanup with employee deletion
python tools/cleanup_old_records.py --delete-employees
```

Default retention: 4 years. Records older than this are permanently deleted.

#### Security Maintenance

**Rotate Secret Key:**
```bash
python tools/rotate_secret.py
```

**Reset Admin Password (requires physical access):**
```bash
sudo python tools/reset_admin.py
```

Password saved to `/var/lib/picontrol/reset_password.txt`.

#### System Maintenance

**Restart Service:**
```bash
sudo systemctl restart picontrol
```

**View Logs:**
```bash
sudo journalctl -u picontrol --since "1 hour ago"
```

**Update Application:**
```bash
cd /opt/picontrol
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart picontrol
```

### Backup and Recovery

#### Database Backup

**Manual Backup:**
```bash
cp /var/lib/picontrol/pi_control.db /var/backups/picontrol/backup_$(date +%Y%m%d_%H%M%S).db
```

**Automated Backup (via cron):**
```bash
# Add to crontab
0 2 * * * cp /var/lib/picontrol/pi_control.db /var/backups/picontrol/backup_$(date +\%Y\%m\%d).db
```

**Restore from Backup:**
```bash
sudo systemctl stop picontrol
sudo cp /var/backups/picontrol/backup_20250101.db /var/lib/picontrol/pi_control.db
sudo systemctl start picontrol
```

---

## Security

### Authentication & Authorization

- **Session-based Authentication**: Secure session cookies with cryptographic signing
- **Password Security**: bcrypt hashing with salt for admin accounts
- **Machine ID Validation**: Physical access required for admin reset

### Data Protection

- **Input Validation**: All user inputs validated and sanitized
- **SQL Injection Prevention**: Parameterized queries via SQLModel ORM
- **XSS Protection**: Template auto-escaping and output encoding

### Network Security

- **HTTPS Support**: SSL/TLS configuration for production deployment
- **Firewall Configuration**: Restrict access to necessary ports only
- **Network Isolation**: Consider placing on isolated network segment

### System Security

- **Service Isolation**: Dedicated user account for application service
- **File Permissions**: Restricted database and configuration file access
- **Audit Logging**: Comprehensive logging of administrative actions

### Security Best Practices

1. Change default admin password immediately after installation
2. Use strong, randomly generated passwords
3. Keep system and dependencies updated
4. Enable HTTPS in production environments
5. Regularly backup database with encryption
6. Monitor logs for suspicious activity
7. Restrict physical access to Raspberry Pi
8. Rotate secret keys periodically
9. Use firewall to limit network exposure
10. Review admin audit logs regularly

---

## Troubleshooting

### Common Issues

#### Database Permission Errors

**Symptoms:** `sqlite3.OperationalError: unable to open database file`

**Solution:**
```bash
sudo chown -R picontrol:picontrol /var/lib/picontrol
sudo chmod 755 /var/lib/picontrol
sudo chmod 644 /var/lib/picontrol/pi_control.db
```

#### Service Fails to Start

**Diagnosis:**
```bash
sudo systemctl status picontrol
sudo journalctl -u picontrol --no-pager -n 50
```

**Common causes:**
- Missing dependencies: Reinstall requirements
- Port already in use: Check for conflicting processes
- Database corruption: Restore from backup

#### RFID Reader Not Detected

**Diagnosis:**
```bash
lsusb | grep -i rfid
dmesg | tail -30
```

**Solutions:**
- Verify USB connection
- Check device permissions: `ls -l /dev/ttyUSB*`
- Test with simulator first

#### Port Already in Use

**Solution:**
```bash
sudo lsof -i :8000
sudo systemctl stop picontrol
```

#### Cannot Access Web Interface

**Diagnosis:**
```bash
sudo systemctl status picontrol
sudo ufw status
hostname -I
```

**Solutions:**
- Ensure service is running
- Open firewall port: `sudo ufw allow 8000/tcp`
- Verify correct IP address

---

## Contributing

We welcome contributions to improve PiControl!

### Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/[your-username]/PiControl.git`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Set up development environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for modules, classes, and functions
- Include tests for new functionality
- Update documentation as needed

### Submitting Changes

1. Commit changes: `git commit -m "Add feature: description"`
2. Push to fork: `git push origin feature/your-feature`
3. Create Pull Request on GitHub
4. Describe changes thoroughly
5. Link related issues

### Reporting Issues

Use GitHub Issues for bug reports and feature requests. Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant log output

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

### Key Points

- ✅ **Freedom to Use**: Use for any purpose, including commercial
- ✅ **Freedom to Modify**: Examine and modify source code
- ✅ **Freedom to Share**: Distribute copies of original software
- ⚠️ **Copyleft**: Modified versions must also be GPL-3.0
- ⚠️ **Source Code**: Must provide source when distributing

See the [LICENSE](LICENSE) file for complete terms.

---

## Support

### Documentation

- **API Documentation**: Available at `/docs` when application is running
- **Security Guidelines**: See [SECURITY_GUIDELINES.md](SECURITY_GUIDELINES.md)
- **Production Checklist**: See [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)

### Community

- **GitHub Issues**: [Report bugs and request features](https://github.com/ismailhaddouche/PiControl/issues)
- **GitHub Discussions**: [Community Q&A](https://github.com/ismailhaddouche/PiControl/discussions)

---

**PiControl** - Modern employee time tracking for Raspberry Pi 🥧⏰

*Author: hismardev*
