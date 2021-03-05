echo "Starting Python Dev Server"
cd /workspaces/django-workflow-system 
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
