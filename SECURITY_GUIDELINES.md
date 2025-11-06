# Security Guidelines

**Comprehensive Security Guide for PiControl**

This document provides detailed security guidelines, best practices, and hardening procedures for deploying and maintaining PiControl in production environments.

---

## Table of Contents

- [Overview](#overview)
- [Threat Model](#threat-model)
- [Security Architecture](#security-architecture)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Authentication & Authorization](#authentication--authorization)
- [Data Protection](#data-protection)
- [Network Security](#network-security)
- [System Hardening](#system-hardening)
- [RFID Security](#rfid-security)
- [Secure Configuration](#secure-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Incident Response](#incident-response)
- [Security Maintenance](#security-maintenance)
- [Compliance](#compliance)
- [Security Auditing](#security-auditing)
- [Resources](#resources)

---

## Overview

PiControl is designed with security in mind, but proper deployment and configuration are critical to maintaining a secure system. This guide covers security considerations specific to employee time tracking systems and Raspberry Pi deployments.

### Security Principles

1. **Defense in Depth** - Multiple layers of security controls
2. **Least Privilege** - Minimal permissions for users and processes
3. **Secure by Default** - Safe configuration out of the box
4. **Fail Secure** - Graceful degradation without compromising security
5. **Audit Everything** - Comprehensive logging of security-relevant events

### Document Scope

This guide addresses security concerns for:
- Production deployments on Raspberry Pi
- Network-accessible installations
- Systems processing employee personal data
- GDPR/compliance-sensitive environments

---

## Threat Model

### Assets to Protect

| Asset | Description | Sensitivity |
|-------|-------------|-------------|
| **Employee Personal Data** | Names, document IDs, work hours | High |
| **Authentication Credentials** | Admin passwords, session tokens | Critical |
| **System Configuration** | Secret keys, database, service accounts | Critical |
| **Business Intelligence** | Work patterns, attendance records | Medium |

### Threat Actors

| Actor | Capability | Motivation |
|-------|-----------|------------|
| **External Attackers** | Network-based exploitation | Data theft, service disruption |
| **Malicious Insiders** | Physical/network access | Fraud, data manipulation |
| **Curious Employees** | Limited technical skills | Unauthorized access, curiosity |
| **Physical Threats** | Device access | Device theft, RFID cloning |

### Attack Vectors

1. **Network Attacks** - SQL injection, XSS, session hijacking, CSRF
2. **Physical Access** - Device tampering, RFID card cloning, USB attacks
3. **Social Engineering** - Credential theft, phishing, pretexting
4. **Privilege Escalation** - Unauthorized admin access, service exploitation
5. **Data Exfiltration** - Database theft, backup compromise, log harvesting

---

## Security Architecture

### Defense Layers

```
┌─────────────────────────────────────────┐
│  Layer 4: Physical Security             │
│  - Device access controls               │
│  - RFID reader protection               │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  Layer 3: Network Security              │
│  - Firewall rules                       │
│  - TLS encryption                       │
│  - Network segmentation                 │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  Layer 2: Application Security          │
│  - Authentication                       │
│  - Input validation                     │
│  - Session management                   │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  Layer 1: Data Security                 │
│  - Encryption at rest                   │
│  - Secure backups                       │
│  - Audit logging                        │
└─────────────────────────────────────────┘
```

### Security Components

| Component | Technology | Protection Against |
|-----------|-----------|-------------------|
| **Session Management** | Signed cookies (itsdangerous) | Session hijacking, tampering |
| **Password Storage** | bcrypt hashing | Credential theft, rainbow tables |
| **Input Validation** | Pydantic models | SQL injection, XSS, corruption |
| **HTTPS/TLS** | SSL certificates | MITM attacks, eavesdropping |
| **Audit Logging** | Database logs | Unauthorized changes, forensics |
| **Machine-ID Validation** | Hardware binding | Remote admin reset attacks |

---

## Pre-Deployment Checklist

### Critical Security Tasks

**Must complete before production deployment:**

- [ ] Generate strong SECRET_KEY (32+ random bytes)
- [ ] Change default admin password immediately
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure firewall to restrict port access
- [ ] Set restrictive file permissions on database and config files
- [ ] Create dedicated system user for the service
- [ ] Disable SSH password authentication (use keys only)
- [ ] Update Raspberry Pi OS to latest stable version
- [ ] Configure automatic security updates
- [ ] Set up encrypted backups with secure storage

### Recommended Enhancements

**Additional hardening for high-security environments:**

- [ ] Implement rate limiting for login attempts
- [ ] Add CSRF protection for state-changing operations
- [ ] Configure session timeout (recommended: 3600 seconds)
- [ ] Set up intrusion detection (fail2ban, AIDE)
- [ ] Enable AppArmor or SELinux profiles
- [ ] Restrict physical access to Raspberry Pi device
- [ ] Use separate VLANs for management traffic
- [ ] Implement database encryption at rest
- [ ] Set up centralized log aggregation and monitoring
- [ ] Create and test disaster recovery plan

---

## Authentication & Authorization

### Password Security

#### Password Policy

Enforce strong passwords for all admin accounts:

**Requirements:**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- No common words or dictionary patterns
- Unique (not reused from other services)
- Changed every 90 days

**Generate secure password:**
```bash
python3 -c "import secrets, string; chars = string.ascii_letters + string.digits + string.punctuation; print(''.join(secrets.choice(chars) for _ in range(20)))"
```

#### Password Storage

- **Algorithm:** bcrypt with salt (via Passlib)
- **Work Factor:** Default 12 rounds (configurable)
- **No plaintext:** Passwords never stored or logged in clear text
- **Salt:** Unique salt per password (automatic)

#### Password Reset

**Standard procedure (physical access required):**
```bash
# Execute on Raspberry Pi console
cd /opt/picontrol
sudo -u picontrol PICONTROL_DB_DIR=/var/lib/picontrol \
  /opt/picontrol/.venv/bin/python tools/reset_admin.py

# Password output to stdout only
# Change immediately after first login
```

### Session Management

#### Secure Configuration

```python
# Session middleware configuration (app/main.py)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY"),  # Required
    session_cookie="picontrol_session",
    max_age=3600,  # 1 hour default
    same_site="lax",
    https_only=True  # Must enable with HTTPS in production
)
```

#### Cookie Security Flags

| Flag | Purpose | Production Value |
|------|---------|------------------|
| `HttpOnly` | Prevents JavaScript access | Always enabled |
| `Secure` | Requires HTTPS | **Must enable** |
| `SameSite` | Prevents CSRF attacks | `Lax` or `Strict` |
| `Max-Age` | Session lifetime | 3600 seconds (1 hour) |

#### Session Best Practices

1. **Configure secure cookie flags** - Enable `Secure` flag when using HTTPS
2. **Set appropriate timeout** - Balance security vs. usability (default: 1 hour)
3. **Implement absolute timeout** - Force re-authentication after max duration
4. **Clear sessions on logout** - Complete session invalidation
5. **Rotate SECRET_KEY periodically** - Invalidates all existing sessions

### Authorization Controls

#### Admin Access Protection

All administrative endpoints require:
1. Valid authenticated session
2. User account with `is_admin=True` flag
3. Session not expired

**Protected operations:**
- Employee management (create, edit, archive, restore)
- Manual check-in/out entries
- Database export/import
- System configuration changes
- Admin user management
- RFID card assignment

---

## Data Protection

### Database Security

#### File Permissions

```bash
# Database file - read/write owner only
sudo chown picontrol:picontrol /var/lib/picontrol/pi_control.db
sudo chmod 600 /var/lib/picontrol/pi_control.db

# Database directory - restricted access
sudo chown picontrol:picontrol /var/lib/picontrol
sudo chmod 750 /var/lib/picontrol
```

#### Encryption at Rest

**Option 1: Full Disk Encryption (Recommended)**
```bash
# Enable during Raspberry Pi OS installation
# Uses LUKS encryption for entire filesystem
# Protects all data if device is stolen
```

**Option 2: Database Encryption with SQLCipher**
```bash
# Requires replacing SQLite with SQLCipher
pip install sqlcipher3-binary

# Modify app/db.py to use SQLCipher engine
# Add encryption key management
```

#### SQL Injection Prevention

**Defense mechanisms:**

1. **ORM Usage** - All queries via SQLModel ORM (parameterized queries)
2. **No Raw SQL** - Avoid `session.execute()` with string concatenation
3. **Input Validation** - Pydantic models validate all inputs before database
4. **Type Safety** - SQLModel enforces type checking

**Secure example:**
```python
# Safe - parameterized via ORM
employee = session.get(Employee, employee_id)

# UNSAFE - never do this:
# query = f"SELECT * FROM employee WHERE id = '{employee_id}'"
# session.execute(query)
```

### Data Minimization

**Collect only necessary data:**

✅ **Required:**
- Employee document ID
- Employee name
- RFID UID (for access control)
- Check-in/out timestamps
- Admin usernames (for audit)

❌ **Avoid storing:**
- Social Security Numbers
- Personal addresses
- Phone numbers (unless required)
- Biometric data (beyond RFID)
- Financial information

### Data Retention

**Configure automatic cleanup:**

```bash
# Default retention: 4 years
# Configure via environment or script modification

# Dry-run to preview deletions
python tools/cleanup_old_records.py --dry-run

# Execute cleanup
python tools/cleanup_old_records.py

# Add to cron for automation
0 2 * * 0 /opt/picontrol/.venv/bin/python /opt/picontrol/tools/cleanup_old_records.py
```

### Backup Security

#### Encrypted Backups

```bash
# Create encrypted backup with GPG
gpg --symmetric --cipher-algo AES256 \
  /var/lib/picontrol/pi_control.db

# Restore from encrypted backup
gpg --decrypt pi_control.db.gpg > /var/lib/picontrol/pi_control.db
sudo chown picontrol:picontrol /var/lib/picontrol/pi_control.db
sudo chmod 600 /var/lib/picontrol/pi_control.db
```

#### Backup Best Practices

1. **Encrypt all backups** - Use GPG or similar encryption
2. **Restrict backup permissions** - `chmod 600` on backup files
3. **Off-site storage** - Store backups on separate device/network
4. **Test restores regularly** - Verify backup integrity monthly
5. **Implement 3-2-1 rule** - 3 copies, 2 different media, 1 off-site
6. **Automate backup rotation** - Keep 7 daily, 4 weekly, 12 monthly

---

## Network Security

### Firewall Configuration

#### UFW (Uncomplicated Firewall)

```bash
# Enable firewall
sudo ufw enable

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH from trusted network only
sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcp

# Allow application port (if not using reverse proxy)
sudo ufw allow from 192.168.1.0/24 to any port 8000 proto tcp

# Verify configuration
sudo ufw status verbose
```

#### iptables (Advanced Configuration)

```bash
# Flush existing rules
sudo iptables -F

# Default policies
sudo iptables -P INPUT DROP
sudo iptables -P FORWARD DROP
sudo iptables -P OUTPUT ACCEPT

# Allow established connections
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow loopback
sudo iptables -A INPUT -i lo -j ACCEPT

# Allow SSH from trusted subnet
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 22 -j ACCEPT

# Allow application from local network
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 8000 -j ACCEPT

# Save rules
sudo iptables-save | sudo tee /etc/iptables/rules.v4
```

### HTTPS/TLS Configuration

#### nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/picontrol

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name picontrol.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name picontrol.example.com;

    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/picontrol.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/picontrol.example.com/privkey.pem;

    # Modern SSL configuration (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Proxy configuration
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

#### SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d picontrol.example.com

# Test auto-renewal
sudo certbot renew --dry-run

# Auto-renewal is configured automatically via systemd timer
```

### Network Isolation

**Recommended configurations:**

1. **VLAN Segmentation** - Place on isolated management VLAN
2. **No Internet Exposure** - Keep on local network only
3. **VPN Access** - Use VPN for remote administration
4. **MAC Filtering** - Restrict network access by MAC address
5. **Port Security** - Disable unused switch ports

---

## System Hardening

### Raspberry Pi OS Security

#### System Updates

```bash
# Update package lists
sudo apt update

# Upgrade all packages
sudo apt upgrade -y

# Install security updates automatically
sudo apt install unattended-upgrades apt-listchanges
sudo dpkg-reconfigure -plow unattended-upgrades
```

#### Disable Unnecessary Services

```bash
# List running services
sudo systemctl list-units --type=service --state=running

# Disable unused services
sudo systemctl disable bluetooth.service
sudo systemctl disable avahi-daemon.service
sudo systemctl disable triggerhappy.service
sudo systemctl disable hciuart.service

# Stop immediately
sudo systemctl stop bluetooth.service avahi-daemon.service
```

#### SSH Hardening

Edit SSH configuration:
```bash
sudo nano /etc/ssh/sshd_config
```

**Recommended settings:**
```
# Disable root login
PermitRootLogin no

# Disable password authentication
PasswordAuthentication no
PubkeyAuthentication yes

# Disable X11 forwarding
X11Forwarding no

# Limit authentication attempts
MaxAuthTries 3

# Set timeouts
ClientAliveInterval 300
ClientAliveCountMax 2

# Limit users
AllowUsers picontrol-admin

# Use strong ciphers only
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

### Application User Isolation

```bash
# Create dedicated system user (no login shell)
sudo useradd -r -s /bin/false picontrol

# Set ownership
sudo chown -R picontrol:picontrol /opt/picontrol
sudo chown -R picontrol:picontrol /var/lib/picontrol
sudo chown -R picontrol:picontrol /var/log/picontrol
```

### File System Permissions

```bash
# Application directory (read-only for service user)
sudo chmod -R 755 /opt/picontrol
sudo chmod 750 /opt/picontrol/.venv

# Database directory (read-write for service user only)
sudo chmod 750 /var/lib/picontrol
sudo chmod 600 /var/lib/picontrol/pi_control.db

# Log directory
sudo chmod 750 /var/log/picontrol
sudo chmod 640 /var/log/picontrol/*.log

# Configuration files
sudo chmod 600 /etc/default/picontrol

# Ensure correct ownership
sudo chown -R picontrol:picontrol /var/lib/picontrol
sudo chown -R picontrol:picontrol /var/log/picontrol
sudo chown root:root /etc/default/picontrol
```

### systemd Service Hardening

Add security directives to service file:

```ini
# /etc/systemd/system/picontrol.service

[Service]
User=picontrol
Group=picontrol
WorkingDirectory=/opt/picontrol

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/picontrol /var/log/picontrol
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6
RestrictNamespaces=true
RestrictRealtime=true
RestrictSUIDSGID=true
LockPersonality=true
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM
SystemCallArchitectures=native

# Resource limits
LimitNOFILE=1024
LimitNPROC=512
```

Reload systemd and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart picontrol
```

---

## RFID Security

### RFID Card Security

#### Threat Assessment

**Vulnerabilities of EM4100/EM4102 cards:**
- Low-cost cards are easily cloneable
- No encryption or authentication
- Passive cards can be read remotely (up to ~10cm)
- No write protection

**Mitigation strategies:**
1. **Physical security** - Supervised check-in areas
2. **Anomaly detection** - Flag suspicious patterns
3. **Card + PIN** - Future enhancement for high security
4. **Upgrade cards** - Consider encrypted RFID (MIFARE DESFire)

#### Card Assignment Security

```bash
# Protect RFID write operation wrapper
sudo chown root:picontrol /usr/local/bin/picontrol-write-rfid
sudo chmod 750 /usr/local/bin/picontrol-write-rfid

# Verify sudoers entry is restrictive
# /etc/sudoers.d/picontrol:
# picontrol ALL=(ALL) NOPASSWD: /usr/local/bin/picontrol-write-rfid *
```

#### RFID Reader Physical Security

**Best practices:**
1. Mount reader in tamper-evident enclosure
2. Position in area with camera coverage
3. Use cable locks to prevent theft
4. Monitor USB device connections
5. Implement tamper detection alerts

### Anti-Spoofing Measures

**Recommended implementations:**

1. **Rate Limiting**
   - Limit check-ins to once per minute per card
   - Prevent rapid-fire spoofing attempts

2. **Anomaly Detection**
   - Flag impossible travel times (multiple locations)
   - Alert on unusual check-in patterns
   - Detect duplicate simultaneous check-ins

3. **Time-Based Rules**
   - Restrict check-ins to business hours
   - Require manual approval for off-hours access

4. **Geolocation Validation** (Future)
   - Validate check-ins from known locations
   - GPS verification for mobile check-ins

---

## Secure Configuration

### Environment Variables

#### SECRET_KEY Generation

**Critical: Never use default values in production**

```bash
# Generate cryptographically secure 32-byte key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output:
# x4yM9pL3kN7qR2vC5wZ8tA6bD1eF0gH4jK8mN2pQ5sT9

# Set in environment file
echo "SECRET_KEY=<generated-key>" | sudo tee /etc/default/picontrol
sudo chmod 600 /etc/default/picontrol
sudo chown root:root /etc/default/picontrol
```

#### Environment File Configuration

```bash
# /etc/default/picontrol

# CRITICAL: Set unique SECRET_KEY (required)
SECRET_KEY=<generate-using-secrets-module>

# Database configuration
PICONTROL_DB_DIR=/var/lib/picontrol

# Server configuration
PICONTROL_HOST=127.0.0.1  # Localhost if using reverse proxy
PICONTROL_PORT=8000

# Session configuration
SESSION_LIFETIME=3600  # 1 hour in seconds

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/picontrol/app.log

# Backup configuration
PICONTROL_BACKUP_DIR=/var/backups/picontrol
```

### Configuration Validation

```bash
# Verify SECRET_KEY is set and not default
sudo systemctl show picontrol --property=Environment | grep SECRET_KEY

# Check environment file permissions
ls -la /etc/default/picontrol
# Expected: -rw------- 1 root root

# Validate database permissions
ls -la /var/lib/picontrol/pi_control.db
# Expected: -rw------- 1 picontrol picontrol

# Test configuration
sudo systemctl restart picontrol
sudo systemctl status picontrol
```

---

## Monitoring & Logging

### Application Logging

#### Admin Audit Logs

All administrative actions are logged to `adminaction` table:

**Logged operations:**
- `create_employee` - New employee creation
- `update_employee` - Employee information changes
- `archive_employee` - Employee archival
- `restore_employee` - Employee restoration
- `assign_rfid` - RFID card assignments
- `manual_checkin` - Manual check-in entries
- `export_db` - Database exports
- `import_db` - Database imports
- `change_password` - Password changes
- `rotate_secret` - Secret key rotation

#### Viewing Audit Logs

**Web interface:**
```
Navigate to: http://<server>/admin/logs
Filter by: date range, admin user, action type
```

**Database query:**
```bash
sqlite3 /var/lib/picontrol/pi_control.db \
  "SELECT * FROM adminaction ORDER BY timestamp DESC LIMIT 20;"
```

**Export logs:**
```bash
sqlite3 /var/lib/picontrol/pi_control.db \
  "SELECT * FROM adminaction WHERE timestamp > date('now', '-7 days');" \
  > audit_logs.csv
```

### System Logging

#### systemd Journal

```bash
# Real-time log monitoring
sudo journalctl -u picontrol -f

# View logs since last boot
sudo journalctl -u picontrol -b

# View logs from last 24 hours
sudo journalctl -u picontrol --since "24 hours ago"

# Export logs to file
sudo journalctl -u picontrol --since "7 days ago" \
  > /var/log/picontrol_journal.txt
```

#### Log Rotation

Configure logrotate for application logs:

```bash
# /etc/logrotate.d/picontrol
/var/log/picontrol/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 640 picontrol picontrol
    sharedscripts
    postrotate
        systemctl reload picontrol > /dev/null 2>&1 || true
    endscript
}
```

Test configuration:
```bash
sudo logrotate -d /etc/logrotate.d/picontrol
```

### Security Monitoring

#### Failed Login Detection

**Manual review:**
```bash
# Search logs for failed login attempts
sudo journalctl -u picontrol | grep -i "invalid credentials"

# Count failed attempts by IP (if X-Forwarded-For logged)
sudo journalctl -u picontrol | grep "invalid credentials" | \
  grep -oP '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' | sort | uniq -c
```

#### Intrusion Detection (AIDE)

```bash
# Install AIDE
sudo apt install aide

# Initialize database
sudo aideinit

# Copy baseline
sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Run integrity check
sudo aide --check

# Automate checks (daily at 5 AM)
echo "0 5 * * * root /usr/bin/aide --check" | sudo tee -a /etc/crontab
```

#### Log Analysis

```bash
# Monitor for error patterns
sudo journalctl -u picontrol | grep -E "ERROR|CRITICAL|FAIL"

# Check database access
sudo lsof /var/lib/picontrol/pi_control.db

# Monitor network connections
sudo ss -tulpn | grep :8000

# Check disk usage
df -h /var/lib/picontrol
du -sh /var/lib/picontrol/*
```

---

## Incident Response

### Incident Response Plan

#### Phase 1: Detection

**Automated monitoring:**
- Service failures and crashes
- Repeated failed login attempts
- Database integrity violations
- Unusual access patterns
- Resource exhaustion (CPU, memory, disk)

**Manual review triggers:**
- User reports of suspicious activity
- Anomalous check-in patterns
- Unexpected system behavior
- External security advisories

#### Phase 2: Containment

**Immediate actions if breach suspected:**

```bash
# 1. Isolate system from network
sudo ufw deny incoming
sudo ufw status

# 2. Stop the service
sudo systemctl stop picontrol

# 3. Create forensic backup (preserve evidence)
sudo dd if=/dev/mmcblk0 of=/mnt/external/forensic-backup.img \
  bs=4M status=progress

# 4. Preserve all logs
sudo journalctl -u picontrol > /mnt/external/incident-systemd.log
sudo cp -r /var/log/picontrol /mnt/external/logs-backup/
sqlite3 /var/lib/picontrol/pi_control.db \
  ".dump" > /mnt/external/database-dump.sql

# 5. Document current state
sudo systemctl status picontrol > /mnt/external/service-status.txt
sudo lsof -p $(pgrep -f picontrol) > /mnt/external/open-files.txt
```

#### Phase 3: Eradication

```bash
# 1. Rotate all credentials
cd /opt/picontrol
sudo -u picontrol /opt/picontrol/.venv/bin/python tools/rotate_secret.py
sudo -u picontrol /opt/picontrol/.venv/bin/python tools/reset_admin.py

# 2. Update system and dependencies
sudo apt update && sudo apt full-upgrade -y
cd /opt/picontrol
source .venv/bin/activate
pip install --upgrade -r requirements.txt

# 3. Review code for tampering
git status
git diff HEAD
git log --oneline -20

# 4. Scan for malware (optional)
sudo apt install clamav
sudo freshclam
sudo clamscan -r /opt/picontrol
```

#### Phase 4: Recovery

```bash
# 1. Restore from known-good backup
sudo systemctl stop picontrol
sudo cp /var/backups/picontrol/verified-clean.db \
  /var/lib/picontrol/pi_control.db
sudo chown picontrol:picontrol /var/lib/picontrol/pi_control.db
sudo chmod 600 /var/lib/picontrol/pi_control.db

# 2. Re-enable network access
sudo ufw default allow outgoing
sudo ufw allow from 192.168.1.0/24 to any port 8000

# 3. Restart service
sudo systemctl start picontrol

# 4. Verify integrity
sudo systemctl status picontrol
curl http://localhost:8000/
sqlite3 /var/lib/picontrol/pi_control.db "PRAGMA integrity_check;"
```

#### Phase 5: Post-Incident Review

**Document the incident:**
1. Timeline of events
2. Attack vector identification
3. Root cause analysis
4. Actions taken
5. Data affected
6. Lessons learned
7. Process improvements

**Update security controls:**
- Implement additional monitoring
- Enhance detection capabilities
- Update incident response plan
- Conduct security training

---

## Security Maintenance

### Maintenance Schedule

#### Daily Tasks

- [ ] Review admin audit logs for suspicious activity
- [ ] Check service status and error logs
- [ ] Monitor disk space and resource usage
- [ ] Verify backup completion

#### Weekly Tasks

- [ ] Review failed login attempts
- [ ] Verify backup integrity (test restore)
- [ ] Update application dependencies
- [ ] Review firewall logs
- [ ] Check for system updates

#### Monthly Tasks

- [ ] Rotate admin credentials
- [ ] Audit user accounts (remove inactive)
- [ ] Review and update security policies
- [ ] Test disaster recovery procedures
- [ ] Run vulnerability scan
- [ ] Review access control lists

#### Quarterly Tasks

- [ ] Full security audit
- [ ] Penetration testing (if applicable)
- [ ] Review and update documentation
- [ ] Update incident response plan
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

*This document should be reviewed and updated regularly to reflect evolving security best practices and emerging threats.*
