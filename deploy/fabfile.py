from fabric.contrib.files import append, exists, sed
from fabric.api import cd, env, local, run, settings
import random

REPO_URL = 'git@github.com:vishal-netsol/django_app.git'

def deploy():
    """ Run a command on the host. Assumes user has SSH keys setup """
    with cd('/Users/pardeepsaini/test'):
        _get_latest_source()
        _update_settings(env.host)
        _update_virtualenv()
        


# def deploy():
#     site_folder = f'/home/{env.user}/sites/{env.host}' 
#     run(f'mkdir -p {site_folder}')  
#     with cd(site_folder):  
#         _get_latest_source()
#         _update_settings(env.host)  
#         _update_virtualenv()
#         _update_static_files()
#         _update_database()


def _get_latest_source():
    if exists('.git'):  
        run("git fetch")  
    else:
        code_dir = '/Users/pardeepsaini/test/django_app'
        with settings(warn_only=True):
            if run("test -d %s" % code_dir).failed:
                run("git clone %s" % REPO_URL)
        with cd(code_dir):
            run("git stash")
            run("git pull")
            run("touch app.wsgi")
    # current_commit = local("git log -n 1 --format=%H", capture=True)  
    # run('git reset --hard %s' % current_commit)

def _update_settings(site_name):
    settings_path = '/Users/pardeepsaini/test/django_app/blog/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")  
    sed(settings_path,
        'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = [" %s " % site_name]'  
    )
    secret_key_file = '/Users/pardeepsaini/test/django_app/blog/secret_key.py'
    if not exists(secret_key_file):  
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.choice(chars) for _ in range(50))
        append(secret_key_file, 'SECRET_KEY = {}'.format(key))
    append(settings_path, '\nfrom .secret_key import SECRET_KEY')

def _update_virtualenv():
    if not exists('virtualenv/bin/pip'):
        run('sudo easy_install pip')
        run('sudo pip install virtualenv')
        # run('python -m virtualenv venv')
        run('virtualenv web3_env')
    run('source web3_env/bin/activate')
    run('pip install -r django_app/requirements.txt')

# def _update_static_files():
#     run('./virtualenv/bin/python manage.py collectstatic --noinput')

# def _update_database():
#     run('./virtualenv/bin/python manage.py migrate --noinput')