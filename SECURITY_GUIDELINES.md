# Seguridad: pasos urgentes para este repositorio

Este documento enumera acciones inmediatas y comandos para mitigar la exposición de secretos
o una base de datos accidentalmente incluida en el historial.

IMPORTANTE: las operaciones que reescriben el historial (BFG, git-filter-repo) deben coordinarse
con colaboradores. Haz un backup antes de proceder.

1) Quitar archivos sensibles del árbol de trabajo (ya realizado en esta copia):

   - El archivo `pi_control.db` fue movido fuera del repo y ya no está en la rama actual.
     Se creó un backup en `/tmp/pi_control.db.bak`.

2) Añadir entradas a `.gitignore` (ya realizado):

   - `pi_control.db`, `.env`, `.env.example`, `reset_password.txt`, `secret_key.txt`, `.test_db/`

3) Opciones para purgar el historial (elige una):

   Opción rápida (BFG):

   - Instalar BFG y clonar espejo:

     git clone --mirror git@github.com:tu_usuario/PiControl.git
     java -jar bfg.jar --delete-files pi_control.db
     cd PiControl.git
     git reflog expire --expire=now --all && git gc --prune=now --aggressive
     git push --force

   Opción recomendada (git-filter-repo):

     pip install git-filter-repo
     git clone --mirror git@github.com:tu_usuario/PiControl.git
     cd PiControl.git
     git filter-repo --invert-paths --paths pi_control.db
     git push --force

   - Después de reescribir el historial, rotar todas las credenciales expuestas (passwords, API keys).

4) Rotación de secretos en la máquina objetivo

   - Rotear SECRET_KEY (si fue expuesta), API keys y cualquier contraseña presente en la BD.
   - Cambiar claves y tokens en los servicios afectados (por ejemplo, proveedores de API).

5) Crear scripts/migraciones para recrear la DB en el despliegue

   - Se añadió `scripts/init_db.py` que invoca `app.db.init_db()`.
   - Evita mantener la DB en el repo; usa migraciones o scripts de inicialización.

6) Revisión de servicios systemd y scripts

   - Revisa `install/*.service` y `tools/*.sh` para asegurar que no contienen credenciales en claro.
   - Asegúrate de usar `EnvironmentFile=/etc/default/picontrol` y proteger permisos (0600).

7) Comandos útiles para buscar patrones de credenciales localmente:

   git grep -nE "API[_-]?KEY|TOKEN|SECRET|PASSWORD|aws_secret_access_key|BEGIN RSA PRIVATE KEY" || true

8) Próximos pasos recomendados

   - Ejecutar un escaneo detallado (opción A1) para mostrar fragmentos con coincidencias y recomendaciones de cambio.
   - Si quieres, puedo ejecutar git-filter-repo en un espejo local (necesitarás acceso y coordinación para push --force).
