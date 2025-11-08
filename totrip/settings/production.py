from .base import *
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DEBUG = False

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")

ALLOWED_HOSTS = [host.strip() for host in os.environ.get('ALLOWED_HOSTS', '').split(',') if host.strip()]

render_url = os.environ.get('RENDER_EXTERNAL_URL')
if render_url:
    from urllib.parse import urlparse
    parsed = urlparse(render_url)
    hostname = parsed.hostname
    if hostname and hostname not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(hostname)

if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS must be set when DEBUG is False")

if 'DATABASE_URL' in os.environ:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.environ['DATABASE_URL'])
    }

WAGTAILADMIN_BASE_URL = os.environ.get('WAGTAILADMIN_BASE_URL', 'https://your-app.onrender.com')

base_url = os.environ.get('RENDER_EXTERNAL_URL')
if base_url:
    CSRF_TRUSTED_ORIGINS = [base_url]

try:
    from .local import *
except ImportError:
    pass
