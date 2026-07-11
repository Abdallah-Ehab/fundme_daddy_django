# FundMeDaddy — Crowdfunding Platform

A Django-based crowdfunding platform where users register, activate their account via email, and create/manage fundraising campaigns.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Activation emails are printed to the console (console email backend). Registration creates an inactive user; click the activation link in the console output to activate.

## Apps

- **accounts** — Custom User model (email login, Egyptian phone validation), registration, activation, login/logout
- **projects** — Campaign CRUD with ownership-based authorization and date-range search

## URLs

| URL | View |
| --- | ---- |
| `/projects/` | Public project list |
| `/projects/new/` | Create project (login required) |
| `/projects/<pk>/` | Project detail |
| `/projects/<pk>/edit/` | Edit project (owner only) |
| `/projects/<pk>/delete/` | Delete project (owner only) |
| `/accounts/register/` | Register |
| `/accounts/login/` | Login |
| `/accounts/logout/` | Logout |

## Tests

```bash
python manage.py test
```

Tests cover: Egyptian phone validation, registration→activation→login flow, project date validation, and ownership authorization.
