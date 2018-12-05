#!/usr/bin/env python3

import os
import subprocess
import sys
import click

def docker_compose_exec(*args):
    subprocess.run(['docker-compose', 'exec'] + list(args))

@click.group()
def cli():
    """
    Unified way to run things
    """
    pass


@click.command()
@click.option('--ip', default='0.0.0.0')
@click.option('--port', default='8000')
def server(ip, port):
    """
    Run development server. By default it listens on all interfaces(0.0.0.0) and port 8000
    """
    docker_compose_exec('app', './bin/runserver.sh', ip, port)

@click.command(name='pip-install')
def pip_install():
    """
    Install python dependencies from requirements.development.txt
    """
    docker_compose_exec('app', './bin/install.sh')

@click.group()
def db():
    """
    Database related commands
    """
    pass

def run_with_psql(*args):
    docker_compose_exec(*(['postgresql', 'psql'] + list(args)))

@click.command()
@click.option("--user", default='fereol')
def psql(user):
    """
    Runs interactive psql session, by default with user `fereol`.
    """
    run_with_psql('-U', user)


@click.command()
@click.argument("path", required=True)
def load(path):
    """
    Load database from .sql file. Path should be relative to db_backups/
    """
    run_with_psql('-U', 'postgres', '-c', 'DROP DATABASE "fereol";')
    run_with_psql('-U', 'postgres', '-c', 'CREATE DATABASE "fereol";')
    run_with_psql('-U', 'fereol', '-f' '/db_backups/{}'.format(path))


@click.group()
def static():
    """
    Static files related commands
    """
    pass

@click.command(name='compile')
def compile_():
    """
    Compiles all assets to static files using `yarn dev`
    """
    docker_compose_exec('frontend', 'yarn', 'dev')


@click.command()
@click.argument('cmd', nargs=-1)
def manage(cmd):
    """
    Runs manage.py [ARGS]
    """
    docker_compose_exec(*(['app', 'python', 'manage.py'] + list(cmd)))

cli.add_command(db)

cli.add_command(server)

db.add_command(psql)
db.add_command(load)

cli.add_command(static)

static.add_command(compile_)

cli.add_command(pip_install)
cli.add_command(manage)

if __name__ == '__main__':
    cli()
