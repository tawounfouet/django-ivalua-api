# ivalua_api/settings/base.py
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Internationalization
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]