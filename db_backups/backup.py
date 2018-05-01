#!/usr/bin/env python3
import os
import subprocess
import time

def get_temp_database_file_path(suffix):
    time_now_str = time.strftime("")
    path = "/tmp/ii_zapisy_db_dump_{}".format(time_now_str)
    return "{}_{}".format(path, suffix) if suffix else path

def perform_database_dump(out_dev_dump: str, out_prod_dump: str):
    new_environ = os.environ.copy()
    new_environ
    result = subprocess.run(
        "pg_dump -U {} -h localhost -p {} {}".format(DB_USER, DB_PORT, DB_NAME),
        stdout=subprocess.PIPE,
    )

    if result.returncode != 0:
        raise Exception("pg_dump failed with error code {}".format(result.returncode))

    
