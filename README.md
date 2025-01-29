Django Blog Application

This is a Django-based Blog Application that allows users to create, manage, and interact with blog posts.

Features

User authentication (Sign up, Login, Logout)

Create, Read, Update, and Delete (CRUD) blog posts

Commenting system

Category-based blog filtering

User profile management

Pagination for blog posts

Search functionality

Getting Started

Prerequisites

Ensure you have the following installed:

Python (>= 3.8)

Django (>= 4.0)

PostgreSQL or SQLite (default)

Installation

1.Clone the repository:
git clone https://github.com/your-username/django-blog.git
cd django-blog
2.Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
3.Install dependencies:
pip install -r requirements.txt
4.Apply database migrations:
python manage.py migrate
5.Create a superuser:
python manage.py createsuperuser
6.Run the development server:
python manage.py runserver

Open http://127.0.0.1:8000 to access the application.
