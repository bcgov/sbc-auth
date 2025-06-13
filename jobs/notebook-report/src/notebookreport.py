"""The Notebook Report - This module is the API for the Auth Notebook Report."""

import ast
import fnmatch
import logging
import os
import requests
import base64
from pathlib import Path
import sys
import traceback
from datetime import date, datetime, timedelta

import papermill as pm
from flask import Flask, current_app

from config import Config
from structured_logging import StructuredLogging

# Notebook Scheduler
# ---------------------------------------
# This script helps with the automated processing of Jupyter Notebooks via
# papermill (https://github.com/nteract/papermill/)


def create_app(config=Config):
    """Create app."""
    app = Flask(__name__)
    app.config.from_object(config)

    # Configure Structured Logging
    structured_logger = StructuredLogging()
    structured_logger.init_app(app)
    app.logger = structured_logger.get_logger()

    return app


def findfiles(directory, pattern):
    """Find files matched."""
    for filename in os.listdir(directory):
        if fnmatch.fnmatch(filename.lower(), pattern):
            yield os.path.join(directory, filename)

def send_email(email: dict, token):
    """Send the email."""    
    response = requests.request("POST",
        Config.NOTIFY_API_URL,
        json=email,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )
        
    if response.status_code == 200:
        current_app.logger.info('The email was sent successfully')
    else:    
        current_app.logger.error(f'response:{response}')
        raise Exception('Unsuccessful response when sending email.')
  

def processnotebooks(notebookdirectory, token):
    """Process Notebook."""

    ext = ''
    if not Config.ENVIRONMENT == 'production':
        ext = ' on ' + Config.ENVIRONMENT
        
    week_report_dates = ast.literal_eval(Config.WEEKLY_REPORT_DATES)

    # For weekly tasks, we only run on the specified days
    if date.today().weekday() in week_report_dates:
        current_app.logger.info('Processing: %s', notebookdirectory)
        file = 'auth.ipynb'
        
        subject = 'SBC-AUTH Weekly Stats till ' + datetime.strftime(datetime.now()-timedelta(1), '%Y-%m-%d') + ext
        filename = 'auth_weekly_stats_till_' + datetime.strftime(datetime.now()-timedelta(1), '%Y-%m-%d') + '.csv'
        recipients = Config.WEEKLY_REPORT_RECIPIENTS        
           
        email = {
            'recipients': recipients,
            'content': {
                'subject': subject,
                'body': 'Please see the attachment(s).',
                'attachments': []
            }
        }    

        try:
            pm.execute_notebook(os.path.join(notebookdirectory, file), 'temp.ipynb', parameters=None)
            with open(filename, "rb") as f:
                attachments = []
                file_encoded = base64.b64encode(f.read())
                attachments.append(
                    {
                        'fileName': filename,
                        'fileBytes': file_encoded.decode(),
                        'fileUrl': '',
                        'attachOrder': 1
                    }
                )
            email['content']['attachments'] = attachments
        except Exception:  # noqa: B902
            current_app.logger.error('Error processing notebook %s.', notebookdirectory)
            email = {
                'recipients': Config.ERROR_EMAIL_RECIPIENTS,
                'content': {
                    'subject': 'Error Notification ' + subject,
                    'body': 'Failed to generate report: ' + traceback.format_exc(),
                    'attachments': []
                }
            }
        finally:
            if Path('temp.ipynb').exists():
                os.remove('temp.ipynb')
            if Path(filename).exists():    
                os.remove(filename)
            send_email(email, token)            


if __name__ == '__main__':
    app = create_app(Config)
    app.app_context().push()    
    start_time = datetime.now()
    
    client = Config.NOTIFY_CLIENT_ID
    secret = Config.NOTIFY_CLIENT_SECRET
    kc_url = Config.KEYCLOAK_AUTH_TOKEN_URL 
        
    response = requests.post(url=kc_url,
        data='grant_type=client_credentials',
        headers={'content-type': 'application/x-www-form-urlencoded'},
        auth=(client, secret))
    
    token = response.json()['access_token']

    # processing the files in the fold 'weekly'.
    processnotebooks('weekly', token)

    end_time = datetime.now()
    current_app.logger.info('job - jupyter notebook report completed in: %s', end_time - start_time)
    sys.exit()
