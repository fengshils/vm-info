import os,sys,django

from django.core.wsgi import get_wsgi_application

# sys.path.extend([r'E:/pythonproject/django_rest_env/mysite',])
sys.path.extend([os.getcwd(),])
os.environ.setdefault("DJANGO_SETTINGS_MODULE","mysite.settings")
application = get_wsgi_application()
django.setup()


from main.models import *

print(VCenter.objects.get(id=1))