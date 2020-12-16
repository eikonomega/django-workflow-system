================
Django Workflows
================

Workflows is a Django app to conduct Web-based surveys/activities.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "workflows" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'workflows',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('workflows/', include('workflows.urls')),

3. Run ``python manage.py migrate`` to create the workflows models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a workflow (you'll need the Admin app enabled).
