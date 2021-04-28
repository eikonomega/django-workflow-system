from setuptools import setup


def read(f):
    return open(f, encoding="utf-8").read()


setup(
    name="django-workflow-system",
    version="0.2",
    description="A highly customizable workflow system for Django. Create surveys, activities, etc.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Center for Research Computing",
    author_email="prometheus-team@nd.edu",
    license="MIT",
    packages=["workflows"],
    python_requires=">3.8",
    install_requires=["Pillow>=6.2.0", "jsonschema==3.0.1", "Django >= 3.1.0"],
    zip_safe=False,
)
