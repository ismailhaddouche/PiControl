# Security Guidelines# Security Guidelines# Seguridad: pasos urgentes para este repositorio



**Comprehensive Security Guide for PiControl**



This document provides detailed security guidelines, best practices, and hardening procedures for deploying and maintaining PiControl in production environments.**Comprehensive Security Guide for PiControl**Este documento enumera acciones inmediatas y comandos para mitigar la exposición de secretos



---o una base de datos accidentalmente incluida en el historial.



## Table of ContentsThis document provides detailed security guidelines, best practices, and hardening procedures for deploying and maintaining PiControl in production environments.



- [Overview](#overview)IMPORTANTE: las operaciones que reescriben el historial (BFG, git-filter-repo) deben coordinarse

- [Threat Model](#threat-model)

- [Security Architecture](#security-architecture)---con colaboradores. Haz un backup antes de proceder.

- [Pre-Deployment Checklist](#pre-deployment-checklist)

- [Authentication & Authorization](#authentication--authorization)

- [Data Protection](#data-protection)

- [Network Security](#network-security)## Table of Contents1) Quitar archivos sensibles del árbol de trabajo (ya realizado en esta copia):

- [System Hardening](#system-hardening)

- [RFID Security](#rfid-security)

- [Secure Configuration](#secure-configuration)

- [Monitoring & Logging](#monitoring--logging)- [Overview](#overview)   - El archivo `pi_control.db` fue movido fuera del repo y ya no está en la rama actual.

- [Incident Response](#incident-response)

- [Security Maintenance](#security-maintenance)- [Threat Model](#threat-model)     Se creó un backup en `/tmp/pi_control.db.bak`.

- [Compliance](#compliance)

- [Security Auditing](#security-auditing)- [Security Architecture](#security-architecture)

- [Resources](#resources)

- [Pre-Deployment Security Checklist](#pre-deployment-security-checklist)2) Añadir entradas a `.gitignore` (ya realizado):

---

- [Authentication & Authorization](#authentication--authorization)

## Overview

- [Data Protection](#data-protection)   - `pi_control.db`, `.env`, `.env.example`, `reset_password.txt`, `secret_key.txt`, `.test_db/`

PiControl is designed with security in mind, but proper deployment and configuration are critical to maintaining a secure system. This guide covers security considerations specific to employee time tracking systems and Raspberry Pi deployments.

- [Network Security](#network-security)

### Security Principles

- [System Hardening](#system-hardening)3) Opciones para purgar el historial (elige una):

1. **Defense in Depth** - Multiple layers of security controls

2. **Least Privilege** - Minimal permissions for users and processes- [RFID Security](#rfid-security)

3. **Secure by Default** - Safe configuration out of the box

4. **Fail Secure** - Graceful degradation without compromising security- [Secure Configuration](#secure-configuration)   Opción rápida (BFG):

5. **Audit Everything** - Comprehensive logging of security-relevant events

- [Monitoring & Logging](#monitoring--logging)

### Document Scope

- [Incident Response](#incident-response)   - Instalar BFG y clonar espejo:

This guide addresses security concerns for:

- Production deployments on Raspberry Pi- [Security Maintenance](#security-maintenance)

- Network-accessible installations

- Systems processing employee personal data- [Compliance Considerations](#compliance-considerations)     git clone --mirror git@github.com:tu_usuario/PiControl.git

- GDPR/compliance-sensitive environments

- [Security Auditing](#security-auditing)     java -jar bfg.jar --delete-files pi_control.db

---

     cd PiControl.git

## Threat Model

---     git reflog expire --expire=now --all && git gc --prune=now --aggressive

### Assets to Protect

     git push --force

| Asset | Description | Sensitivity |

|-------|-------------|-------------|## Overview

| **Employee Personal Data** | Names, document IDs, work hours | High |

| **Authentication Credentials** | Admin passwords, session tokens | Critical |   Opción recomendada (git-filter-repo):

| **System Configuration** | Secret keys, database, service accounts | Critical |

| **Business Intelligence** | Work patterns, attendance records | Medium |PiControl is designed with security in mind, but proper deployment and configuration are critical to maintaining a secure system. This guide covers security considerations specific to time tracking systems and Raspberry Pi deployments.



### Threat Actors     pip install git-filter-repo



| Actor | Capability | Motivation |### Security Principles     git clone --mirror git@github.com:tu_usuario/PiControl.git

|-------|-----------|------------|

| **External Attackers** | Network-based exploitation | Data theft, service disruption |     cd PiControl.git

| **Malicious Insiders** | Physical/network access | Fraud, data manipulation |

| **Curious Employees** | Limited technical skills | Unauthorized access, curiosity |1. **Defense in Depth**: Multiple layers of security controls     git filter-repo --invert-paths --paths pi_control.db

| **Physical Threats** | Device access | Device theft, RFID cloning |

2. **Least Privilege**: Minimal permissions for users and processes     git push --force

### Attack Vectors

3. **Secure by Default**: Safe configuration out of the box

1. **Network Attacks** - SQL injection, XSS, session hijacking, CSRF

2. **Physical Access** - Device tampering, RFID card cloning, USB attacks4. **Fail Secure**: Graceful degradation without compromising security   - Después de reescribir el historial, rotar todas las credenciales expuestas (passwords, API keys).

3. **Social Engineering** - Credential theft, phishing, pretexting

4. **Privilege Escalation** - Unauthorized admin access, service exploitation5. **Audit Everything**: Comprehensive logging of security-relevant events

5. **Data Exfiltration** - Database theft, backup compromise, log harvesting

4) Rotación de secretos en la máquina objetivo

---

---

## Security Architecture

      - Rotear SECRET_KEY (si fue expuesta), API keys y cualquier contraseña presente en la BD.

### Defense Layers

## Threat Model      - Nota: los scripts `tools/reset_admin.py` y `tools/rotate_secret.py` han sido modificados para

```

┌─────────────────────────────────────────┐         evitar escribir secretos en disco por defecto. `reset_admin.py` ahora imprime la contraseña en

│  Layer 4: Physical Security             │

│  - Device access controls               │### Assets to Protect         stdout (one-time) y `rotate_secret.py` imprime la nueva SECRET_KEY y solo crea copia con

│  - RFID reader protection               │

└─────────────────────────────────────────┘         `--backup`.

            ↓

┌─────────────────────────────────────────┐1. **Employee Personal Data**: Names, document IDs, work hours   - Cambiar claves y tokens en los servicios afectados (por ejemplo, proveedores de API).

│  Layer 3: Network Security              │

│  - Firewall rules                       │2. **Authentication Credentials**: Admin passwords, session tokens

│  - TLS encryption                       │

│  - Network segmentation                 │3. **System Configuration**: Secret keys, database, service accounts5) Crear scripts/migraciones para recrear la DB en el despliegue

└─────────────────────────────────────────┘

            ↓4. **Business Intelligence**: Work patterns, attendance records

┌─────────────────────────────────────────┐

│  Layer 2: Application Security          │   - Se añadió `scripts/init_db.py` que invoca `app.db.init_db()`.

│  - Authentication                       │

│  - Input validation                     │### Threat Actors   - Evita mantener la DB en el repo; usa migraciones o scripts de inicialización.

│  - Session management                   │

└─────────────────────────────────────────┘

            ↓

┌─────────────────────────────────────────┐1. **External Attackers**: Internet-based exploitation attempts6) Revisión de servicios systemd y scripts

│  Layer 1: Data Security                 │

│  - Encryption at rest                   │2. **Malicious Insiders**: Employees with physical/network access

│  - Secure backups                       │

│  - Audit logging                        │3. **Curious Employees**: Unauthorized access attempts by staff   - Revisa `install/*.service` y `tools/*.sh` para asegurar que no contienen credenciales en claro.

└─────────────────────────────────────────┘

```4. **Physical Threats**: Device theft, RFID cloning   - Asegúrate de usar `EnvironmentFile=/etc/default/picontrol` y proteger permisos (0600).



### Security Components



| Component | Technology | Protection Against |### Attack Vectors7) Comandos útiles para buscar patrones de credenciales localmente:

|-----------|-----------|-------------------|

| **Session Management** | Signed cookies (itsdangerous) | Session hijacking, tampering |

| **Password Storage** | bcrypt hashing | Credential theft, rainbow tables |

| **Input Validation** | Pydantic models | SQL injection, XSS, corruption |1. **Network Attacks**: SQL injection, XSS, session hijacking   git grep -nE "API[_-]?KEY|TOKEN|SECRET|PASSWORD|aws_secret_access_key|BEGIN RSA PRIVATE KEY" || true

| **HTTPS/TLS** | SSL certificates | MITM attacks, eavesdropping |

| **Audit Logging** | Database logs | Unauthorized changes, forensics |2. **Physical Access**: Device tampering, RFID card cloning

| **Machine-ID Validation** | Hardware binding | Remote admin reset attacks |

3. **Social Engineering**: Credential theft, phishing8) Próximos pasos recomendados

---

4. **Privilege Escalation**: Unauthorized admin access

## Pre-Deployment Checklist

5. **Data Exfiltration**: Database theft, backup compromise   - Ejecutar un escaneo detallado (opción A1) para mostrar fragmentos con coincidencias y recomendaciones de cambio.

### Critical Security Tasks

   - Si quieres, puedo ejecutar git-filter-repo en un espejo local (necesitarás acceso y coordinación para push --force).

**Must complete before production deployment:**

---

- [ ] Generate strong SECRET_KEY (32+ random bytes)

- [ ] Change default admin password immediately## Security Architecture

- [ ] Enable HTTPS with valid SSL certificate

- [ ] Configure firewall to restrict port access### Security Layers

- [ ] Set restrictive file permissions on database and config files

- [ ] Create dedicated system user for the service```

- [ ] Disable SSH password authentication (use keys only)┌─────────────────────────────────────────┐

- [ ] Update Raspberry Pi OS to latest stable version│  Physical Security (Pi + RFID Reader)   │

- [ ] Configure automatic security updates├─────────────────────────────────────────┤

- [ ] Set up encrypted backups with secure storage│  Network Security (Firewall + TLS)      │

├─────────────────────────────────────────┤

### Recommended Enhancements│  Application Security (Auth + Validation)│

├─────────────────────────────────────────┤

**Additional hardening for high-security environments:**│  Data Security (Encryption + Backups)   │

└─────────────────────────────────────────┘

- [ ] Implement rate limiting for login attempts```

- [ ] Add CSRF protection for state-changing operations

- [ ] Configure session timeout (recommended: 3600 seconds)### Security Components

- [ ] Set up intrusion detection (fail2ban, AIDE)

- [ ] Enable AppArmor or SELinux profiles| Component | Security Feature | Protection Against |

- [ ] Restrict physical access to Raspberry Pi device|-----------|------------------|-------------------|

- [ ] Use separate VLANs for management traffic| Session Management | Cryptographic signing | Session hijacking, tampering |

- [ ] Implement database encryption at rest| Password Storage | bcrypt hashing | Credential theft, rainbow tables |

- [ ] Set up centralized log aggregation and monitoring| Input Validation | Pydantic models | SQL injection, XSS, data corruption |

- [ ] Create and test disaster recovery plan| HTTPS/TLS | SSL certificates | Man-in-the-middle, eavesdropping |

| Audit Logging | Admin action logs | Unauthorized changes, forensics |

---| Machine-ID Validation | Hardware binding | Remote admin reset attacks |



## Authentication & Authorization---



### Password Security## Pre-Deployment Security Checklist



#### Password Policy### Critical Security Tasks



Enforce strong passwords for all admin accounts:- [ ] **Generate strong SECRET_KEY** (32+ random bytes)

- [ ] **Change default admin password** immediately

**Requirements:**- [ ] **Enable HTTPS** with valid SSL certificate

- Minimum 12 characters- [ ] **Configure firewall** to restrict port access

- Mix of uppercase, lowercase, numbers, symbols- [ ] **Set file permissions** on database and config files

- No common words or dictionary patterns- [ ] **Create dedicated system user** for the service

- Unique (not reused from other services)- [ ] **Disable SSH password authentication** (use keys only)

- Changed every 90 days- [ ] **Update Raspberry Pi OS** to latest stable version

- [ ] **Configure automatic security updates**

**Generate secure password:**- [ ] **Set up encrypted backups** with secure storage

```bash

python3 -c "import secrets, string; chars = string.ascii_letters + string.digits + string.punctuation; print(''.join(secrets.choice(chars) for _ in range(20)))"### Recommended Security Enhancements

```

- [ ] Implement rate limiting for login attempts

#### Password Storage- [ ] Add CSRF protection for state-changing operations

- [ ] Configure session timeout (default: 3600 seconds)

- **Algorithm:** bcrypt with salt (via Passlib)- [ ] Set up intrusion detection (fail2ban)

- **Work Factor:** Default 12 rounds (configurable)- [ ] Enable AppArmor/SELinux profiles

- **No plaintext:** Passwords never stored or logged in clear text- [ ] Restrict physical access to Raspberry Pi

- **Salt:** Unique salt per password (automatic)- [ ] Use separate VLANs for management traffic

- [ ] Implement database encryption at rest

#### Password Reset- [ ] Set up log aggregation and monitoring

- [ ] Create disaster recovery plan

**Standard procedure (physical access required):**

```bash---

# Execute on Raspberry Pi console

cd /opt/picontrol## Authentication & Authorization

sudo -u picontrol PICONTROL_DB_DIR=/var/lib/picontrol \

  /opt/picontrol/.venv/bin/python tools/reset_admin.py### Password Security



# Password output to stdout only#### Strong Password Policy

# Change immediately after first login

```Enforce strong passwords for admin accounts:



### Session Management```bash

# Minimum requirements:

#### Secure Configuration# - At least 12 characters

# - Mix of uppercase, lowercase, numbers, symbols

```python# - No common words or patterns

# Session middleware configuration (app/main.py)# - Unique (not reused from other services)

app.add_middleware(

    SessionMiddleware,# Generate strong password:

    secret_key=os.environ.get("SECRET_KEY"),  # Requiredpython3 -c "import secrets, string; chars = string.ascii_letters + string.digits + string.punctuation; print(''.join(secrets.choice(chars) for _ in range(20)))"

    session_cookie="picontrol_session",```

    max_age=3600,  # 1 hour default

    same_site="lax",#### Password Storage

    https_only=True  # Must enable with HTTPS in production

)- **Algorithm**: bcrypt with salt (via Passlib)

```- **Work Factor**: Default (can be increased for higher security)

- **No plaintext**: Passwords never stored or logged in plain text

#### Cookie Security Flags

#### Password Reset Procedure

| Flag | Purpose | Production Value |

|------|---------|------------------|```bash

| `HttpOnly` | Prevents JavaScript access | Always enabled |# Admin password reset (requires physical access to Pi)

| `Secure` | Requires HTTPS | **Must enable** |sudo python tools/reset_admin.py

| `SameSite` | Prevents CSRF attacks | `Lax` or `Strict` |

| `Max-Age` | Session lifetime | 3600 seconds (1 hour) |# Password is output to stdout only (not saved to file by default)

# Change immediately after first login

#### Session Best Practices```



1. **Configure secure cookie flags** - Enable `Secure` flag when using HTTPS### Session Management

2. **Set appropriate timeout** - Balance security vs. usability (default: 1 hour)

3. **Implement absolute timeout** - Force re-authentication after max duration#### Session Security Configuration

4. **Clear sessions on logout** - Complete session invalidation

5. **Rotate SECRET_KEY periodically** - Invalidates all existing sessions```python

# In app/main.py

### Authorization Controlsapp.add_middleware(

    SessionMiddleware,

#### Admin Access Protection    secret_key=os.environ.get("SECRET_KEY"),  # Must be set

    session_cookie="picontrol_session",

All administrative endpoints require:    max_age=3600,  # 1 hour

1. Valid authenticated session    same_site="lax",

2. User account with `is_admin=True` flag    https_only=True  # Enable in production with HTTPS

3. Session not expired)

```

**Protected operations:**

- Employee management (create, edit, archive, restore)#### Session Best Practices

- Manual check-in/out entries

- Database export/import1. **Secure Cookie Flags**:

- System configuration changes   - `HttpOnly`: Prevents JavaScript access

- Admin user management   - `Secure`: Requires HTTPS (enable in production)

- RFID card assignment   - `SameSite=Lax`: Prevents CSRF attacks



---2. **Session Timeout**:

   - Default: 1 hour (3600 seconds)

## Data Protection   - Configurable via `SESSION_LIFETIME` environment variable

   - Implement absolute timeout + idle timeout

### Database Security

3. **Session Invalidation**:

#### File Permissions   - Logout clears session completely

   - SECRET_KEY rotation invalidates all sessions

```bash   - No session persistence across restarts (by design)

# Database file - read/write owner only

sudo chown picontrol:picontrol /var/lib/picontrol/pi_control.db### Multi-Factor Authentication (Future)

sudo chmod 600 /var/lib/picontrol/pi_control.db

Consider implementing 2FA for admin accounts:

# Database directory - restricted access- TOTP (Time-based One-Time Password)

sudo chown picontrol:picontrol /var/lib/picontrol- Hardware tokens (YubiKey)

sudo chmod 750 /var/lib/picontrol- Email/SMS verification codes

```

---

#### Encryption at Rest

## Data Protection

**Option 1: Full Disk Encryption (Recommended)**

```bash### Database Security

# Enable during Raspberry Pi OS installation

# Uses LUKS encryption for entire filesystem#### File Permissions

# Protects all data if device is stolen

``````bash

# Set restrictive permissions on database

**Option 2: Database Encryption with SQLCipher**sudo chown picontrol:picontrol /var/lib/picontrol/pi_control.db

```bashsudo chmod 600 /var/lib/picontrol/pi_control.db

# Requires replacing SQLite with SQLCipher

pip install sqlcipher3-binary# Protect directory

sudo chmod 750 /var/lib/picontrol

# Modify app/db.py to use SQLCipher engine```

# Add encryption key management

```#### Encryption at Rest



#### SQL Injection PreventionFor sensitive deployments, encrypt the database:



**Defense mechanisms:**```bash

# Option 1: Full disk encryption (recommended)

1. **ORM Usage** - All queries via SQLModel ORM (parameterized queries)# Enable during Raspberry Pi OS installation (LUKS)

2. **No Raw SQL** - Avoid `session.execute()` with string concatenation

3. **Input Validation** - Pydantic models validate all inputs before database# Option 2: SQLCipher for database encryption

4. **Type Safety** - SQLModel enforces type checking# Requires replacing SQLite with SQLCipher build

pip install sqlcipher3

**Secure example:**```

```python

# Safe - parameterized via ORM#### SQL Injection Prevention

employee = session.get(Employee, employee_id)

- **ORM Usage**: All queries via SQLModel ORM (parameterized)

# UNSAFE - never do this:- **No Raw SQL**: Avoid `session.execute()` with string concatenation

# query = f"SELECT * FROM employee WHERE id = '{employee_id}'"- **Input Validation**: Pydantic models validate all inputs

# session.execute(query)

``````python

# Safe (parameterized via ORM)

### Data Minimizationemployee = session.get(Employee, employee_id)



**Collect only necessary data:**# NEVER do this (vulnerable to SQL injection):

# session.execute(f"SELECT * FROM employee WHERE id = '{employee_id}'")

✅ **Required:**```

- Employee document ID

- Employee name### Data Minimization

- RFID UID (for access control)

- Check-in/out timestampsOnly collect and store necessary data:

- Admin usernames (for audit)- Employee document ID and name (required)

- RFID UID (for access control)

❌ **Avoid storing:**- Check-in/out timestamps (for reporting)

- Social Security Numbers- Admin usernames (for audit trails)

- Personal addresses

- Phone numbers (unless required)**Do NOT store**:

- Biometric data (beyond RFID)- Social Security Numbers

- Financial information- Personal addresses

- Phone numbers (unless explicitly needed)

### Data Retention- Biometric data beyond RFID



**Configure automatic cleanup:**### Data Retention



```bash```bash

# Default retention: 4 years# Configure automatic cleanup (default: 4 years retention)

# Configure via environment or script modification# Edit cleanup script or add cron job:

0 2 * * 0 /opt/picontrol/.venv/bin/python /opt/picontrol/tools/cleanup_old_records.py

# Dry-run to preview deletions

python tools/cleanup_old_records.py --dry-run# Manual cleanup with dry-run

python tools/cleanup_old_records.py --dry-run

# Execute cleanup

python tools/cleanup_old_records.py# Execute cleanup

python tools/cleanup_old_records.py

# Add to cron for automation```

0 2 * * 0 /opt/picontrol/.venv/bin/python /opt/picontrol/tools/cleanup_old_records.py

```### Backup Security



### Backup Security#### Encrypted Backups



#### Encrypted Backups```bash

# Create encrypted backup with GPG

```bashgpg --symmetric --cipher-algo AES256 /var/lib/picontrol/pi_control.db

# Create encrypted backup with GPG

gpg --symmetric --cipher-algo AES256 \# Restore from encrypted backup

  /var/lib/picontrol/pi_control.dbgpg --decrypt pi_control.db.gpg > /var/lib/picontrol/pi_control.db

```

# Restore from encrypted backup

gpg --decrypt pi_control.db.gpg > /var/lib/picontrol/pi_control.db#### Backup Access Control

sudo chown picontrol:picontrol /var/lib/picontrol/pi_control.db

sudo chmod 600 /var/lib/picontrol/pi_control.db```bash

```# Store backups with restrictive permissions

sudo chmod 600 /var/backups/picontrol/*.db

#### Backup Best Practicessudo chown root:root /var/backups/picontrol/*.db



1. **Encrypt all backups** - Use GPG or similar encryption# Use separate backup user (principle of least privilege)

2. **Restrict backup permissions** - `chmod 600` on backup files```

3. **Off-site storage** - Store backups on separate device/network

4. **Test restores regularly** - Verify backup integrity monthly#### Off-site Backup Storage

5. **Implement 3-2-1 rule** - 3 copies, 2 different media, 1 off-site

6. **Automate backup rotation** - Keep 7 daily, 4 weekly, 12 monthly- Store backups on separate device/network

- Use encrypted cloud storage (e.g., encrypted S3 bucket)

---- Implement backup rotation (3-2-1 rule)

- Test restore procedures regularly

## Network Security

---

### Firewall Configuration

## Network Security

#### UFW (Uncomplicated Firewall)

### Firewall Configuration

```bash

# Enable firewall#### UFW (Uncomplicated Firewall)

sudo ufw enable

```bash

# Default policies# Enable firewall

sudo ufw default deny incomingsudo ufw enable

sudo ufw default allow outgoing

# Default deny incoming

# Allow SSH from trusted network onlysudo ufw default deny incoming

sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcpsudo ufw default allow outgoing



# Allow application port (if not using reverse proxy)# Allow SSH (restrict to specific IP if possible)

sudo ufw allow from 192.168.1.0/24 to any port 8000 proto tcpsudo ufw allow from 192.168.1.0/24 to any port 22



# Verify configuration# Allow application port (only if not using reverse proxy)

sudo ufw status verbosesudo ufw allow from 192.168.1.0/24 to any port 8000

```

# Check status

#### iptables (Advanced Configuration)sudo ufw status verbose

```

```bash

# Flush existing rules#### iptables (Advanced)

sudo iptables -F

```bash

# Default policies# Drop all incoming except established connections

sudo iptables -P INPUT DROPsudo iptables -P INPUT DROP

sudo iptables -P FORWARD DROPsudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

sudo iptables -P OUTPUT ACCEPT

# Allow SSH from trusted network only

# Allow established connectionssudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 22 -j ACCEPT

sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow application access from local network

# Allow loopbacksudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 8000 -j ACCEPT

sudo iptables -A INPUT -i lo -j ACCEPT

# Save rules

# Allow SSH from trusted subnetsudo iptables-save > /etc/iptables/rules.v4

sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 22 -j ACCEPT```



# Allow application from local network### HTTPS/TLS Configuration

sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 8000 -j ACCEPT

#### Reverse Proxy with nginx

# Save rules

sudo iptables-save | sudo tee /etc/iptables/rules.v4```nginx

```# /etc/nginx/sites-available/picontrol



### HTTPS/TLS Configurationserver {

    listen 80;

#### nginx Reverse Proxy    server_name picontrol.example.com;

    return 301 https://$server_name$request_uri;

```nginx}

# /etc/nginx/sites-available/picontrol

server {

# Redirect HTTP to HTTPS    listen 443 ssl http2;

server {    server_name picontrol.example.com;

    listen 80;

    server_name picontrol.example.com;    # SSL certificates (use Let's Encrypt)

    return 301 https://$server_name$request_uri;    ssl_certificate /etc/letsencrypt/live/picontrol.example.com/fullchain.pem;

}    ssl_certificate_key /etc/letsencrypt/live/picontrol.example.com/privkey.pem;



# HTTPS server    # Modern SSL configuration

server {    ssl_protocols TLSv1.2 TLSv1.3;

    listen 443 ssl http2;    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';

    server_name picontrol.example.com;    ssl_prefer_server_ciphers on;

    ssl_session_cache shared:SSL:10m;

    # SSL certificates (Let's Encrypt)    ssl_session_timeout 10m;

    ssl_certificate /etc/letsencrypt/live/picontrol.example.com/fullchain.pem;

    ssl_certificate_key /etc/letsencrypt/live/picontrol.example.com/privkey.pem;    # Security headers

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Modern SSL configuration (Mozilla Intermediate)    add_header X-Frame-Options "SAMEORIGIN" always;

    ssl_protocols TLSv1.2 TLSv1.3;    add_header X-Content-Type-Options "nosniff" always;

    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;    add_header X-XSS-Protection "1; mode=block" always;

    ssl_prefer_server_ciphers off;

    ssl_session_cache shared:SSL:10m;    # Proxy to application

    ssl_session_timeout 1d;    location / {

    ssl_session_tickets off;        proxy_pass http://127.0.0.1:8000;

        proxy_set_header Host $host;

    # OCSP stapling        proxy_set_header X-Real-IP $remote_addr;

    ssl_stapling on;        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

    ssl_stapling_verify on;        proxy_set_header X-Forwarded-Proto $scheme;

    }

    # Security headers}

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;```

    add_header X-Frame-Options "SAMEORIGIN" always;

    add_header X-Content-Type-Options "nosniff" always;#### Let's Encrypt SSL Certificate

    add_header X-XSS-Protection "1; mode=block" always;

    add_header Referrer-Policy "strict-origin-when-cross-origin" always;```bash

# Install certbot

    # Proxy configurationsudo apt install certbot python3-certbot-nginx

    location / {

        proxy_pass http://127.0.0.1:8000;# Obtain certificate

        proxy_set_header Host $host;sudo certbot --nginx -d picontrol.example.com

        proxy_set_header X-Real-IP $remote_addr;

        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;# Auto-renewal (certbot creates cron job automatically)

        proxy_set_header X-Forwarded-Proto $scheme;sudo certbot renew --dry-run

        ```

        # Timeouts

        proxy_connect_timeout 60s;### Network Isolation

        proxy_send_timeout 60s;

        proxy_read_timeout 60s;- **VLAN Segmentation**: Isolate PiControl on management VLAN

    }- **No Internet Exposure**: Keep on local network only

}- **VPN Access**: Use VPN for remote administration

```- **MAC Filtering**: Restrict network access by MAC address



#### SSL Certificate (Let's Encrypt)---



```bash## System Hardening

# Install certbot

sudo apt install certbot python3-certbot-nginx### Raspberry Pi OS Security



# Obtain certificate#### System Updates

sudo certbot --nginx -d picontrol.example.com

```bash

# Test auto-renewal# Update system regularly

sudo certbot renew --dry-runsudo apt update

sudo apt upgrade -y

# Auto-renewal is configured automatically via systemd timer

```# Enable automatic security updates

sudo apt install unattended-upgrades

### Network Isolationsudo dpkg-reconfigure -plow unattended-upgrades

```

**Recommended configurations:**

#### Disable Unnecessary Services

1. **VLAN Segmentation** - Place on isolated management VLAN

2. **No Internet Exposure** - Keep on local network only```bash

3. **VPN Access** - Use VPN for remote administration# List running services

4. **MAC Filtering** - Restrict network access by MAC addresssudo systemctl list-units --type=service --state=running

5. **Port Security** - Disable unused switch ports

# Disable unnecessary services

---sudo systemctl disable bluetooth

sudo systemctl disable avahi-daemon

## System Hardeningsudo systemctl disable triggerhappy

```

### Raspberry Pi OS Security

#### SSH Hardening

#### System Updates

```bash

```bash# Edit SSH config

# Update package listssudo nano /etc/ssh/sshd_config

sudo apt update

# Recommended settings:

# Upgrade all packagesPermitRootLogin no

sudo apt upgrade -yPasswordAuthentication no

PubkeyAuthentication yes

# Install security updates automaticallyX11Forwarding no

sudo apt install unattended-upgrades apt-listchangesMaxAuthTries 3

sudo dpkg-reconfigure -plow unattended-upgradesClientAliveInterval 300

```ClientAliveCountMax 2



#### Disable Unnecessary Services# Restart SSH

sudo systemctl restart sshd

```bash```

# List running services

sudo systemctl list-units --type=service --state=running### Application User Isolation



# Disable unused services```bash

sudo systemctl disable bluetooth.service# Create dedicated system user (no login shell)

sudo systemctl disable avahi-daemon.servicesudo useradd -r -s /bin/false picontrol

sudo systemctl disable triggerhappy.service

sudo systemctl disable hciuart.service# Assign ownership

sudo chown -R picontrol:picontrol /opt/picontrol

# Stop immediatelysudo chown -R picontrol:picontrol /var/lib/picontrol

sudo systemctl stop bluetooth.service avahi-daemon.servicesudo chown -R picontrol:picontrol /var/log/picontrol

``````



#### SSH Hardening### File System Permissions



Edit SSH configuration:```bash

```bash# Application directory (read-only for service user)

sudo nano /etc/ssh/sshd_configsudo chmod -R 755 /opt/picontrol

```sudo chmod 750 /opt/picontrol/.venv



**Recommended settings:**# Data directory (read-write only for service user)

```sudo chmod 750 /var/lib/picontrol

# Disable root loginsudo chmod 600 /var/lib/picontrol/pi_control.db

PermitRootLogin no

# Log directory

# Disable password authenticationsudo chmod 750 /var/log/picontrol

PasswordAuthentication nosudo chmod 640 /var/log/picontrol/*.log

PubkeyAuthentication yes

# Configuration files

# Disable X11 forwardingsudo chmod 600 /etc/default/picontrol

X11Forwarding no```



# Limit authentication attempts### systemd Service Hardening

MaxAuthTries 3

```ini

# Set timeouts# /etc/systemd/system/picontrol.service

ClientAliveInterval 300

ClientAliveCountMax 2[Service]

# Security hardening

# Limit usersNoNewPrivileges=true

AllowUsers picontrol-adminPrivateTmp=true

ProtectSystem=strict

# Use strong ciphers onlyProtectHome=true

Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.comReadWritePaths=/var/lib/picontrol /var/log/picontrol

MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.comProtectKernelTunables=true

KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512ProtectControlGroups=true

```RestrictRealtime=true

RestrictNamespaces=true

Restart SSH:SystemCallFilter=@system-service

```bashSystemCallErrorNumber=EPERM

sudo systemctl restart sshd```

```

---

### Application User Isolation

## RFID Security

```bash

# Create dedicated system user (no login shell)### RFID Card Security

sudo useradd -r -s /bin/false picontrol

#### Cloning Prevention

# Set ownership

sudo chown -R picontrol:picontrol /opt/picontrolWhile EM4100/EM4102 cards are clonable:

sudo chown -R picontrol:picontrol /var/lib/picontrol- Use physical security (supervised areas)

sudo chown -R picontrol:picontrol /var/log/picontrol- Implement card + PIN authentication (future enhancement)

```- Consider upgrading to encrypted RFID cards (e.g., MIFARE DESFire)

- Monitor for suspicious activity patterns

### File System Permissions

#### Card Assignment Security

```bash

# Application directory (read-only for service user)```bash

sudo chmod -R 755 /opt/picontrol# Protect RFID write operation (RC522)

sudo chmod 750 /opt/picontrol/.venv# Ensure wrapper script has restricted permissions

sudo chmod 750 /usr/local/bin/picontrol-write-rfid

# Database directory (read-write for service user only)sudo chown root:picontrol /usr/local/bin/picontrol-write-rfid

sudo chmod 750 /var/lib/picontrol

sudo chmod 600 /var/lib/picontrol/pi_control.db# Sudoers entry (limited scope)

# picontrol ALL=(ALL) NOPASSWD: /usr/local/bin/picontrol-write-rfid *

# Log directory```

sudo chmod 750 /var/log/picontrol

sudo chmod 640 /var/log/picontrol/*.log#### RFID Reader Physical Security



# Configuration files- Mount reader in tamper-evident enclosure

sudo chmod 600 /etc/default/picontrol- Position in supervised area with camera coverage

- Use cable locks to prevent theft

# Ensure correct ownership- Monitor USB device connections

sudo chown -R picontrol:picontrol /var/lib/picontrol

sudo chown -R picontrol:picontrol /var/log/picontrol### Anti-Spoofing Measures

sudo chown root:root /etc/default/picontrol

```1. **Rate Limiting**: Prevent rapid check-in attempts

2. **Anomaly Detection**: Flag unusual patterns (multiple locations)

### systemd Service Hardening3. **Time-Based Rules**: Restrict check-ins to business hours

4. **Geolocation**: Validate check-ins from known locations (future)

Add security directives to service file:

---

```ini

# /etc/systemd/system/picontrol.service## Secure Configuration



[Service]### Environment Variables

User=picontrol

Group=picontrol#### SECRET_KEY Generation

WorkingDirectory=/opt/picontrol

```bash

# Security hardening# Generate cryptographically secure secret key

NoNewPrivileges=truepython3 -c "import secrets; print(secrets.token_urlsafe(32))"

PrivateTmp=true

ProtectSystem=strict# Set in environment file

ProtectHome=trueecho "SECRET_KEY=<generated-key>" | sudo tee -a /etc/default/picontrol

ReadWritePaths=/var/lib/picontrol /var/log/picontrolsudo chmod 600 /etc/default/picontrol

ProtectKernelTunables=true```

ProtectKernelModules=true

ProtectControlGroups=true#### Environment File Template

RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6

RestrictNamespaces=true```bash

RestrictRealtime=true# /etc/default/picontrol

RestrictSUIDSGID=true

LockPersonality=true# CRITICAL: Generate unique SECRET_KEY

SystemCallFilter=@system-serviceSECRET_KEY=<generate-with-secrets-module>

SystemCallErrorNumber=EPERM

SystemCallArchitectures=native# Database configuration

PICONTROL_DB_DIR=/var/lib/picontrol

# Resource limits

LimitNOFILE=1024# Server configuration

LimitNPROC=512PICONTROL_HOST=127.0.0.1  # Bind to localhost if using reverse proxy

```PICONTROL_PORT=8000



Reload systemd and restart:# Session configuration

```bashSESSION_LIFETIME=3600

sudo systemctl daemon-reload

sudo systemctl restart picontrol# Logging

```LOG_LEVEL=INFO

LOG_FILE=/var/log/picontrol/app.log

---

# Backup configuration

## RFID SecurityPICONTROL_BACKUP_DIR=/var/backups/picontrol

```

### RFID Card Security

### Configuration Validation

#### Threat Assessment

```bash

**Vulnerabilities of EM4100/EM4102 cards:**# Verify SECRET_KEY is set and not default

- Low-cost cards are easily cloneablesudo systemctl show picontrol --property=Environment | grep SECRET_KEY

- No encryption or authentication

- Passive cards can be read remotely (up to ~10cm)# Check file permissions

- No write protectionsudo ls -la /etc/default/picontrol

# Should be: -rw------- 1 root root

**Mitigation strategies:**

1. **Physical security** - Supervised check-in areas# Validate database permissions

2. **Anomaly detection** - Flag suspicious patternssudo ls -la /var/lib/picontrol/pi_control.db

3. **Card + PIN** - Future enhancement for high security# Should be: -rw------- 1 picontrol picontrol

4. **Upgrade cards** - Consider encrypted RFID (MIFARE DESFire)```



#### Card Assignment Security---



```bash## Monitoring & Logging

# Protect RFID write operation wrapper

sudo chown root:picontrol /usr/local/bin/picontrol-write-rfid### Application Logging

sudo chmod 750 /usr/local/bin/picontrol-write-rfid

#### Admin Audit Logs

# Verify sudoers entry is restrictive

# /etc/sudoers.d/picontrol:All administrative actions are logged to the `adminaction` table:

# picontrol ALL=(ALL) NOPASSWD: /usr/local/bin/picontrol-write-rfid *

``````python

# Logged actions include:

#### RFID Reader Physical Security- create_employee

- update_employee

**Best practices:**- archive_employee

1. Mount reader in tamper-evident enclosure- restore_employee

2. Position in area with camera coverage- assign_rfid

3. Use cable locks to prevent theft- manual_checkin

4. Monitor USB device connections- export_db

5. Implement tamper detection alerts- import_db

- change_password

### Anti-Spoofing Measures- rotate_secret

```

**Recommended implementations:**

#### Viewing Audit Logs

1. **Rate Limiting**

   - Limit check-ins to once per minute per card```bash

   - Prevent rapid-fire spoofing attempts# Via web interface

# Navigate to: http://<server>/admin/logs

2. **Anomaly Detection**

   - Flag impossible travel times (multiple locations)# Via database query

   - Alert on unusual check-in patternssqlite3 /var/lib/picontrol/pi_control.db "SELECT * FROM adminaction ORDER BY timestamp DESC LIMIT 20;"

   - Detect duplicate simultaneous check-ins```



3. **Time-Based Rules**### System Logging

   - Restrict check-ins to business hours

   - Require manual approval for off-hours access#### systemd Journal



4. **Geolocation Validation** (Future)```bash

   - Validate check-ins from known locations# View service logs

   - GPS verification for mobile check-inssudo journalctl -u picontrol -f



---# View logs since last boot

sudo journalctl -u picontrol -b

## Secure Configuration

# Export logs to file

### Environment Variablessudo journalctl -u picontrol --since "7 days ago" > picontrol_logs.txt

```

#### SECRET_KEY Generation

#### Log Rotation

**Critical: Never use default values in production**

```bash

```bash# Configure logrotate for application logs

# Generate cryptographically secure 32-byte keysudo nano /etc/logrotate.d/picontrol

python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Add configuration:

# Example output:/var/log/picontrol/*.log {

# x4yM9pL3kN7qR2vC5wZ8tA6bD1eF0gH4jK8mN2pQ5sT9    daily

    rotate 30

# Set in environment file    compress

echo "SECRET_KEY=<generated-key>" | sudo tee /etc/default/picontrol    delaycompress

sudo chmod 600 /etc/default/picontrol    missingok

sudo chown root:root /etc/default/picontrol    notifempty

```    create 640 picontrol picontrol

    sharedscripts

#### Environment File Configuration    postrotate

        systemctl reload picontrol > /dev/null 2>&1 || true

```bash    endscript

# /etc/default/picontrol}

```

# CRITICAL: Set unique SECRET_KEY (required)

SECRET_KEY=<generate-using-secrets-module>### Security Monitoring



# Database configuration#### Failed Login Attempts

PICONTROL_DB_DIR=/var/lib/picontrol

Monitor for brute force attacks:

# Server configuration

PICONTROL_HOST=127.0.0.1  # Localhost if using reverse proxy```bash

PICONTROL_PORT=8000# Check for repeated failed logins (implement in application)

# Future enhancement: Add failed login tracking to database

# Session configuration

SESSION_LIFETIME=3600  # 1 hour in seconds# Use fail2ban for SSH protection

sudo apt install fail2ban

# Loggingsudo systemctl enable fail2ban

LOG_LEVEL=INFO```

LOG_FILE=/var/log/picontrol/app.log

#### Intrusion Detection

# Backup configuration

PICONTROL_BACKUP_DIR=/var/backups/picontrol```bash

```# Install and configure AIDE (Advanced Intrusion Detection Environment)

sudo apt install aide

### Configuration Validationsudo aideinit

sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db

```bash

# Verify SECRET_KEY is set and not default# Run integrity check

sudo systemctl show picontrol --property=Environment | grep SECRET_KEYsudo aide --check



# Check environment file permissions# Schedule regular checks

ls -la /etc/default/picontrolecho "0 5 * * * root /usr/bin/aide --check" | sudo tee -a /etc/crontab

# Expected: -rw------- 1 root root```



# Validate database permissions#### Log Analysis

ls -la /var/lib/picontrol/pi_control.db

# Expected: -rw------- 1 picontrol picontrol```bash

# Monitor for suspicious patterns

# Test configurationsudo journalctl -u picontrol | grep -i "error\|fail\|unauthorized"

sudo systemctl restart picontrol

sudo systemctl status picontrol# Check database access patterns

```sudo lsof /var/lib/picontrol/pi_control.db



---# Monitor network connections

sudo ss -tulpn | grep :8000

## Monitoring & Logging```



### Application Logging---



#### Admin Audit Logs## Incident Response



All administrative actions are logged to `adminaction` table:### Incident Response Plan



**Logged operations:**#### Detection

- `create_employee` - New employee creation

- `update_employee` - Employee information changes1. **Automated Alerts**: Configure monitoring for:

- `archive_employee` - Employee archival   - Service failures

- `restore_employee` - Employee restoration   - Repeated failed login attempts

- `assign_rfid` - RFID card assignments   - Database integrity violations

- `manual_checkin` - Manual check-in entries   - Unusual access patterns

- `export_db` - Database exports

- `import_db` - Database imports2. **Manual Review**: Regular review of:

- `change_password` - Password changes   - Admin audit logs

- `rotate_secret` - Secret key rotation   - System logs

   - Network traffic patterns

#### Viewing Audit Logs   - Database changes



**Web interface:**#### Containment

```

Navigate to: http://<server>/admin/logs```bash

Filter by: date range, admin user, action type# Immediate actions if breach suspected:

```

# 1. Isolate system

**Database query:**sudo ufw deny incoming

```bashsudo systemctl stop picontrol

sqlite3 /var/lib/picontrol/pi_control.db \

  "SELECT * FROM adminaction ORDER BY timestamp DESC LIMIT 20;"# 2. Create forensic backup

```sudo dd if=/dev/mmcblk0 of=/mnt/external/pi-backup.img bs=4M status=progress



**Export logs:**# 3. Preserve logs

```bashsudo journalctl -u picontrol > /mnt/external/incident-logs.txt

sqlite3 /var/lib/picontrol/pi_control.db \sudo cp -r /var/log/picontrol /mnt/external/

  "SELECT * FROM adminaction WHERE timestamp > date('now', '-7 days');" \```

  > audit_logs.csv

```#### Eradication



### System Logging```bash

# 1. Rotate all credentials

#### systemd Journalpython tools/rotate_secret.py

python tools/reset_admin.py

```bash

# Real-time log monitoring# 2. Update system and dependencies

sudo journalctl -u picontrol -fsudo apt update && sudo apt upgrade -y

pip install --upgrade -r requirements.txt

# View logs since last boot

sudo journalctl -u picontrol -b# 3. Review and remove any malicious code

git diff HEAD~10..HEAD  # Review recent changes

# View logs from last 24 hours```

sudo journalctl -u picontrol --since "24 hours ago"

#### Recovery

# Export logs to file

sudo journalctl -u picontrol --since "7 days ago" \```bash

  > /var/log/picontrol_journal.txt# 1. Restore from known-good backup

```sudo systemctl stop picontrol

sudo cp /var/backups/picontrol/backup_clean.db /var/lib/picontrol/pi_control.db

#### Log Rotation

# 2. Restart service

Configure logrotate for application logs:sudo systemctl start picontrol



```bash# 3. Verify integrity

# /etc/logrotate.d/picontrolsudo systemctl status picontrol

/var/log/picontrol/*.log {curl http://localhost:8000/

    daily```

    rotate 30

    compress#### Lessons Learned

    delaycompress

    missingokDocument and review:

    notifempty- Timeline of incident

    create 640 picontrol picontrol- Root cause analysis

    sharedscripts- Actions taken

    postrotate- Process improvements

        systemctl reload picontrol > /dev/null 2>&1 || true- Updated security controls

    endscript

}---

```

## Security Maintenance

Test configuration:

```bash### Regular Security Tasks

sudo logrotate -d /etc/logrotate.d/picontrol

```#### Daily

- [ ] Review admin audit logs

### Security Monitoring- [ ] Check service status and logs

- [ ] Monitor disk space and resource usage

#### Failed Login Detection

#### Weekly

**Manual review:**- [ ] Review failed login attempts

```bash- [ ] Check backup integrity

# Search logs for failed login attempts- [ ] Update application dependencies

sudo journalctl -u picontrol | grep -i "invalid credentials"- [ ] Review firewall rules and network access



# Count failed attempts by IP (if X-Forwarded-For logged)#### Monthly

sudo journalctl -u picontrol | grep "invalid credentials" | \- [ ] Rotate credentials (admin password, SECRET_KEY)

  grep -oP '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' | sort | uniq -c- [ ] Audit user accounts (remove inactive)

```- [ ] Review and update security policies

- [ ] Test disaster recovery procedures

#### Intrusion Detection (AIDE)- [ ] Run security vulnerability scan



```bash#### Quarterly

# Install AIDE- [ ] Full security audit

sudo apt install aide- [ ] Penetration testing (if applicable)

- [ ] Review access control lists

# Initialize database- [ ] Update incident response plan

sudo aideinit- [ ] Security awareness training



# Copy baseline### Credential Rotation

sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db

#### SECRET_KEY Rotation

# Run integrity check

sudo aide --check```bash

# Generate new SECRET_KEY

# Automate checks (daily at 5 AM)python tools/rotate_secret.py

echo "0 5 * * * root /usr/bin/aide --check" | sudo tee -a /etc/crontab

```# Update environment file

sudo nano /etc/default/picontrol

#### Log Analysis# Replace SECRET_KEY value



```bash# Restart service (invalidates all sessions)

# Monitor for error patternssudo systemctl restart picontrol

sudo journalctl -u picontrol | grep -E "ERROR|CRITICAL|FAIL"```



# Check database access#### Admin Password Rotation

sudo lsof /var/lib/picontrol/pi_control.db

```bash

# Monitor network connections# Via web interface: /admin/configuration

sudo ss -tulpn | grep :8000# Or via CLI:

python tools/reset_admin.py

# Check disk usage

df -h /var/lib/picontrol# Change immediately after login

du -sh /var/lib/picontrol/*```

```

### Vulnerability Management

---

#### Dependency Updates

## Incident Response

```bash

### Incident Response Plan# Check for outdated packages

pip list --outdated

#### Phase 1: Detection

# Update dependencies

**Automated monitoring:**pip install --upgrade -r requirements.txt

- Service failures and crashes

- Repeated failed login attempts# Test after updates

- Database integrity violationsPYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest -v

- Unusual access patterns```

- Resource exhaustion (CPU, memory, disk)

#### Security Scanning

**Manual review triggers:**

- User reports of suspicious activity```bash

- Anomalous check-in patterns# Scan for known vulnerabilities in dependencies

- Unexpected system behaviorpip install safety

- External security advisoriessafety check



#### Phase 2: Containment# Scan for common misconfigurations

pip install bandit

**Immediate actions if breach suspected:**bandit -r app/

```

```bash

# 1. Isolate system from network---

sudo ufw deny incoming

sudo ufw status## Compliance Considerations



# 2. Stop the service### GDPR Compliance

sudo systemctl stop picontrol

For deployments in EU/EEA:

# 3. Create forensic backup (preserve evidence)

sudo dd if=/dev/mmcblk0 of=/mnt/external/forensic-backup.img \1. **Data Minimization**: Only collect necessary data

  bs=4M status=progress2. **Right to Erasure**: Implement employee data deletion (archive function)

3. **Data Portability**: Support data export (DB export feature)

# 4. Preserve all logs4. **Consent**: Document employee consent for data collection

sudo journalctl -u picontrol > /mnt/external/incident-systemd.log5. **Data Protection**: Implement encryption and access controls

sudo cp -r /var/log/picontrol /mnt/external/logs-backup/6. **Breach Notification**: 72-hour breach notification requirement

sqlite3 /var/lib/picontrol/pi_control.db \

  ".dump" > /mnt/external/database-dump.sql### Data Retention Policies



# 5. Document current state```python

sudo systemctl status picontrol > /mnt/external/service-status.txt# Configure retention in cleanup script

sudo lsof -p $(pgrep -f picontrol) > /mnt/external/open-files.txt# Default: 4 years + 1 day

```# Adjust based on legal requirements:



#### Phase 3: Eradication# In tools/cleanup_old_records.py:

RETENTION_YEARS = 4  # Modify as needed

```bash```

# 1. Rotate all credentials

cd /opt/picontrol### Access Control Documentation

sudo -u picontrol /opt/picontrol/.venv/bin/python tools/rotate_secret.py

sudo -u picontrol /opt/picontrol/.venv/bin/python tools/reset_admin.pyMaintain records of:

- Who has admin access

# 2. Update system and dependencies- When access was granted/revoked

sudo apt update && sudo apt full-upgrade -y- Purpose of access

cd /opt/picontrol- Regular access reviews

source .venv/bin/activate

pip install --upgrade -r requirements.txt---



# 3. Review code for tampering## Security Auditing

git status

git diff HEAD### Self-Assessment Checklist

git log --oneline -20

#### Authentication

# 4. Scan for malware (optional)- [ ] Strong passwords enforced

sudo apt install clamav- [ ] Default credentials changed

sudo freshclam- [ ] Session timeout configured

sudo clamscan -r /opt/picontrol- [ ] Secure session management

```- [ ] Failed login tracking



#### Phase 4: Recovery#### Authorization

- [ ] Admin-only operations protected

```bash- [ ] Least privilege principle applied

# 1. Restore from known-good backup- [ ] Regular access reviews

sudo systemctl stop picontrol

sudo cp /var/backups/picontrol/verified-clean.db \#### Data Protection

  /var/lib/picontrol/pi_control.db- [ ] Database encrypted at rest

sudo chown picontrol:picontrol /var/lib/picontrol/pi_control.db- [ ] Backups encrypted

sudo chmod 600 /var/lib/picontrol/pi_control.db- [ ] Sensitive data not logged

- [ ] Data retention policy enforced

# 2. Re-enable network access

sudo ufw default allow outgoing#### Network Security

sudo ufw allow from 192.168.1.0/24 to any port 8000- [ ] HTTPS enabled with valid certificate

- [ ] Firewall configured and active

# 3. Restart service- [ ] No unnecessary ports exposed

sudo systemctl start picontrol- [ ] Network segmentation implemented



# 4. Verify integrity#### System Security

sudo systemctl status picontrol- [ ] OS and packages updated

curl http://localhost:8000/- [ ] Unnecessary services disabled

sqlite3 /var/lib/picontrol/pi_control.db "PRAGMA integrity_check;"- [ ] File permissions restrictive

```- [ ] Service running as non-root user



#### Phase 5: Post-Incident Review#### Monitoring

- [ ] Audit logging enabled

**Document the incident:**- [ ] Log retention configured

1. Timeline of events- [ ] Security events monitored

2. Attack vector identification- [ ] Incident response plan documented

3. Root cause analysis

4. Actions taken### External Security Assessment

5. Data affected

6. Lessons learnedConsider professional security audit:

7. Process improvements- Penetration testing

- Code review

**Update security controls:**- Configuration audit

- Implement additional monitoring- Compliance assessment

- Enhance detection capabilities

- Update incident response plan### Security Reporting

- Conduct security training

Report security issues responsibly:

---- **Email**: [Repository maintainer - see GitHub profile]

- **Do NOT**: Open public GitHub issues for security vulnerabilities

## Security Maintenance- **Provide**: Detailed description, steps to reproduce, impact assessment

- **Response Time**: Expect acknowledgment within 48 hours

### Maintenance Schedule

---

#### Daily Tasks

## Additional Resources

- [ ] Review admin audit logs for suspicious activity

- [ ] Check service status and error logs### Security Tools

- [ ] Monitor disk space and resource usage

- [ ] Verify backup completion- **Vulnerability Scanning**: OWASP ZAP, Nikto

- **Dependency Checking**: Safety, Snyk

#### Weekly Tasks- **Code Analysis**: Bandit, Pylint

- **Penetration Testing**: Metasploit, Burp Suite

- [ ] Review failed login attempts

- [ ] Verify backup integrity (test restore)### References

- [ ] Update application dependencies

- [ ] Review firewall logs- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

- [ ] Check for system updates- [CIS Benchmarks for Debian](https://www.cisecurity.org/cis-benchmarks/)

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

#### Monthly Tasks- [GDPR Official Text](https://gdpr-info.eu/)



- [ ] Rotate admin credentials### Community

- [ ] Audit user accounts (remove inactive)

- [ ] Review and update security policies- **GitHub Issues**: Bug reports and feature requests

- [ ] Test disaster recovery procedures- **Security Advisories**: Watch repository for security updates

- [ ] Run vulnerability scan- **Discussions**: Community security discussions

- [ ] Review access control lists

---

#### Quarterly Tasks

**Last Updated**: November 2025  

- [ ] Full security audit**Version**: 1.0  

- [ ] Penetration testing (if applicable)**Maintained By**: PiControl Security Team

- [ ] Review and update documentation

- [ ] Update incident response plan*This document should be reviewed and updated regularly to reflect current security best practices and emerging threats.*

- [ ] Conduct security awareness training
- [ ] Rotate SECRET_KEY

### Credential Rotation

#### SECRET_KEY Rotation

```bash
# 1. Generate new key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 2. Update environment file
sudo nano /etc/default/picontrol
# Replace SECRET_KEY value with new key

# 3. Restart service (invalidates all sessions)
sudo systemctl restart picontrol

# 4. Notify users to re-login
```

#### Admin Password Rotation

**Via web interface:**
```
1. Navigate to /admin/configuration
2. Enter new password twice
3. Click "Change Password"
4. Log in with new password
```

**Via command line:**
```bash
cd /opt/picontrol
sudo -u picontrol /opt/picontrol/.venv/bin/python tools/reset_admin.py
# Change password immediately after login
```

### Vulnerability Management

#### Dependency Updates

```bash
# Check for outdated packages
cd /opt/picontrol
source .venv/bin/activate
pip list --outdated

# Update all dependencies
pip install --upgrade -r requirements.txt

# Run tests after updates
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest -v

# Restart service
sudo systemctl restart picontrol
```

#### Security Scanning

```bash
# Install security tools
pip install safety bandit

# Scan dependencies for known vulnerabilities
safety check --json

# Scan code for security issues
bandit -r app/ -f json -o bandit-report.json

# Review findings
cat bandit-report.json | jq '.results'
```

---

## Compliance

### GDPR Compliance

**For deployments in EU/EEA:**

#### Data Protection Requirements

1. **Data Minimization**
   - Collect only necessary employee data
   - Avoid storing sensitive personal information
   - Regular review of data collection practices

2. **Right to Erasure**
   - Implement employee data deletion (archive function)
   - Provide data export for deleted records
   - Document deletion procedures

3. **Data Portability**
   - Support data export via database export feature
   - Provide data in machine-readable format (SQLite, JSON)
   - Enable employee access to their own data

4. **Consent Management**
   - Document employee consent for data collection
   - Maintain consent records
   - Provide opt-out mechanisms where applicable

5. **Data Protection by Design**
   - Implement encryption at rest and in transit
   - Apply principle of least privilege
   - Regular security assessments

6. **Breach Notification**
   - 72-hour breach notification requirement
   - Document incident response procedures
   - Maintain breach notification contacts

### Data Retention Policy

```python
# Configure retention period (default: 4 years)
# Edit tools/cleanup_old_records.py:

RETENTION_YEARS = 4  # Adjust based on legal requirements

# Considerations:
# - Employment law requirements
# - Tax record retention
# - Audit trail compliance
# - Business needs
```

### Access Control Documentation

**Maintain records of:**
- Admin user accounts and permissions
- Access grant/revoke dates
- Purpose of admin access
- Regular access reviews (quarterly)
- Terminated user account cleanup

### Compliance Audit Trail

```bash
# Export compliance-relevant logs
sqlite3 /var/lib/picontrol/pi_control.db <<EOF
.mode csv
.output compliance_audit.csv
SELECT 
    timestamp,
    admin_username,
    action,
    details
FROM adminaction
WHERE timestamp > date('now', '-1 year')
ORDER BY timestamp DESC;
.quit
EOF
```

---

## Security Auditing

### Self-Assessment Checklist

#### Authentication & Authorization

- [ ] Strong password policy enforced
- [ ] Default credentials changed
- [ ] Session timeout configured appropriately
- [ ] Secure cookie flags enabled (Secure, HttpOnly, SameSite)
- [ ] Failed login tracking implemented
- [ ] Admin-only operations properly protected

#### Data Protection

- [ ] Database encrypted at rest (or full disk encryption)
- [ ] Backups encrypted
- [ ] Sensitive data not logged in plain text
- [ ] Data retention policy enforced
- [ ] SQL injection prevention verified
- [ ] Input validation comprehensive

#### Network Security

- [ ] HTTPS enabled with valid certificate
- [ ] TLS 1.2+ only (no SSL, TLS 1.0, TLS 1.1)
- [ ] Firewall configured and active
- [ ] No unnecessary ports exposed
- [ ] Network segmentation implemented
- [ ] Security headers configured

#### System Security

- [ ] Operating system and packages updated
- [ ] Unnecessary services disabled
- [ ] File permissions restrictive
- [ ] Service running as non-root user
- [ ] systemd security hardening applied
- [ ] SSH hardening completed

#### Monitoring & Logging

- [ ] Audit logging enabled
- [ ] Log retention configured
- [ ] Security events monitored
- [ ] Incident response plan documented
- [ ] Log rotation configured
- [ ] Intrusion detection active

### External Security Assessment

**Consider professional security services:**

1. **Penetration Testing**
   - Identify vulnerabilities before attackers
   - Test incident response procedures
   - Validate security controls

2. **Code Review**
   - Static code analysis
   - Security-focused code audit
   - Dependency vulnerability assessment

3. **Configuration Audit**
   - System hardening verification
   - Network security review
   - Access control assessment

4. **Compliance Assessment**
   - GDPR compliance review
   - Industry-specific standards
   - Best practices validation

### Security Reporting

**Report security issues responsibly:**

- **Contact:** See repository maintainer on GitHub
- **Channel:** Private security advisory (not public issues)
- **Include:** 
  - Detailed vulnerability description
  - Steps to reproduce
  - Impact assessment
  - Suggested remediation (if any)
- **Response Time:** Expect acknowledgment within 48 hours
- **Disclosure:** Coordinate public disclosure timing

---

## Resources

### Security Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| **OWASP ZAP** | Web application security scanner | `apt install zaproxy` |
| **Nikto** | Web server scanner | `apt install nikto` |
| **Safety** | Python dependency vulnerability checker | `pip install safety` |
| **Bandit** | Python code security analyzer | `pip install bandit` |
| **Lynis** | Security auditing tool | `apt install lynis` |
| **fail2ban** | Intrusion prevention | `apt install fail2ban` |
| **AIDE** | File integrity monitoring | `apt install aide` |

### Documentation References

| Resource | URL |
|----------|-----|
| **OWASP Top 10** | https://owasp.org/www-project-top-ten/ |
| **CIS Benchmarks** | https://www.cisecurity.org/cis-benchmarks/ |
| **NIST Cybersecurity Framework** | https://www.nist.gov/cyberframework |
| **GDPR Official Text** | https://gdpr-info.eu/ |
| **Mozilla SSL Config Generator** | https://ssl-config.mozilla.org/ |
| **Let's Encrypt** | https://letsencrypt.org/ |

### Community Support

- **GitHub Issues:** Bug reports and feature requests
- **Security Advisories:** Watch repository for security updates
- **Discussions:** Community security discussions

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**Maintained By:** HismarDev
