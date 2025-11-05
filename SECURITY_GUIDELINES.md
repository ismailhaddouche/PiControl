# Security: Urgent Steps for This Repository

This document lists immediate actions and commands to mitigate exposure of secrets
or a database accidentally included in the history.

IMPORTANT: Operations that rewrite history (BFG, git-filter-repo) must be coordinated
with collaborators. Make a backup before proceeding.

1) Remove sensitive files from working tree (already done in this copy):

   - The `pi_control.db` file was moved outside the repo and is no longer in the current branch.
     A backup was created at `/tmp/pi_control.db.bak`.

2) Add entries to `.gitignore` (already done):

   - `pi_control.db`, `.env`, `.env.example`, `reset_password.txt`, `secret_key.txt`, `.test_db/`

3) Options to purge history (choose one):

   Quick option (BFG):

   - Install BFG and clone mirror:

     git clone --mirror git@github.com:your_user/PiControl.git
     java -jar bfg.jar --delete-files pi_control.db
     cd PiControl.git
     git reflog expire --expire=now --all && git gc --prune=now --aggressive
     git push --force

   Recommended option (git-filter-repo):

     pip install git-filter-repo
     git clone --mirror git@github.com:your_user/PiControl.git
     cd PiControl.git
     git filter-repo --invert-paths --paths pi_control.db
     git push --force

   - After rewriting history, rotate all exposed credentials (passwords, API keys).

4) Secret rotation on target machine

      - Rotate SECRET_KEY (if exposed), API keys and any passwords present in the DB.
      - Note: The `tools/reset_admin.py` and `tools/rotate_secret.py` scripts have been modified to
         avoid writing secrets to disk by default. `reset_admin.py` now prints the password to
         stdout (one-time) and `rotate_secret.py` prints the new SECRET_KEY and only creates a backup with
         `--backup`.
   - Change keys and tokens in affected services (e.g., API providers).

5) Create scripts/migrations to recreate the DB in deployment

   - Added `scripts/init_db.py` which invokes `app.db.init_db()`.
   - Avoid keeping the DB in the repo; use migrations or initialization scripts.

6) Review systemd services and scripts

   - Review `install/*.service` and `tools/*.sh` to ensure they don't contain credentials in plain text.
   - Make sure to use `EnvironmentFile=/etc/default/picontrol` and protect permissions (0600).

7) Useful commands to search for credential patterns locally:

   git grep -nE "API[_-]?KEY|TOKEN|SECRET|PASSWORD|aws_secret_access_key|BEGIN RSA PRIVATE KEY" || true

8) Recommended next steps

   - Run a detailed scan (option A1) to show fragments with matches and change recommendations.
   - If desired, I can run git-filter-repo in a local mirror (you'll need access and coordination for push --force).
