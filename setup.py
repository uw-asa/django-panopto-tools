from setuptools import find_packages, setup

setup(
    name="django-panopto-tools",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'AuthZ-Group',
        'Django',
        'django-ical',
        'Django-UserService',
        'Pillow',
        'UW-Panopto-Client',
        'UW-RestClients-R25'
    ]
)
