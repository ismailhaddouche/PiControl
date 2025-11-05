# PiControl - Employee Time Tracking System

A modern, web-based employee time tracking system designed for Raspberry Pi with RFID card support. Built with FastAPI and SQLite, featuring a responsive web interface for employee management and automated check-in/check-out functionality.

**Author:** hismardev

## 📋 Summary

PiControl is a lightweight application designed to run on a Raspberry Pi and manage employee check-in/check-out records using RFID readers. It provides an administration API (FastAPI), a web interface for administrators, a simulator to test check-ins without hardware, and utilities for installation and recovery on a physical device.

This repository contains the server logic, data models, HTML templates, and installation scripts designed to deploy PiControl on a Raspberry Pi or in a local development environment.

## 🚀 Features

### Core Functionality

- **RFID-based Time Tracking**: Automatic employee check-in/out using RFID cards
- **Employee Management**: Complete CRUD operations for employee records
- **Real-time Dashboard**: Live view of employee status and recent activity
- **Time Reports**: Detailed work hours calculation and reporting
- **Archive System**: Soft delete functionality for employee records
- **Admin Interface**: Secure web-based administration panel

### Advanced Features

- **Automatic Type Detection**: Smart detection of entry vs exit based on last check-in
- **Session Management**: Secure user authentication with session cookies
- **Data Validation**: Comprehensive input validation and error handling
- **Responsive Design**: Mobile-friendly interface for all devices
- **RESTful API**: Complete REST API for integration with external systems
- **Background Cleanup**: Automated cleanup of old records and maintenance

## 🛠 Technology Stack

### Backend

- **Framework**: FastAPI 0.95+ (Modern, fast Python web framework)
- **Database**: SQLite with SQLModel ORM (Type-safe database operations)
- **Authentication**: Session-based with secure password hashing (passlib + bcrypt)
- **Validation**: Pydantic models for data validation
- **ASGI Server**: Uvicorn with performance optimizations

### Frontend

- **Template Engine**: Jinja2 with responsive HTML templates
- **CSS Framework**: Custom responsive CSS with mobile-first design
- **JavaScript**: Vanilla JS for dynamic interactions
- **Forms**: HTML5 forms with client-side validation

### System Integration

- **Operating System**: Optimized for Raspberry Pi OS (Debian-based)
- **Service Management**: systemd service integration
- **Process Management**: Background task handling
- **Security**: Machine-ID validation for admin reset functionality

The project avoids heavy dependencies to facilitate installation on Raspberry Pi and resource-limited environments.

## 📋 Requirements

### Hardware Requirements

- **Raspberry Pi**: Pi 3B+ or newer (recommended Pi 4 for better performance)
- **Storage**: Minimum 8GB microSD card (Class 10 recommended)
- **RFID Reader**: USB RFID reader compatible with EM4100/EM4102 cards
- **Network**: Ethernet or Wi-Fi connectivity

### Software Requirements

- **OS**: Raspberry Pi OS (Bullseye or newer) or compatible Debian-based system
- **Python**: 3.10+ (3.11+ recommended for optimal performance)
- **System Packages**:
  ```bash
  sudo apt update
  sudo apt install python3-pip python3-venv git sqlite3
  ```

### Python Dependencies

All Python dependencies are managed via `requirements.txt`:

- `fastapi>=0.95.0` - Web framework
- `uvicorn[standard]>=0.22.0` - ASGI server
- `sqlmodel>=0.0.8` - Database ORM
- `passlib[bcrypt]>=1.7.4` - Password hashing
- `python-multipart>=0.0.20` - Form data handling
- `itsdangerous>=2.1.2` - Session security
- `jinja2>=3.1.0` - Template engine
- `httpx>=0.24.0` - HTTP client for testing
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing support

## 🔧 Installation

### Automatic Installation (Recommended)

#### Option 1: Direct from GitHub

```bash
# Download and run the installer
curl -sSL https://raw.githubusercontent.com/ismailhaddouche/PiControl/main/install/install_from_github.sh | bash
```

#### Option 2: Clone and Install Locally

```bash
# Clone the repository
git clone https://github.com/ismailhaddouche/PiControl.git
cd PiControl

# Run the local installer
chmod +x install/pi_installer.sh
sudo ./install/pi_installer.sh
```

### Manual Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/ismailhaddouche/PiControl.git
   cd PiControl
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Initialize Database**
   ```bash
   python scripts/init_db.py
   ```

5. **Create Admin User**
   ```bash
   python tools/reset_admin.py
   ```

6. **Configure Service (Optional)**
   ```bash
   sudo cp install/picontrol.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable picontrol
   sudo systemctl start picontrol
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
PICONTROL_DB_DIR=/var/lib/picontrol

# Server Configuration
PICONTROL_HOST=0.0.0.0
PICONTROL_PORT=8000

# Security Configuration
SECRET_KEY=your-secure-secret-key-here

# Backup Configuration
PICONTROL_BACKUP_DIR=/var/backups/picontrol

# Log Configuration
LOG_LEVEL=INFO
```

### Database Setup

The application automatically creates the database on first run:

- **Location**: `/var/lib/picontrol/pi_control.db` (configurable via `PICONTROL_DB_DIR`)
- **Schema**: Automatically created with English table names (`employee`, `checkin`, `user`, `config`)
- **Permissions**: Ensure the application has read/write access to the database directory

### RFID Configuration

1. **Connect RFID Reader**: Plug USB RFID reader into Raspberry Pi
2. **Test Reader**: Use the simulator to test RFID functionality:
   ```bash
   python simulador.py
   ```
3. **Configure Cards**: Assign RFID cards to employees through the web interface

## 🚀 Usage

### Starting the Application

#### Development Mode
```bash
# Activate virtual environment
source .venv/bin/activate

# Start development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Production Mode (systemd service)
```bash
# Start the service
sudo systemctl start picontrol

# Check status
sudo systemctl status picontrol

# View logs
sudo journalctl -u picontrol -f
```

### Web Interface
1. **Access**: Navigate to `http://your-pi-ip:8000`
2. **Login**: Use admin credentials (created during setup)
3. **Employee Management**: Add employees and assign RFID cards
4. **Time Tracking**: Employees can check in/out by scanning RFID cards

### API Usage

#### Employee Management
```bash
# Create employee
curl -X POST "http://localhost:8000/employees/" \
  -H "Content-Type: application/json" \
  -d '{"document_id": "EMP001", "name": "John Doe", "rfid_uid": "0123456789"}'

# List all employees
curl "http://localhost:8000/employees/"

# Assign RFID to employee
curl -X PUT "http://localhost:8000/employees/EMP001/rfid" \
  -H "Content-Type: application/json" \
  -d '{"rfid_uid": "0123456789"}'
```

#### Time Tracking
```bash
# Create check-in (automatic entry/exit detection)
curl -X POST "http://localhost:8000/checkins/" \
  -H "Content-Type: application/json" \
  -d '{"rfid_uid": "0123456789"}'

# Get employee check-ins
curl "http://localhost:8000/checkins/employee/EMP001"

# Get hours worked report
curl "http://localhost:8000/reports/hours/EMP001?start_date=2025-01-01&end_date=2025-01-31"
```

## 🔧 Maintenance

### Regular Maintenance Tasks

#### Database Cleanup
```bash
# Clean old records (older than 4 years)
python tools/cleanup_old_records.py --dry-run

# Execute cleanup (creates backup first)
python tools/cleanup_old_records.py

# Clean old records and inactive employees
python tools/cleanup_old_records.py --delete-employees
```

#### Security Maintenance
```bash
# Rotate secret key
python tools/rotate_secret.py

# Reset admin password (requires physical access to Pi)
sudo python tools/reset_admin.py
```

#### System Maintenance
```bash
# Restart service
sudo systemctl restart picontrol

# Check service logs
sudo journalctl -u picontrol --since "1 hour ago"

# Update application
cd /opt/picontrol
git pull origin main
sudo systemctl restart picontrol
```

### Backup and Recovery

#### Database Backup
```bash
# Manual backup
cp /var/lib/picontrol/pi_control.db /var/backups/picontrol/backup_$(date +%Y%m%d_%H%M%S).db

# Automated backup (via cron)
# Add to crontab: 0 2 * * * /opt/picontrol/tools/backup_db.sh
```

#### System Backup
```bash
# Backup entire configuration
tar -czf picontrol_backup.tar.gz \
  /var/lib/picontrol \
  /etc/systemd/system/picontrol.service \
  /opt/picontrol
```

### Monitoring and Diagnostics

#### Health Checks
```bash
# Check API health
curl http://localhost:8000/

# Check database connectivity
python -c "from app.db import get_session; print('Database OK')"

# Check RFID simulator
python simulador.py
```

#### Log Analysis
```bash
# Application logs
sudo journalctl -u picontrol -f

# System resource usage
htop
df -h
free -m

# Network connectivity
ss -tulpn | grep :8000
```

### Troubleshooting

#### Common Issues

1. **Database Permission Errors**
   ```bash
   sudo chown -R picontrol:picontrol /var/lib/picontrol
   sudo chmod 755 /var/lib/picontrol
   ```

2. **Service Won't Start**
   ```bash
   sudo systemctl status picontrol
   sudo journalctl -u picontrol --no-pager
   ```

3. **RFID Reader Not Detected**
   ```bash
   lsusb | grep -i rfid
   dmesg | tail -20
   ```

4. **Port Already in Use**
   ```bash
   sudo ss -tulpn | grep :8000
   sudo systemctl stop picontrol
   ```

## 🧪 Testing

### Running Tests
```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest -v

# Run with coverage
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest --cov=app tests/

# Run specific test
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest tests/test_api.py::test_create_employee_and_checkin
```

### Manual Testing
```bash
# Test RFID simulation
python simulador.py

# Test API endpoints
curl http://localhost:8000/docs  # Swagger documentation
```

## 📁 Project Structure

```
PiControl/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   ├── models.py                 # Database models (Employee, CheckIn, User, Config)
│   ├── crud.py                   # Database operations and business logic
│   ├── db.py                     # Database connection and session management
│   ├── routers/                  # API route handlers
│   │   ├── __init__.py
│   │   ├── employees.py          # Employee management endpoints
│   │   ├── checkins.py           # Time tracking endpoints
│   │   └── web.py                # Web interface routes
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── base.html             # Base template with common layout
│   │   ├── login.html            # Admin login page
│   │   ├── menu.html             # Main navigation menu
│   │   ├── employees.html        # Employee management interface
│   │   ├── checkins.html         # Check-in/out interface
│   │   ├── reports.html          # Time reports interface
│   │   └── configuration.html    # System configuration
│   └── static/                   # Static assets (CSS, JS)
│       ├── style.css             # Main stylesheet
│       └── app.js                # JavaScript functionality
├── install/                      # Installation scripts
│   ├── install_from_github.sh    # GitHub installer
│   ├── pi_installer.sh           # Local installer
│   └── picontrol.service         # systemd service definition
├── tools/                        # Utility scripts
│   ├── cleanup_old_records.py    # Database cleanup utility
│   ├── reset_admin.py            # Admin password reset
│   ├── rotate_secret.py          # Security key rotation
│   └── picontrol-*.sh            # System management scripts
├── tests/                        # Test suite
│   └── test_api.py               # API endpoint tests
├── scripts/                      # Setup scripts
│   └── init_db.py               # Database initialization
├── simulador.py                  # RFID simulator for development/testing
├── requirements.txt              # Python dependencies
├── README.md                     # This documentation
├── LICENSE                       # GPL-3.0 license
└── SECURITY_GUIDELINES.md        # Security best practices
```

## 🔒 Security

### Authentication & Authorization
- **Session-based Authentication**: Secure session cookies with CSRF protection
- **Password Security**: bcrypt hashing with salt for admin accounts
- **Machine ID Validation**: Physical access required for admin reset functionality

### Data Protection
- **Input Validation**: All user inputs validated and sanitized
- **SQL Injection Prevention**: Parameterized queries via SQLModel
- **XSS Protection**: Template auto-escaping and CSP headers

### Network Security
- **HTTPS Support**: SSL/TLS configuration for production deployment
- **CORS Configuration**: Controlled cross-origin resource sharing
- **Rate Limiting**: Built-in protection against abuse

### System Security
- **Service Isolation**: Dedicated user account for application service
- **File Permissions**: Restricted database and configuration file access
- **Log Security**: Sensitive data excluded from logs

## 📄 API Documentation

### Interactive Documentation
Once the application is running, access the interactive API documentation:
- **Swagger UI**: `http://your-server:8000/docs`
- **ReDoc**: `http://your-server:8000/redoc`

### Key Endpoints

#### Employee Management
- `POST /employees/` - Create new employee
- `GET /employees/` - List all employees  
- `GET /employees/{employee_id}` - Get employee details
- `PUT /employees/{employee_id}/rfid` - Assign RFID card
- `DELETE /employees/{employee_id}` - Archive employee
- `POST /employees/{employee_id}/restore` - Restore archived employee

#### Time Tracking  
- `POST /checkins/` - Create check-in/out record
- `GET /checkins/` - List check-in records
- `GET /checkins/employee/{employee_id}` - Get employee's check-ins
- `GET /reports/hours/{employee_id}` - Get hours worked report

#### Administration
- `GET /admin/` - Admin dashboard (requires authentication)
- `POST /admin/login` - Admin login
- `POST /admin/logout` - Admin logout
- `GET /admin/employees` - Employee management interface
- `GET /admin/checkins` - Check-in management interface

## 🤝 Contributing

We welcome contributions to improve PiControl! Please follow these guidelines:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Install development dependencies: `pip install -r requirements.txt`
4. Make your changes and add tests
5. Run tests: `pytest`
6. Submit a pull request

### Code Standards
- **Python Style**: Follow PEP 8 guidelines
- **Type Hints**: Use type hints for all functions
- **Documentation**: Update docstrings and README as needed
- **Testing**: Add tests for new functionality

### Reporting Issues
- Use GitHub Issues to report bugs or request features
- Include system information (OS, Python version, etc.)
- Provide steps to reproduce the issue
- Include relevant log output

## 📜 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

### Summary
- ✅ **Use**: Free to use, copy, and distribute
- ✅ **Modify**: Free to modify and create derivative works  
- ✅ **Distribute**: Free to distribute original and modified versions
- ⚠️ **Copyleft**: Modified versions must also be licensed under GPL-3.0
- ⚠️ **Source Code**: Must provide source code when distributing

### Commercial Use
GPL-3.0 allows commercial use, but any modifications or derivative works must also be released under GPL-3.0. For commercial deployments, ensure compliance with the license terms.

See the [LICENSE](LICENSE) file for the complete license text.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- Database management via [SQLModel](https://sqlmodel.tiangolo.com/) - SQLAlchemy with Pydantic
- Inspired by modern time tracking solutions and Raspberry Pi IoT projects
- Thanks to the open-source community for the excellent tools and libraries

## 📞 Support

### Community Support
- **GitHub Issues**: [Report bugs and request features](https://github.com/ismailhaddouche/PiControl/issues)
- **Discussions**: [Community discussions and Q&A](https://github.com/ismailhaddouche/PiControl/discussions)

### Documentation
- **API Docs**: Available at `/docs` when application is running
- **Code Documentation**: Inline docstrings and type hints throughout codebase
- **Security Guidelines**: See [SECURITY_GUIDELINES.md](SECURITY_GUIDELINES.md)

---

**PiControl** - Modern employee time tracking for the Raspberry Pi era 🥧⏰
