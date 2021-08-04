from setuptools import setup, find_packages


def read(f):
    return open(f, encoding="utf-8").read()


setup(
    name="django-workflow-system",
    version="0.9.5",
    description="A highly customizable workflow system for Django. Create surveys, activities, etc.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Center for Research Computing",
    author_email="prometheus-team@nd.edu",
    license="MIT",
    packages=find_packages(
        include=["django_workflow_system", "django_workflow_system.*"]
    ),
    include_package_data=True,
    python_requires=">3.8",
    install_requires=[
        "Pillow>=6.2.0",
        "jsonschema>=3.0.1",
        "Django >= 3.1.0",
        "djangorestframework>=3.12.2",
        "factory_boy>=3.2.0",
    ],
    zip_safe=False,
)
