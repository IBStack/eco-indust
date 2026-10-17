# EcoIndustrial – version Django

Conversion du site PHP/MySQL (Garoua – déchets plastiques) en projet Django 5.

## Installation

```bash
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations core
python manage.py migrate
python manage.py seed_demo      # données de démo + compte admin
python manage.py runserver
```

Site : http://127.0.0.1:8000/ — Administration : http://127.0.0.1:8000/admin/
Admin de démo : `admin@ecoindustrial.local` / `password` (**à changer**).

## Correspondance PHP → Django

| PHP | Django |
|---|---|
| `inc/init.php` (session, CSRF, `need()`) | middleware Django, `@login_required`, `{% csrf_token %}` |
| tables `users`, `campagnes`… (`database.sql`) | `core/models.py` |
| `index.php`, `campagnes.php`, … | `core/views.py` + `templates/core/*.html` |
| `inc/header.php` / `footer.php` | `templates/base.html` |
| `admin/*.php` (CRUD, modération, suivi, paramètres) | Django admin (`core/admin.py`) |
| `assets/style.css` | `static/css/style.css` |
| `BASE` / `config.php` | `config/settings.py` |

Notes :
- Le rôle `admin` devient `is_staff`, le champ `actif` devient `is_active`.
- Hero optionnel : placez `static/img/hero.jpg`.
- Base SQLite par défaut ; instructions MySQL en commentaire dans `settings.py`.
- Les anciens mots de passe PHP (bcrypt) ne sont pas importés ; recréez les comptes.
- En production : `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, puis `collectstatic`.
