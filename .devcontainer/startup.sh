echo "Starting Python Dev Server"
cd /workspaces/django-workflow-system
python manage makemigrations
python manage migrate
python manage.py runserver
