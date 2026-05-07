# Chitalishte Connect Deployment Guide

This app is a Django site located in `backend/`. It is not a static site, so it
cannot be deployed to GitHub Pages as-is. The recommended first production setup
is:

- GitHub for source control and CI
- A small Ubuntu VPS for hosting Django
- Gunicorn as the Django application server
- Nginx as the public web server
- Certbot/Let's Encrypt for HTTPS
- Persistent server disk for `db.sqlite3`, uploaded media, and backups

For a low-traffic chitalishte site, this path is simple, predictable, and works
with the app's current SQLite and local media configuration. If you later want
auto-scaling or a platform-as-a-service host, plan a separate step to move the
database to Postgres and media uploads to object storage.

## 1. Decide What You Are Buying

Buy these two things:

1. A domain name, for example `your-domain.bg` or `your-domain.com`.
2. Hosting that can run Python/Django. For this project, use a VPS, not static
   hosting.

Good domain registrar options include Cloudflare Registrar, Porkbun, Namecheap,
or your preferred Bulgarian registrar. Good VPS options include Hetzner,
DigitalOcean, Linode/Akamai, Vultr, or another Ubuntu server provider.

Minimum starting server:

- Ubuntu 24.04 LTS
- 1 CPU
- 1 GB RAM
- 20 GB+ disk
- SSH access
- Backups enabled

You can upgrade later if the site grows.

## 2. Prepare The Project For GitHub

From your local machine:

```bash
cd /Users/dimitardimov/Desktop/chitalishte/chitalishte-connect
git status
```

Do not commit local-only files:

- `backend/.venv/`
- `backend/db.sqlite3`
- `backend/media/`
- `backend/staticfiles/`
- `.DS_Store`
- any `.env` file

This repository already has a GitHub remote:

```bash
git remote -v
```

Current remote:

```text
https://github.com/growmorebg/chitalishte-connect.git
```

After confirming the runtime dependency in the next step, commit and push the
app code:

```bash
git add .gitignore README.md DEPLOYMENT.md .github archive backend
git status
git commit -m "Prepare Django deployment"
git push origin chitalishte-bulgarski
```

Then open GitHub and create a pull request from `chitalishte-bulgarski` into
`main`. The existing GitHub Actions workflow runs:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

After the pull request passes, merge it into `main`.

If you need to create a new GitHub repository instead:

```bash
gh repo create growmorebg/chitalishte-connect --private --source=. --remote=origin --push
```

Use `--public` instead of `--private` only if you are comfortable making the
source code public.

## 3. Confirm Production Runtime Dependency

The app depends on Django and Pillow. The production server also needs Gunicorn
to run Django behind Nginx.

Confirm `backend/requirements.txt` includes:

```text
gunicorn>=23.0,<24
```

Keeping Gunicorn in requirements means the server can install everything with
one command.

## 4. Create The Server

In your VPS provider dashboard:

1. Create an Ubuntu 24.04 LTS server.
2. Add your SSH public key.
3. Enable provider backups.
4. Copy the server public IPv4 address.

SSH into the server:

```bash
ssh root@SERVER_IP
```

Create a non-root deploy user:

```bash
adduser deploy
usermod -aG sudo deploy
rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

Log out, then log back in as `deploy`:

```bash
ssh deploy@SERVER_IP
```

Install server packages:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git nginx ufw
```

Enable the firewall:

```bash
sudo ufw allow OpenSSH
sudo ufw allow "Nginx Full"
sudo ufw enable
sudo ufw status
```

## 5. Point The Domain To The Server

In your domain registrar or DNS provider, create:

```text
Type  Name  Value
A     @     SERVER_IP
CNAME www   your-domain.com
```

Replace `your-domain.com` with your real domain.

Notes:

- `@` means the root/apex domain, such as `your-domain.com`.
- `www` points `www.your-domain.com` to the root domain.
- If using Cloudflare, start with DNS-only mode until HTTPS is working.
- DNS can update in minutes, but sometimes takes longer.

Check DNS from your local machine:

```bash
dig +short your-domain.com
dig +short www.your-domain.com
```

Both should resolve to your server.

## 6. Clone The App On The Server

On the server as `deploy`:

```bash
sudo mkdir -p /srv/chitalishte-connect
sudo chown deploy:deploy /srv/chitalishte-connect
git clone https://github.com/growmorebg/chitalishte-connect.git /srv/chitalishte-connect
cd /srv/chitalishte-connect
git checkout main
```

Create the Python virtual environment:

```bash
cd /srv/chitalishte-connect/backend
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If Gunicorn is not in `requirements.txt` yet:

```bash
python -m pip install gunicorn
```

## 7. Configure Production Environment Variables

Create an environment file:

```bash
sudo nano /etc/chitalishte-connect.env
```

Paste this, changing the domain and secret key:

```bash
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com,SERVER_IP
DJANGO_PUBLIC_SITE_URL=https://www.your-domain.com
DJANGO_COOKIE_CONSENT_COOKIE_SECURE=1
```

For the current production domain, use:

```bash
DJANGO_PUBLIC_SITE_URL=https://www.kirilimetodii1926.com
```

Generate a strong Django secret key:

```bash
cd /srv/chitalishte-connect/backend
. .venv/bin/activate
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Put the generated value into `/etc/chitalishte-connect.env`.

Lock down the file:

```bash
sudo chown root:root /etc/chitalishte-connect.env
sudo chmod 600 /etc/chitalishte-connect.env
```

## 8. Create The Production Database

This project currently uses SQLite at `backend/db.sqlite3`.

Option A: start with a fresh production database:

```bash
cd /srv/chitalishte-connect/backend
. .venv/bin/activate
set -a
. /etc/chitalishte-connect.env
set +a
python manage.py migrate
python manage.py seed_site_content
python manage.py createsuperuser
```

Option B: copy the current local content to production:

```bash
scp /Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/backend/db.sqlite3 deploy@SERVER_IP:/srv/chitalishte-connect/backend/db.sqlite3
rsync -av /Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/backend/media/ deploy@SERVER_IP:/srv/chitalishte-connect/backend/media/
```

Then run migrations anyway:

```bash
cd /srv/chitalishte-connect/backend
. .venv/bin/activate
set -a
. /etc/chitalishte-connect.env
set +a
python manage.py migrate
python manage.py createsuperuser
```

Do not put `db.sqlite3` or `media/` into GitHub.

## 9. Collect Static Files

On the server:

```bash
cd /srv/chitalishte-connect/backend
. .venv/bin/activate
set -a
. /etc/chitalishte-connect.env
set +a
python manage.py collectstatic --noinput
python manage.py check --deploy
```

`check --deploy` may recommend extra hardening settings. Treat those as a
pre-launch checklist.

## 10. Test Gunicorn Manually

On the server:

```bash
cd /srv/chitalishte-connect/backend
. .venv/bin/activate
set -a
. /etc/chitalishte-connect.env
set +a
gunicorn --bind 127.0.0.1:8001 chitalishte_project.wsgi:application
```

In a second SSH window:

```bash
curl -I http://127.0.0.1:8001/
```

You should see an HTTP response such as `200`, `301`, or `302`.

Stop Gunicorn in the first SSH window with `Ctrl+C`.

## 11. Create A systemd Service

Create the service file:

```bash
sudo nano /etc/systemd/system/chitalishte-connect.service
```

Paste:

```ini
[Unit]
Description=Chitalishte Connect Django app
After=network.target

[Service]
User=deploy
Group=www-data
WorkingDirectory=/srv/chitalishte-connect/backend
EnvironmentFile=/etc/chitalishte-connect.env
ExecStart=/srv/chitalishte-connect/backend/.venv/bin/gunicorn \
  --workers 3 \
  --bind unix:/run/chitalishte-connect.sock \
  chitalishte_project.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now chitalishte-connect
sudo systemctl status chitalishte-connect
```

Useful logs:

```bash
journalctl -u chitalishte-connect -f
```

## 12. Configure Nginx

Create an Nginx site:

```bash
sudo nano /etc/nginx/sites-available/chitalishte-connect
```

Paste, changing the domain:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    client_max_body_size 20M;

    location /static/ {
        alias /srv/chitalishte-connect/backend/staticfiles/;
    }

    location /media/ {
        alias /srv/chitalishte-connect/backend/media/;
    }

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://unix:/run/chitalishte-connect.sock;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/chitalishte-connect /etc/nginx/sites-enabled/chitalishte-connect
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

Visit:

```text
http://your-domain.com
```

## 13. Enable HTTPS

Install Certbot:

```bash
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/local/bin/certbot
```

Request and install a certificate:

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

Test renewal:

```bash
sudo certbot renew --dry-run
```

Then visit:

```text
https://your-domain.com
```

## 14. Configure The Django Admin And Content

Open:

```text
https://your-domain.com/admin/
```

Log in with the superuser account.

Important admin areas:

- `core.SiteSettings`
- `pages.HomePage`
- `programs.Program`
- `stories.Story`
- `pages.Page`
- `pages.HistoryEntry`
- `pages.BoardMember`
- `core.Location`
- `pages.GalleryImage`

Upload images through the admin. They will be stored in:

```text
/srv/chitalishte-connect/backend/media/
```

Back this directory up.

## 15. Deployment Updates After The First Launch

When you change the code locally:

```bash
git add .
git commit -m "Describe the change"
git push origin chitalishte-bulgarski
```

Open a pull request into `main`, wait for CI, then merge.

On the server:

```bash
cd /srv/chitalishte-connect
git pull origin main
cd backend
. .venv/bin/activate
python -m pip install -r requirements.txt
set -a
. /etc/chitalishte-connect.env
set +a
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check --deploy
sudo systemctl restart chitalishte-connect
sudo systemctl reload nginx
```

Check:

```bash
sudo systemctl status chitalishte-connect
curl -I https://your-domain.com
```

## 16. Backups

At minimum, back up:

- `/srv/chitalishte-connect/backend/db.sqlite3`
- `/srv/chitalishte-connect/backend/media/`
- `/etc/chitalishte-connect.env`
- Nginx config in `/etc/nginx/sites-available/chitalishte-connect`

Simple manual backup from your local machine:

```bash
mkdir -p ~/chitalishte-backups
scp deploy@SERVER_IP:/srv/chitalishte-connect/backend/db.sqlite3 ~/chitalishte-backups/db.sqlite3
rsync -av deploy@SERVER_IP:/srv/chitalishte-connect/backend/media/ ~/chitalishte-backups/media/
```

Also enable VPS provider snapshots/backups.

## 17. Email Notifications

The app has inquiry notification settings, but email is disabled by default:

```bash
DJANGO_INQUIRY_NOTIFICATION_ENABLED=0
```

When you are ready to send emails from contact/inquiry forms, choose an email
provider and add SMTP settings to Django. The current settings file does not yet
define SMTP host, port, username, password, or TLS settings, so this needs a
small code/config update before production email can work reliably.

## 18. Production Hardening To Add Next

Before announcing the site widely, consider adding environment-based settings
for:

- `CSRF_TRUSTED_ORIGINS`
- `SECURE_SSL_REDIRECT`
- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`
- `SECURE_PROXY_SSL_HEADER`
- production logging
- error monitoring such as Sentry

Run this after setting production environment variables:

```bash
python manage.py check --deploy
```

Use its output as the final launch checklist.

## 19. Platform Hosting Alternative

Render, Railway, Fly.io, and similar hosts can run Django, but the current app
stores its database and uploads on the local filesystem. On these platforms,
the default filesystem is often ephemeral unless you attach a persistent disk or
volume.

For those platforms, plan to change the app to support:

- `DATABASE_URL` / managed Postgres
- object storage for media uploads, such as S3-compatible storage
- WhiteNoise or CDN/static storage for static files
- a platform start command such as:

```bash
gunicorn chitalishte_project.wsgi:application
```

That is a good later upgrade. For the first launch, the VPS path above is
usually faster and less surprising.

## Reference Docs

- Django deployment checklist: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
- Django static files deployment: https://docs.djangoproject.com/en/5.2/howto/static-files/deployment/
- Gunicorn deployment notes: https://gunicorn.org/deploy/
- Certbot Nginx instructions: https://certbot.eff.org/instructions
- Cloudflare DNS records: https://developers.cloudflare.com/dns/manage-dns-records/
- GitHub CLI `gh repo create`: https://cli.github.com/manual/gh_repo_create
