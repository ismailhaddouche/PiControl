# Security Guidelines# Seguridad: pasos urgentes para este repositorio



**Comprehensive Security Guide for PiControl**Este documento enumera acciones inmediatas y comandos para mitigar la exposición de secretos

o una base de datos accidentalmente incluida en el historial.

This document provides detailed security guidelines, best practices, and hardening procedures for deploying and maintaining PiControl in production environments.

IMPORTANTE: las operaciones que reescriben el historial (BFG, git-filter-repo) deben coordinarse

---con colaboradores. Haz un backup antes de proceder.



## Table of Contents1) Quitar archivos sensibles del árbol de trabajo (ya realizado en esta copia):



- [Overview](#overview)   - El archivo `pi_control.db` fue movido fuera del repo y ya no está en la rama actual.

- [Threat Model](#threat-model)     Se creó un backup en `/tmp/pi_control.db.bak`.

- [Security Architecture](#security-architecture)

- [Pre-Deployment Security Checklist](#pre-deployment-security-checklist)2) Añadir entradas a `.gitignore` (ya realizado):

- [Authentication & Authorization](#authentication--authorization)

- [Data Protection](#data-protection)   - `pi_control.db`, `.env`, `.env.example`, `reset_password.txt`, `secret_key.txt`, `.test_db/`

- [Network Security](#network-security)

- [System Hardening](#system-hardening)3) Opciones para purgar el historial (elige una):

- [RFID Security](#rfid-security)

- [Secure Configuration](#secure-configuration)   Opción rápida (BFG):

- [Monitoring & Logging](#monitoring--logging)

- [Incident Response](#incident-response)   - Instalar BFG y clonar espejo:

- [Security Maintenance](#security-maintenance)

- [Compliance Considerations](#compliance-considerations)     git clone --mirror git@github.com:tu_usuario/PiControl.git

- [Security Auditing](#security-auditing)     java -jar bfg.jar --delete-files pi_control.db

     cd PiControl.git

---     git reflog expire --expire=now --all && git gc --prune=now --aggressive

     git push --force

## Overview

   Opción recomendada (git-filter-repo):

PiControl is designed with security in mind, but proper deployment and configuration are critical to maintaining a secure system. This guide covers security considerations specific to time tracking systems and Raspberry Pi deployments.

     pip install git-filter-repo

### Security Principles     git clone --mirror git@github.com:tu_usuario/PiControl.git

     cd PiControl.git

1. **Defense in Depth**: Multiple layers of security controls     git filter-repo --invert-paths --paths pi_control.db

2. **Least Privilege**: Minimal permissions for users and processes     git push --force

3. **Secure by Default**: Safe configuration out of the box

4. **Fail Secure**: Graceful degradation without compromising security   - Después de reescribir el historial, rotar todas las credenciales expuestas (passwords, API keys).

5. **Audit Everything**: Comprehensive logging of security-relevant events

4) Rotación de secretos en la máquina objetivo

---

      - Rotear SECRET_KEY (si fue expuesta), API keys y cualquier contraseña presente en la BD.

## Threat Model      - Nota: los scripts `tools/reset_admin.py` y `tools/rotate_secret.py` han sido modificados para

         evitar escribir secretos en disco por defecto. `reset_admin.py` ahora imprime la contraseña en

### Assets to Protect         stdout (one-time) y `rotate_secret.py` imprime la nueva SECRET_KEY y solo crea copia con

         `--backup`.

1. **Employee Personal Data**: Names, document IDs, work hours   - Cambiar claves y tokens en los servicios afectados (por ejemplo, proveedores de API).

2. **Authentication Credentials**: Admin passwords, session tokens

3. **System Configuration**: Secret keys, database, service accounts5) Crear scripts/migraciones para recrear la DB en el despliegue

4. **Business Intelligence**: Work patterns, attendance records

   - Se añadió `scripts/init_db.py` que invoca `app.db.init_db()`.

### Threat Actors   - Evita mantener la DB en el repo; usa migraciones o scripts de inicialización.



1. **External Attackers**: Internet-based exploitation attempts6) Revisión de servicios systemd y scripts

2. **Malicious Insiders**: Employees with physical/network access

3. **Curious Employees**: Unauthorized access attempts by staff   - Revisa `install/*.service` y `tools/*.sh` para asegurar que no contienen credenciales en claro.

4. **Physical Threats**: Device theft, RFID cloning   - Asegúrate de usar `EnvironmentFile=/etc/default/picontrol` y proteger permisos (0600).



### Attack Vectors7) Comandos útiles para buscar patrones de credenciales localmente:



1. **Network Attacks**: SQL injection, XSS, session hijacking   git grep -nE "API[_-]?KEY|TOKEN|SECRET|PASSWORD|aws_secret_access_key|BEGIN RSA PRIVATE KEY" || true

2. **Physical Access**: Device tampering, RFID card cloning

3. **Social Engineering**: Credential theft, phishing8) Próximos pasos recomendados

4. **Privilege Escalation**: Unauthorized admin access

5. **Data Exfiltration**: Database theft, backup compromise   - Ejecutar un escaneo detallado (opción A1) para mostrar fragmentos con coincidencias y recomendaciones de cambio.

   - Si quieres, puedo ejecutar git-filter-repo en un espejo local (necesitarás acceso y coordinación para push --force).

---

## Security Architecture

### Security Layers

```
┌─────────────────────────────────────────┐
│  Physical Security (Pi + RFID Reader)   │
├─────────────────────────────────────────┤
│  Network Security (Firewall + TLS)      │
├─────────────────────────────────────────┤
│  Application Security (Auth + Validation)│
├─────────────────────────────────────────┤
│  Data Security (Encryption + Backups)   │
└─────────────────────────────────────────┘
```

### Security Components

| Component | Security Feature | Protection Against |
|-----------|------------------|-------------------|
| Session Management | Cryptographic signing | Session hijacking, tampering |
| Password Storage | bcrypt hashing | Credential theft, rainbow tables |
| Input Validation | Pydantic models | SQL injection, XSS, data corruption |
| HTTPS/TLS | SSL certificates | Man-in-the-middle, eavesdropping |
| Audit Logging | Admin action logs | Unauthorized changes, forensics |
| Machine-ID Validation | Hardware binding | Remote admin reset attacks |

---

## Pre-Deployment Security Checklist

### Critical Security Tasks

- [ ] **Generate strong SECRET_KEY** (32+ random bytes)
- [ ] **Change default admin password** immediately
- [ ] **Enable HTTPS** with valid SSL certificate
- [ ] **Configure firewall** to restrict port access
- [ ] **Set file permissions** on database and config files
- [ ] **Create dedicated system user** for the service
- [ ] **Disable SSH password authentication** (use keys only)
- [ ] **Update Raspberry Pi OS** to latest stable version
- [ ] **Configure automatic security updates**
- [ ] **Set up encrypted backups** with secure storage

### Recommended Security Enhancements

- [ ] Implement rate limiting for login attempts
- [ ] Add CSRF protection for state-changing operations
- [ ] Configure session timeout (default: 3600 seconds)
- [ ] Set up intrusion detection (fail2ban)
- [ ] Enable AppArmor/SELinux profiles
- [ ] Restrict physical access to Raspberry Pi
- [ ] Use separate VLANs for management traffic
- [ ] Implement database encryption at rest
- [ ] Set up log aggregation and monitoring
- [ ] Create disaster recovery plan

---

## Authentication & Authorization

### Password Security

#### Strong Password Policy

Enforce strong passwords for admin accounts:

```bash
# Minimum requirements:
# - At least 12 characters
# - Mix of uppercase, lowercase, numbers, symbols
# - No common words or patterns
# - Unique (not reused from other services)

# Generate strong password:
python3 -c "import secrets, string; chars = string.ascii_letters + string.digits + string.punctuation; print(''.join(secrets.choice(chars) for _ in range(20)))"
```

#### Password Storage

- **Algorithm**: bcrypt with salt (via Passlib)
- **Work Factor**: Default (can be increased for higher security)
- **No plaintext**: Passwords never stored or logged in plain text

#### Password Reset Procedure

```bash
# Admin password reset (requires physical access to Pi)
sudo python tools/reset_admin.py

# Password is output to stdout only (not saved to file by default)
# Change immediately after first login
```

### Session Management

#### Session Security Configuration

```python
# In app/main.py
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY"),  # Must be set
    session_cookie="picontrol_session",
    max_age=3600,  # 1 hour
    same_site="lax",
    https_only=True  # Enable in production with HTTPS
)
```

#### Session Best Practices

1. **Secure Cookie Flags**:
   - `HttpOnly`: Prevents JavaScript access
   - `Secure`: Requires HTTPS (enable in production)
   - `SameSite=Lax`: Prevents CSRF attacks

2. **Session Timeout**:
   - Default: 1 hour (3600 seconds)
   - Configurable via `SESSION_LIFETIME` environment variable
   - Implement absolute timeout + idle timeout

3. **Session Invalidation**:
   - Logout clears session completely
   - SECRET_KEY rotation invalidates all sessions
   - No session persistence across restarts (by design)

### Multi-Factor Authentication (Future)

Consider implementing 2FA for admin accounts:
- TOTP (Time-based One-Time Password)
- Hardware tokens (YubiKey)
- Email/SMS verification codes

---

## Data Protection

### Database Security

#### File Permissions

```bash
# Set restrictive permissions on database
sudo chown picontrol:picontrol /var/lib/picontrol/pi_control.db
sudo chmod 600 /var/lib/picontrol/pi_control.db

# Protect directory
sudo chmod 750 /var/lib/picontrol
```

#### Encryption at Rest

For sensitive deployments, encrypt the database:

```bash
# Option 1: Full disk encryption (recommended)
# Enable during Raspberry Pi OS installation (LUKS)

# Option 2: SQLCipher for database encryption
# Requires replacing SQLite with SQLCipher build
pip install sqlcipher3
```

#### SQL Injection Prevention

- **ORM Usage**: All queries via SQLModel ORM (parameterized)
- **No Raw SQL**: Avoid `session.execute()` with string concatenation
- **Input Validation**: Pydantic models validate all inputs

```python
# Safe (parameterized via ORM)
employee = session.get(Employee, employee_id)

# NEVER do this (vulnerable to SQL injection):
# session.execute(f"SELECT * FROM employee WHERE id = '{employee_id}'")
```

### Data Minimization

Only collect and store necessary data:
- Employee document ID and name (required)
- RFID UID (for access control)
- Check-in/out timestamps (for reporting)
- Admin usernames (for audit trails)

**Do NOT store**:
- Social Security Numbers
- Personal addresses
- Phone numbers (unless explicitly needed)
- Biometric data beyond RFID

### Data Retention

```bash
# Configure automatic cleanup (default: 4 years retention)
# Edit cleanup script or add cron job:
0 2 * * 0 /opt/picontrol/.venv/bin/python /opt/picontrol/tools/cleanup_old_records.py

# Manual cleanup with dry-run
python tools/cleanup_old_records.py --dry-run

# Execute cleanup
python tools/cleanup_old_records.py
```

### Backup Security

#### Encrypted Backups

```bash
# Create encrypted backup with GPG
gpg --symmetric --cipher-algo AES256 /var/lib/picontrol/pi_control.db

# Restore from encrypted backup
gpg --decrypt pi_control.db.gpg > /var/lib/picontrol/pi_control.db
```

#### Backup Access Control

```bash
# Store backups with restrictive permissions
sudo chmod 600 /var/backups/picontrol/*.db
sudo chown root:root /var/backups/picontrol/*.db

# Use separate backup user (principle of least privilege)
```

#### Off-site Backup Storage

- Store backups on separate device/network
- Use encrypted cloud storage (e.g., encrypted S3 bucket)
- Implement backup rotation (3-2-1 rule)
- Test restore procedures regularly

---

## Network Security

### Firewall Configuration

#### UFW (Uncomplicated Firewall)

```bash
# Enable firewall
sudo ufw enable

# Default deny incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (restrict to specific IP if possible)
sudo ufw allow from 192.168.1.0/24 to any port 22

# Allow application port (only if not using reverse proxy)
sudo ufw allow from 192.168.1.0/24 to any port 8000

# Check status
sudo ufw status verbose
```

#### iptables (Advanced)

```bash
# Drop all incoming except established connections
sudo iptables -P INPUT DROP
sudo iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH from trusted network only
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 22 -j ACCEPT

# Allow application access from local network
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 8000 -j ACCEPT

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

### HTTPS/TLS Configuration

#### Reverse Proxy with nginx

```nginx
# /etc/nginx/sites-available/picontrol

server {
    listen 80;
    server_name picontrol.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name picontrol.example.com;

    # SSL certificates (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/picontrol.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/picontrol.example.com/privkey.pem;

    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Let's Encrypt SSL Certificate

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d picontrol.example.com

# Auto-renewal (certbot creates cron job automatically)
sudo certbot renew --dry-run
```

### Network Isolation

- **VLAN Segmentation**: Isolate PiControl on management VLAN
- **No Internet Exposure**: Keep on local network only
- **VPN Access**: Use VPN for remote administration
- **MAC Filtering**: Restrict network access by MAC address

---

## System Hardening

### Raspberry Pi OS Security

#### System Updates

```bash
# Update system regularly
sudo apt update
sudo apt upgrade -y

# Enable automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

#### Disable Unnecessary Services

```bash
# List running services
sudo systemctl list-units --type=service --state=running

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
sudo systemctl disable triggerhappy
```

#### SSH Hardening

```bash
# Edit SSH config
sudo nano /etc/ssh/sshd_config

# Recommended settings:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
X11Forwarding no
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2

# Restart SSH
sudo systemctl restart sshd
```

### Application User Isolation

```bash
# Create dedicated system user (no login shell)
sudo useradd -r -s /bin/false picontrol

# Assign ownership
sudo chown -R picontrol:picontrol /opt/picontrol
sudo chown -R picontrol:picontrol /var/lib/picontrol
sudo chown -R picontrol:picontrol /var/log/picontrol
```

### File System Permissions

```bash
# Application directory (read-only for service user)
sudo chmod -R 755 /opt/picontrol
sudo chmod 750 /opt/picontrol/.venv

# Data directory (read-write only for service user)
sudo chmod 750 /var/lib/picontrol
sudo chmod 600 /var/lib/picontrol/pi_control.db

# Log directory
sudo chmod 750 /var/log/picontrol
sudo chmod 640 /var/log/picontrol/*.log

# Configuration files
sudo chmod 600 /etc/default/picontrol
```

### systemd Service Hardening

```ini
# /etc/systemd/system/picontrol.service

[Service]
# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/picontrol /var/log/picontrol
ProtectKernelTunables=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictNamespaces=true
SystemCallFilter=@system-service
SystemCallErrorNumber=EPERM
```

---

## RFID Security

### RFID Card Security

#### Cloning Prevention

While EM4100/EM4102 cards are clonable:
- Use physical security (supervised areas)
- Implement card + PIN authentication (future enhancement)
- Consider upgrading to encrypted RFID cards (e.g., MIFARE DESFire)
- Monitor for suspicious activity patterns

#### Card Assignment Security

```bash
# Protect RFID write operation (RC522)
# Ensure wrapper script has restricted permissions
sudo chmod 750 /usr/local/bin/picontrol-write-rfid
sudo chown root:picontrol /usr/local/bin/picontrol-write-rfid

# Sudoers entry (limited scope)
# picontrol ALL=(ALL) NOPASSWD: /usr/local/bin/picontrol-write-rfid *
```

#### RFID Reader Physical Security

- Mount reader in tamper-evident enclosure
- Position in supervised area with camera coverage
- Use cable locks to prevent theft
- Monitor USB device connections

### Anti-Spoofing Measures

1. **Rate Limiting**: Prevent rapid check-in attempts
2. **Anomaly Detection**: Flag unusual patterns (multiple locations)
3. **Time-Based Rules**: Restrict check-ins to business hours
4. **Geolocation**: Validate check-ins from known locations (future)

---

## Secure Configuration

### Environment Variables

#### SECRET_KEY Generation

```bash
# Generate cryptographically secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in environment file
echo "SECRET_KEY=<generated-key>" | sudo tee -a /etc/default/picontrol
sudo chmod 600 /etc/default/picontrol
```

#### Environment File Template

```bash
# /etc/default/picontrol

# CRITICAL: Generate unique SECRET_KEY
SECRET_KEY=<generate-with-secrets-module>

# Database configuration
PICONTROL_DB_DIR=/var/lib/picontrol

# Server configuration
PICONTROL_HOST=127.0.0.1  # Bind to localhost if using reverse proxy
PICONTROL_PORT=8000

# Session configuration
SESSION_LIFETIME=3600

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

# Check file permissions
sudo ls -la /etc/default/picontrol
# Should be: -rw------- 1 root root

# Validate database permissions
sudo ls -la /var/lib/picontrol/pi_control.db
# Should be: -rw------- 1 picontrol picontrol
```

---

## Monitoring & Logging

### Application Logging

#### Admin Audit Logs

All administrative actions are logged to the `adminaction` table:

```python
# Logged actions include:
- create_employee
- update_employee
- archive_employee
- restore_employee
- assign_rfid
- manual_checkin
- export_db
- import_db
- change_password
- rotate_secret
```

#### Viewing Audit Logs

```bash
# Via web interface
# Navigate to: http://<server>/admin/logs

# Via database query
sqlite3 /var/lib/picontrol/pi_control.db "SELECT * FROM adminaction ORDER BY timestamp DESC LIMIT 20;"
```

### System Logging

#### systemd Journal

```bash
# View service logs
sudo journalctl -u picontrol -f

# View logs since last boot
sudo journalctl -u picontrol -b

# Export logs to file
sudo journalctl -u picontrol --since "7 days ago" > picontrol_logs.txt
```

#### Log Rotation

```bash
# Configure logrotate for application logs
sudo nano /etc/logrotate.d/picontrol

# Add configuration:
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

### Security Monitoring

#### Failed Login Attempts

Monitor for brute force attacks:

```bash
# Check for repeated failed logins (implement in application)
# Future enhancement: Add failed login tracking to database

# Use fail2ban for SSH protection
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

#### Intrusion Detection

```bash
# Install and configure AIDE (Advanced Intrusion Detection Environment)
sudo apt install aide
sudo aideinit
sudo cp /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# Run integrity check
sudo aide --check

# Schedule regular checks
echo "0 5 * * * root /usr/bin/aide --check" | sudo tee -a /etc/crontab
```

#### Log Analysis

```bash
# Monitor for suspicious patterns
sudo journalctl -u picontrol | grep -i "error\|fail\|unauthorized"

# Check database access patterns
sudo lsof /var/lib/picontrol/pi_control.db

# Monitor network connections
sudo ss -tulpn | grep :8000
```

---

## Incident Response

### Incident Response Plan

#### Detection

1. **Automated Alerts**: Configure monitoring for:
   - Service failures
   - Repeated failed login attempts
   - Database integrity violations
   - Unusual access patterns

2. **Manual Review**: Regular review of:
   - Admin audit logs
   - System logs
   - Network traffic patterns
   - Database changes

#### Containment

```bash
# Immediate actions if breach suspected:

# 1. Isolate system
sudo ufw deny incoming
sudo systemctl stop picontrol

# 2. Create forensic backup
sudo dd if=/dev/mmcblk0 of=/mnt/external/pi-backup.img bs=4M status=progress

# 3. Preserve logs
sudo journalctl -u picontrol > /mnt/external/incident-logs.txt
sudo cp -r /var/log/picontrol /mnt/external/
```

#### Eradication

```bash
# 1. Rotate all credentials
python tools/rotate_secret.py
python tools/reset_admin.py

# 2. Update system and dependencies
sudo apt update && sudo apt upgrade -y
pip install --upgrade -r requirements.txt

# 3. Review and remove any malicious code
git diff HEAD~10..HEAD  # Review recent changes
```

#### Recovery

```bash
# 1. Restore from known-good backup
sudo systemctl stop picontrol
sudo cp /var/backups/picontrol/backup_clean.db /var/lib/picontrol/pi_control.db

# 2. Restart service
sudo systemctl start picontrol

# 3. Verify integrity
sudo systemctl status picontrol
curl http://localhost:8000/
```

#### Lessons Learned

Document and review:
- Timeline of incident
- Root cause analysis
- Actions taken
- Process improvements
- Updated security controls

---

## Security Maintenance

### Regular Security Tasks

#### Daily
- [ ] Review admin audit logs
- [ ] Check service status and logs
- [ ] Monitor disk space and resource usage

#### Weekly
- [ ] Review failed login attempts
- [ ] Check backup integrity
- [ ] Update application dependencies
- [ ] Review firewall rules and network access

#### Monthly
- [ ] Rotate credentials (admin password, SECRET_KEY)
- [ ] Audit user accounts (remove inactive)
- [ ] Review and update security policies
- [ ] Test disaster recovery procedures
- [ ] Run security vulnerability scan

#### Quarterly
- [ ] Full security audit
- [ ] Penetration testing (if applicable)
- [ ] Review access control lists
- [ ] Update incident response plan
- [ ] Security awareness training

### Credential Rotation

#### SECRET_KEY Rotation

```bash
# Generate new SECRET_KEY
python tools/rotate_secret.py

# Update environment file
sudo nano /etc/default/picontrol
# Replace SECRET_KEY value

# Restart service (invalidates all sessions)
sudo systemctl restart picontrol
```

#### Admin Password Rotation

```bash
# Via web interface: /admin/configuration
# Or via CLI:
python tools/reset_admin.py

# Change immediately after login
```

### Vulnerability Management

#### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update dependencies
pip install --upgrade -r requirements.txt

# Test after updates
PYTHONPATH=. PICONTROL_DB_DIR=./test_db pytest -v
```

#### Security Scanning

```bash
# Scan for known vulnerabilities in dependencies
pip install safety
safety check

# Scan for common misconfigurations
pip install bandit
bandit -r app/
```

---

## Compliance Considerations

### GDPR Compliance

For deployments in EU/EEA:

1. **Data Minimization**: Only collect necessary data
2. **Right to Erasure**: Implement employee data deletion (archive function)
3. **Data Portability**: Support data export (DB export feature)
4. **Consent**: Document employee consent for data collection
5. **Data Protection**: Implement encryption and access controls
6. **Breach Notification**: 72-hour breach notification requirement

### Data Retention Policies

```python
# Configure retention in cleanup script
# Default: 4 years + 1 day
# Adjust based on legal requirements:

# In tools/cleanup_old_records.py:
RETENTION_YEARS = 4  # Modify as needed
```

### Access Control Documentation

Maintain records of:
- Who has admin access
- When access was granted/revoked
- Purpose of access
- Regular access reviews

---

## Security Auditing

### Self-Assessment Checklist

#### Authentication
- [ ] Strong passwords enforced
- [ ] Default credentials changed
- [ ] Session timeout configured
- [ ] Secure session management
- [ ] Failed login tracking

#### Authorization
- [ ] Admin-only operations protected
- [ ] Least privilege principle applied
- [ ] Regular access reviews

#### Data Protection
- [ ] Database encrypted at rest
- [ ] Backups encrypted
- [ ] Sensitive data not logged
- [ ] Data retention policy enforced

#### Network Security
- [ ] HTTPS enabled with valid certificate
- [ ] Firewall configured and active
- [ ] No unnecessary ports exposed
- [ ] Network segmentation implemented

#### System Security
- [ ] OS and packages updated
- [ ] Unnecessary services disabled
- [ ] File permissions restrictive
- [ ] Service running as non-root user

#### Monitoring
- [ ] Audit logging enabled
- [ ] Log retention configured
- [ ] Security events monitored
- [ ] Incident response plan documented

### External Security Assessment

Consider professional security audit:
- Penetration testing
- Code review
- Configuration audit
- Compliance assessment

### Security Reporting

Report security issues responsibly:
- **Email**: [Repository maintainer - see GitHub profile]
- **Do NOT**: Open public GitHub issues for security vulnerabilities
- **Provide**: Detailed description, steps to reproduce, impact assessment
- **Response Time**: Expect acknowledgment within 48 hours

---

## Additional Resources

### Security Tools

- **Vulnerability Scanning**: OWASP ZAP, Nikto
- **Dependency Checking**: Safety, Snyk
- **Code Analysis**: Bandit, Pylint
- **Penetration Testing**: Metasploit, Burp Suite

### References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks for Debian](https://www.cisecurity.org/cis-benchmarks/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [GDPR Official Text](https://gdpr-info.eu/)

### Community

- **GitHub Issues**: Bug reports and feature requests
- **Security Advisories**: Watch repository for security updates
- **Discussions**: Community security discussions

---

**Last Updated**: November 2025  
**Version**: 1.0  
**Maintained By**: PiControl Security Team

*This document should be reviewed and updated regularly to reflect current security best practices and emerging threats.*
