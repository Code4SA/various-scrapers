from __future__ import with_statement
from fabdefs import *
from fabric.api import *
from contextlib import contextmanager

# hook for activating a virtualenv on the server
env.activate = 'source %s/env/bin/activate' % env.code_dir

@contextmanager
def virtualenv():
    with cd(env.code_dir):
        with prefix(env.activate):
            yield


def setup():
    sudo('apt-get install build-essential python python-dev')
    sudo('apt-get install python-pip supervisor')
    sudo('pip install virtualenv')
    sudo('apt-get install git unzip socket')
    sudo('apt-get install libxml2-dev libxslt1-dev')
    sudo('apt-get install beanstalkd mongodb-server')

    # Set beanstalk to start at bootime
    sudo("sed 's/#START=yes/START=yes/' /etc/default/beanstalkd > /tmp/beanstalkd")
    sudo("mv /tmp/beanstalkd /etc/default/beanstalkd")
    sudo("service beanstalkd start")
        
    # create application directory if it doesn't exist yet
    with settings(warn_only=True):
        if run("test -d %s" % env.code_dir).failed:
            # create project folder
            sudo("mkdir -p %s" % env.code_dir)
            sudo("chown adi:adi %s" % env.code_dir)
            run("git clone https://github.com/Code4SA/various-scrapers.git %s" % env.code_dir)

        if run("test -d %s/env" % env.code_dir).failed:
            run('virtualenv --no-site-packages %s/env' % env.code_dir)


def configure():

    # Daily cronjob for the producer
    sudo("echo 'cd %s; %s/bin/python scraper.py producer' > /etc/cron.daily/scrapers" % (env.code_dir, env.env_dir))

    supervisor_conf = open("deploy/consumers.conf").read() % { "code_dir" : env.code_dir, "env_dir" : env.env_dir }
    sudo("echo '%s' > /etc/supervisor/conf.d/consumers.conf" % supervisor_conf)

    supervisor_conf = open("deploy/twitter.conf").read() % { "code_dir" : env.code_dir, "env_dir" : env.env_dir }
    sudo("echo '%s' > /etc/supervisor/conf.d/twitter.conf" % supervisor_conf)

    sudo("supervisorctl update")


def deploy():
    with cd(env.code_dir):
        run("git pull origin develop")

    with virtualenv():
        run('pip install -r requirements.txt')

    sudo("supervisorctl restart 'scraper_consumers:*'")

