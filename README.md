# ToTrip - Tour Guide Platform

A Django-based platform for tour guides in Saudi Arabia to showcase their services, and for tourists to find and review tour guides.

## Features

### For Tour Guides
- Create and manage a profile with personal information, expertise, and languages
- Add tour packages with pricing, duration, and included services
- Upload gallery images and videos to showcase experiences
- Set work schedules and availability
- Receive reviews from tourists

### For Tourists
- Browse and search for tour guides by location, language, or specialty
- View guide profiles, tour packages, and reviews
- Book tours (coming soon)
- Submit reviews for tour guides

### For Administrators
- Verify and manage tour guide accounts
- Feature and recommend guides
- Moderate reviews
- Manage locations, badges, and other site content

## Technology Stack

- **Backend**: Django 5.2, Python 3.12
- **CMS**: Wagtail 6.4
- **Frontend**: TailwindCSS, HTML5, JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Media Storage**: Wagtail Image handling

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/Totrip2025.git
   cd Totrip2025
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv env
   source env/bin/activate  # On Windows, use: env\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Fix any field inconsistencies (if needed):
   ```
   python manage.py shell < fix_inconsistencies.py
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Visit http://127.0.0.1:8000/ in your browser to access the site and http://127.0.0.1:8000/django-admin/ for the Django admin.

## Project Structure

- `tourguides/` - Main application for managing tour guides
  - `models.py` - Database models
  - `views.py` - View functions
  - `urls.py` - URL patterns
  - `forms.py` - Form definitions
  - `admin.py` - Admin interface customization
  - `templates/` - HTML templates
  - `static/` - Static files (CSS, JS, images)

- `totrip/` - Project configuration
  - `settings/` - Django settings
  - `urls.py` - Main URL patterns

## Setting Up for Production

1. Update `settings/production.py` with appropriate settings
2. Configure static and media file storage
3. Set up a PostgreSQL database
4. Configure a web server (Nginx, Apache) with WSGI/ASGI
5. Set up HTTPS using SSL/TLS certificates

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 