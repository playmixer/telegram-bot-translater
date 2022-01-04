import sys, os, shutil

from core import configurations

if len(sys.argv) == 1:
    exit()

command = sys.argv[1]

if command == 'createapp':
    app_name = sys.argv[2]
    if not os.path.exists(configurations.APPS_DIRECTORY):
        os.mkdir(configurations.APPS_DIRECTORY)

    path_to_app = os.path.join(configurations.APPS_DIRECTORY, app_name)
    if os.path.exists(path_to_app):
        print(f'Application {app_name} is exists')
        exit()
    else:
        os.mkdir(path_to_app)

    files = ['handlers.py']
    for f in files:
        shutil.copy(os.path.join('core', 'example', 'app', f), path_to_app)

    print(f'Application {app_name} is created')
