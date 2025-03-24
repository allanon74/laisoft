"""
WSGI config for laisoft project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
import site


from django.core.wsgi import get_wsgi_application

site.addsitedir('/home/django/ambienti/laisoft/lib/python3.10/site-packages')

sys.path.append('/home/django/progetti/laisoft')
sys.path.append('/home/django/progetti/laisoft/laisoft')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laisoft.settings')

activate_env=os.path.expanduser('/home/django/ambienti/laisoft/bin/activate_this.py')
exec(open(activate_env).read(), {'__file__': activate_env})

application = get_wsgi_application()
