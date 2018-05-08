#!/usr/bin/env python3
import os
import subprocess
import time
import traceback
from datetime import datetime, timedelta

import environ
import dropbox


from slack_notifications import (
    initialize_slack, send_error_notification, send_success_notification
)

DROPBOX_DEV_DUMPS_DIRNAME = '/dev_dumps'
DROPBOX_PROD_DUMPS_DIRNAME = '/prod_dumps'
DUMPS_THRESHOLD = timedelta(weeks=-4)

def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))

def get_dump_filename(suffix: str):
    time_now_str = time.strftime('%Y_%m_%d__%H_%M_%S')
    path = '/tmp/ii_zapisy_db_dump_{}'.format(time_now_str)
    with_suffix = '{}_{}'.format(path, suffix) if suffix else path
    # Must end with 7z or 7za will append it itself
    return "{}.7z".format(with_suffix)

def get_secrets_env():
    env = environ.Env()
    secrets_file_path = os.path.join(get_script_dir(), os.pardir, 'env', '.env')
    environ.Env.read_env(secrets_file_path)
    return env


def build_env_with_db_secrets(secrets_env):
    new_environ = os.environ.copy()
    new_environ.update({
        'II_ZAPISY_DB_BACKUP_DB_NAME': secrets_env.str('DATABASE_NAME'),
        'II_ZAPISY_DB_BACKUP_DB_USER': secrets_env.str('DATABASE_USER'),
        'II_ZAPISY_DB_BACKUP_DB_PASS': secrets_env.str('DATABASE_PASSWORD'),
        'II_ZAPISY_DB_BACKUP_DB_PORT': secrets_env.str('DATABASE_PORT'),
        'II_ZAPISY_DB_BACKUP_DUMP_PASS': secrets_env.str('DATABASE_DUMP_PASSWORD')
    })
    return new_environ

# The actual dumping is performed in a separate bash script
# since interfacing with pg_dump/7za is easier there
def perform_database_dump(out_dev_dump: str, out_prod_dump: str, secrets_env):
    new_environ = build_env_with_db_secrets(secrets_env)
    result = subprocess.run(
        './perform_dump.sh {} {} > /dev/null'.format(out_dev_dump, out_prod_dump),
        shell=True,
        stderr=subprocess.PIPE,
        env=new_environ,
        cwd=get_script_dir(),
    )

    if result.returncode != 0:
        raise RuntimeError(
            'perform_dump.sh failed with error code {}: {}'.format(
                result.returncode, result.stderr.decode('utf-8'),
            )
        )



def get_dropbox_instance(secrets_env):
    return dropbox.Dropbox(secrets_env.str('DROPBOX_OAUTH2_TOKEN'))

def dropbox_file_exists(dbx, path: str):
    try:
        dbx.files_get_metadata(path)
        return True
    except:
        return False

def ensure_has_required_dirs(dbx):
    try:
        dbx.files_create_folder(DROPBOX_DEV_DUMPS_DIRNAME)
    except dropbox.exceptions.ApiError:
        pass
    try:
        dbx.files_create_folder(DROPBOX_PROD_DUMPS_DIRNAME)
    except dropbox.exceptions.ApiError:
        pass

def remove_files_older_than_in_folder(dbx, threshold_dt, folder_path: str):
    list_folder_result = dbx.files_list_folder(folder_path)
    for file_entry in list_folder_result.entries:
        file_date = file_entry.client_modified
        if file_date < threshold_dt:
            dbx.files_delete(file_entry.path_lower)

def remove_dumps_older_than_threshold(dbx):
    oldest_allowed_modtime = datetime.now() + DUMPS_THRESHOLD
    remove_files_older_than_in_folder(dbx, oldest_allowed_modtime, DROPBOX_DEV_DUMPS_DIRNAME)
    remove_files_older_than_in_folder(dbx, oldest_allowed_modtime, DROPBOX_PROD_DUMPS_DIRNAME)

# Upload a local file to a Dropbox folder, preserving the
# file's name
def upload_from_file_to_folder(dbx, file_path: str, folder_path: str) -> str:
    file_bytes = open(file_path, mode='rb').read()
    file_name = os.path.basename(file_path)
    dropbox_path = os.path.join(folder_path, file_name)
    dbx.files_upload(file_bytes, dropbox_path)
    return dropbox_path

# Uploads both dumps; returns the generated share link for the dev dump
def upload_generated_dumps(dbx, dev_dump_path: str, prod_dump_path: str) -> str:
    ensure_has_required_dirs(dbx)
    remove_dumps_older_than_threshold(dbx)
    dev_dbx_path = upload_from_file_to_folder(dbx, dev_dump_path, DROPBOX_DEV_DUMPS_DIRNAME)
    upload_from_file_to_folder(dbx, prod_dump_path, DROPBOX_PROD_DUMPS_DIRNAME)
    return dbx.sharing_create_shared_link(dev_dbx_path)


# Main backup routine. Dumps the DBs & uploads them to Dropbox.
# Returns the generated share link for the dev dump
def perform_full_backup(secrets_env) -> str:
    dev_dump_filename = get_dump_filename('dev')
    prod_dump_filename = get_dump_filename('prod')
    perform_database_dump(dev_dump_filename, prod_dump_filename, secrets_env)
    dbx = get_dropbox_instance(secrets_env)
    dev_db_shared_link = upload_generated_dumps(dbx, dev_dump_filename, prod_dump_filename)
    os.remove(dev_dump_filename)
    os.remove(prod_dump_filename)
    return dev_db_shared_link

def main():
    try:
        start_time = datetime.now()
        secrets_env = get_secrets_env()
        initialize_slack(secrets_env)
        shared_link = perform_full_backup(secrets_env)
        end_time = datetime.now()
        seconds_elapsed = (end_time - start_time).seconds
        send_success_notification(shared_link.url, seconds_elapsed)
    except Exception:
        err_desc = traceback.format_exc()
        send_error_notification(err_desc)
main()
