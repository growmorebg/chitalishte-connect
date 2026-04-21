# Chitalishte Connect

This repository now runs as a Django site from [`/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/backend`](/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/backend). The former root-level static prototype is preserved only as archive material in [`/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/archive/static-prototype`](/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/archive/static-prototype) and is no longer the active app.

**Local Setup**
1. `cd backend`
2. `python3 -m venv .venv`
3. `source .venv/bin/activate`
4. `python -m pip install -r requirements.txt`
5. `python manage.py migrate`
6. `python manage.py seed_site_content`
7. `python manage.py createsuperuser`
8. `python manage.py runserver`

The seeded content gives the public site enough neutral data to review key routes without manual entry. You can re-run `python manage.py seed_site_content` safely; it only fills missing review content.

**Admin And Content**
Open [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) after creating a superuser. The most important first-pass content areas are:

- `core.SiteSettings` for site-wide contact details, footer copy, and cookie text
- `pages.HomePage` for the homepage hero, metrics, and editorial blocks
- `programs.Program` and related inlines for schedules, pricing, sessions, and gallery items
- `stories.Story` for news, projects, and attached resources
- `pages.Page`, `pages.HistoryEntry`, `pages.BoardMember`, `core.Location`, and `pages.GalleryImage` for the remaining public sections

**Media And Static Files**
Local uploads are stored in [`/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/backend/media`](/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/backend/media) and are served automatically only while `DJANGO_DEBUG` is true. Collected static files go to [`/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/backend/staticfiles`](/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/backend/staticfiles).

For a hosted deployment:

- set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=0`, and `DJANGO_ALLOWED_HOSTS`
- run `python manage.py migrate`
- run `python manage.py collectstatic --noinput`
- store media on persistent disk or external object storage; do not rely on ephemeral app containers for uploads

**Checks And Deployment Notes**
Run the main validation commands from [`/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/backend`](/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/backend):

- `.venv/bin/python manage.py check`
- `.venv/bin/python manage.py makemigrations --check --dry-run`
- `.venv/bin/python manage.py test`

The old GitHub Pages workflow was specific to the archived static prototype. [`/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/.github/workflows/deploy.yml`](/Users/dimitardimov/Desktop/chitalishte/chitalishte-connect/.github/workflows/deploy.yml) now runs Django CI checks instead. Actual production deployment should target a Django-capable host with persistent media storage.
