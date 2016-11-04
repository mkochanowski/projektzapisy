#!/bin/bash
source /home/zapisy/env26/bin/activate
cd /home/zapisy/projektzapisy/current/zapisy
python manage.py send_mail
