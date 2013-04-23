#!/usr/bin/env python

import os

from fabric.api import *

"""
Base configuration
"""
env.deployed_name = 'soundbites'
env.repo_name = 'soundbites'

env.repo_url = 'git@github.com:jeremyjbowers/%(repo_name)s.git' % env
env.user = 'jbowers'
env.python = 'python2.7'
env.path = '/home/%(user)s/apps/%(deployed_name)s' % env
env.repo_path = env.path
env.virtualenv_path = '/home/%(user)s/.virtualenvs/%(deployed_name)s' % env
env.forward_agent = True


"""
Environments
"""
def production():
    env.settings = 'production'
    env.hosts = ['192.81.214.235']

"""
Branches
"""
def master():
    """
    Work on development branch.
    """
    env.branch = 'master'

def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name

"""
Setup
"""
def setup():
    """
    Setup servers for deployment.
    """
    require('settings', provided_by=[production])
    require('branch', provided_by=[master, branch])

    setup_directories()
    setup_virtualenv()
    clone_repo()
    checkout_latest()
    install_requirements()

def setup_directories():
    """
    Create server directories.
    """
    require('settings', provided_by=[production])

    run('mkdir -p %(path)s' % env)

def setup_virtualenv():
    """
    Setup a server virtualenv.
    """
    require('settings', provided_by=[production])

    run('virtualenv -p %(python)s --no-site-packages %(virtualenv_path)s' % env)
    run('source %(virtualenv_path)s/bin/activate' % env)

def clone_repo():
    """
    Clone the source repository.
    """
    require('settings', provided_by=[production])

    run('git clone %(repo_url)s %(repo_path)s' % env)

def checkout_latest(remote='origin'):
    """
    Checkout the latest source.
    """
    require('settings', provided_by=[production])
    require('branch', provided_by=[master, branch])

    env.remote = remote

    run('cd %(repo_path)s; git fetch %(remote)s' % env)
    run('cd %(repo_path)s; git checkout %(branch)s; git pull %(remote)s %(branch)s' % env)

def install_requirements():
    """
    Install the latest requirements.
    """
    require('settings', provided_by=[production])

    run('%(virtualenv_path)s/bin/pip install -U -r %(repo_path)s/requirements.txt' % env)

"""
Deployment
"""
def deploy(remote='origin'):
    """
    Deploy the latest app to S3 and, if configured, to our servers.
    """
    require('settings', provided_by=[production])

    checkout_latest(remote)
