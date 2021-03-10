from setuptools import setup

setup(
    name="django-workflow-system",
    version="0.1",
    description="A Django app to conduct surveys/activities.",
    author="Center for Research Computing",
    author_email="prometheus-team@nd.edu",
    license="MIT",
    packages=["workflows"],
    python_requires='>3.8'
    install_requires=["Pillow==6.2.0", "jsonschema==3.0.1", "Django >= 3.1.0"],
    zip_safe=False,
)
