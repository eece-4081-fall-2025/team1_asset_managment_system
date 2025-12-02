# BASH Spatial
## Project Overview

The Asset Management System is a web-based Django application designed to help organizations track, manage, and organize both physical and digital assets.
Users can create assets, categorize them, assign custom attributes, edit and delete entries, filter/search through asset lists, and manage assets securely through account authentication.

This project was created for EECE 4081 and includes full backend logic, frontend templates, and an extensive automated test suite.

## Installation Steps
### 1. Install dependencies
```
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
### 2. Apply database migrations
```
python bash_spatial/manage.py migrate
```
### 3. Create admin user
Run
```
python bash_spatial/manage.py createsuperuser
```
and follow on-screen instructions
### 3. Run the development server
```
python bash_spatial/manage.py runserver
```
## Project Structure: 
```
team1_asset_management_system/
│
├── bash_spatial/
│   ├── manage.py
│   ├── asset_managment/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── templates/
│   │   ├── static/
│   │   ├── forms.py
│   │   └── tests.py
│   │
│   ├── project_settings/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py / asgi.py
│
├── requirements.txt
├── README.md
└── .github/workflows/
```
## Technologies Used: 
* Python 3.8
* Django Framework
* SQLite (default database)
* HTML, CSS, JavaScript
* GitHub Actions for automated test running

## Running Tests: 
This project includes unit and integration tests covering:
* Authentication
* Asset CRUD operations
* Attribute CRUD operations
* Search & filtering
* URL routing & resolution
* Error handling (404)
* Template rendering
* Model behavior
Run the complete test suite with:
python bash_spatial/manage.py test
