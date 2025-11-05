# PiControl
A tailored Raspberry Pi app for worker clock-in/out registration using RFID.

**Author:** hismardev

## Summary

PiControl is a lightweight application designed to run on a Raspberry Pi and manage employee check-in/check-out
records using RFID readers. It provides an administration API (FastAPI), a web interface for administrators,
a simulator to test check-ins without hardware, and utilities for installation and recovery on a physical device.

This repository contains the server logic, data models, HTML templates, and installation scripts designed
to deploy PiControl on a Raspberry Pi or in a local development environment.

## Technologies and Stack Used

- **Language:** Python 3.10+ / 3.11+
- **Web framework:** FastAPI (REST endpoints, Jinja2 templates)
- **ASGI Server:** Uvicorn
- **ORM / Models:** SQLModel (SQLAlchemy)
- **Database:** SQLite (`pi_control.db` file)
- **Authentication:** Starlette sessions + password hashing (passlib pbkdf2_sha256)
- **Templates:** Jinja2
- **Lightweight Frontend:** HTML/CSS and JavaScript for AJAX calls
- **Tests:** pytest + httpx TestClient

The project avoids heavy dependencies to facilitate installation on Raspberry Pi and resource-limited environments.

## Requirements

- Raspberry Pi (optional for real deployment) or any Linux for development.
- Python 3.10+ installed.
- Root privileges access to install systemd services (if applicable).

## Installation (local / development)

1. Clone the repository and enter the folder:

```bash
git clone https://github.com/ismailhaddouche/PiControl.git
cd PiControl
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Initialize and start the API (in development you can use reload):

```bash
uvicorn app.main:app --reload
```

5. Open the browser at `http://127.0.0.1:8000/admin` to access the administration UI.

## Raspberry Pi Installation (automatic from GitHub)

The repository includes utilities to install directly from GitHub and prepare the Pi:

- `install/install_from_github.sh`: clones (or updates) the repo in `/opt/picontrol`, creates a virtualenv, installs dependencies, and runs the local installer.
- `install/pi_installer.sh`: installer that saves the `machine-id`, installs scripts in `/usr/local/bin`, creates a systemd service `picontrol-firstboot.service`, and creates a `.desktop` access for the desktop user.

Example usage on Raspberry Pi (run as root):

```bash
sudo bash install/install_from_github.sh https://github.com/ismailhaddouche/PiControl.git main --user pi
```

Important notes:
- Review the scripts before running them as root. The installer places files in `/opt`, `/usr/local/bin` and creates/activates systemd services.
- The installer saves `/etc/machine-id` to `/var/lib/picontrol/machine-id` to allow the admin reset script to only run on the same machine.

## Configuration

- **First boot / setup:** the project includes a setup screen (`/admin/setup`) that allows creating the first administrator user if none exists.
- **Admin password change:** from the `Configuration` UI you can change the admin password.
- **Time zone:** the configuration UI allows selecting a time zone and the server attempts to apply `timedatectl` (requires privileges).
- **Export/import DB:** from the configuration you can download the `pi_control.db` file or upload a copy to replace the database (restart recommended after import).

Security and recovery:
- Includes `tools/picontrol-reset-admin.sh` and `tools/reset_admin.py` to recover admin access on the same Raspberry Pi. The flow verifies the saved `machine-id` to prevent resets from another device.
- The reset script generates a secure password and saves it to `/var/lib/picontrol/reset_password.txt` with permissions 600. It's recommended to rotate or delete it after use.

## Basic Usage

- Adding employees, assigning RFID, and managing check-ins is done from the administration UI (`/admin`).
- To simulate check-ins without a physical RFID reader, run `python simulador.py` in a terminal and type the `rfid_uid` you want to simulate.

Common endpoints:

- `GET /admin` — main panel (requires login)
- `POST /employees/` — create new employee
- `GET /employees/` — list all employees
- `PUT /employees/{id}/rfid` — assign/update RFID
- `DELETE /employees/{id}` — delete employee (archive)
- `POST /employees/{id}/restore` — restore archived employee

## Project Structure

Root of the project and purpose of the most relevant files/directories:

- `app/` — main application code
  - `main.py` — FastAPI entry point and middleware configuration
  - `models.py` — SQLModel models (Employee, CheckIn, User, Config)
  - `crud.py` — data access functions and logic (create employee, check-ins, archive/restore, config)
  - `db.py` — SQLite connection/engine utilities
  - `routers/` — organized web/API routes (employees, checkins, web)
  - `templates/` — Jinja2 templates for web interface
  - `static/` — static CSS/JS for the UI

- `simulador.py` — script that simulates RFID card reading (development mode)
- `pi_control.db` — SQLite file (generated at runtime)
- `install/` — installation scripts and systemd service
  - `install_from_github.sh` — cloner/installer from GitHub
  - `pi_installer.sh` — local installer that configures service / scripts
  - `picontrol-firstboot.service` — systemd first boot unit
- `tools/` — utility scripts
  - `picontrol-reset-admin.sh` — wrapper that validates machine-id and launches reset
  - `reset_admin.py` — Python script that creates or resets admin account

- `tests/` — automated tests (pytest)
- `requirements.txt` — Python dependencies
- `README.md` — this file

## Tests

Run tests with:

```bash
source .venv/bin/activate
pytest -q
```

## Contributing

If you want to contribute, open an issue or pull request. Review style conventions and add tests for relevant changes.

## License

This project is distributed under the GNU General Public License v3.0 (GPL-3.0).

Quick summary (does not replace reading the full text):

- You can use, copy and distribute this software for free.
- If you publish or distribute a modified version of the code, you must do so under the same license (GPL-3.0). This means modifications must also be available as free software under the same terms.
- See the `LICENSE` file for the full text of GPL-3.0 and legal details.

If you include this project within another product (e.g., redistributing binaries or incorporating it into an image), make sure to comply with GPL-3.0 obligations (include license notices and provide source code of modifications under GPL-3.0).

SPDX: MIT -> GPL-3.0-or-later

---

If you want me to add a section with quick administration commands (e.g. how to restart the service, view logs or force migrations), let me know and I'll include it.
