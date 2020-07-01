from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm

env.hosts = ['dev.tdelam.com']
env.user = "trevor"
app_name = "smiths"
code_dir = '/srv/virtualenvs/smiths/smiths'


def mkvirtualenv():
    with settings(warn_only=True):
        if run("test -d %s" % code_dir).failed:
            run("mkvirtualenv %s" % app_name)

def restart_apache():
    sudo('/etc/init.d/apache2 reload')

def deploy():
    virtualenv = '/srv/virtualenv/%s' % app_name
    code_dir = '/srv/virtualenvs/%s/%s' % (app_name, app_name)

    with settings(warn_only=True):
        mkvirtualenv()
        if run("test -d %s" % code_dir).failed:
            run("git clone git@bitbucket.org:tdelam/%s.git %s" % (app_name, code_dir))

    with cd(code_dir):
        run("git pull")
        with prefix('source /srv/virtualenvs/smiths/bin/activate'):
            run('pip install -r %s/requirements.txt' % code_dir)
            run('python manage.py syncdb --noinput')
            run('python manage.py migrate')

def reload():
    sudo('service apache2 reload', pty=False)


def restart():
    sudo('service apache2 restart', pty=False)

