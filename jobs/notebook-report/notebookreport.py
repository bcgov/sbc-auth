"""The Notebook Report - This module is the API for the Auth Notebook Report."""

import ast
import fnmatch
import logging
import os
import smtplib
import sys
import traceback
from datetime import date, datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import papermill as pm
from flask import Flask, current_app

from config import Config
from util.logging import setup_logging

setup_logging(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logging.conf'))  # important to do this first

# Notebook Scheduler
# ---------------------------------------
# This script helps with the automated processing of Jupyter Notebooks via
# papermill (https://github.com/nteract/papermill/)


def create_app(config=Config):
    """Create app."""
    app = Flask(__name__)
    app.config.from_object(config)
    # db.init_app(app)
    app.app_context().push()
    current_app.logger.debug('created the Flask App and pushed the App Context')

    return app


def findfiles(directory, pattern):
    """Find files matched."""
    for filename in os.listdir(directory):
        if fnmatch.fnmatch(filename.lower(), pattern):
            yield os.path.join(directory, filename)


def send_email(note_book, emailtype, errormessage):
    """Send email for results."""
    message = MIMEMultipart()
    date_str = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
    ext = ''
    if not Config.ENVIRONMENT == 'prod':
        ext = ' on ' + Config.ENVIRONMENT

    if emailtype == 'ERROR':
        subject = "Jupyter Notebook Error Notification from sbc-auth for processing '" \
            + note_book + "' on " + date_str + ext
        recipients = Config.ERROR_EMAIL_RECIPIENTS
        message.attach(MIMEText('ERROR!!! \n' + errormessage, 'plain'))
    else:
        file_processing = note_book.split('.ipynb')[0]

        if file_processing == 'auth':
            subject = 'SBC-AUTH Weekly Stats till ' + datetime.strftime(datetime.now()-timedelta(1), '%Y-%m-%d') + ext
            filename = 'auth_weekly_stats_till_' + datetime.strftime(datetime.now()-timedelta(1), '%Y-%m-%d') + '.csv'
            recipients = Config.WEEKLY_REPORT_RECIPIENTS

        # Add body to email
        message.attach(MIMEText('Please see attached.', 'plain'))

        # Open file in binary mode
        with open(os.path.join(os.getcwd(), r'data/')+filename, 'rb') as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}',
        )

        # Add attachment to message and convert message to string
        message.attach(part)

    message['Subject'] = subject
    server = smtplib.SMTP(Config.EMAIL_SMTP)
    email_list = recipients.strip('][').split(', ')
    logging.info('Email recipients list is: %s', email_list)
    server.sendmail(Config.SENDER_EMAIL, email_list, message.as_string())
    logging.info("Email with subject \'%s\' has been sent successfully!", subject)
    server.quit()


def processnotebooks(notebookdirectory, data_dir):
    """Process Notebook."""
    try:
        week_report_dates = ast.literal_eval(Config.WEEKLY_REPORT_DATES)
    except Exception:  # noqa: B902
        logging.exception('Error processing notebook for %s', notebookdirectory)
        send_email(notebookdirectory, 'ERROR', traceback.format_exc())

    # For weekly tasks, we only run on the specified days
    if date.today().weekday() in week_report_dates:
        logging.info('Processing: %s', notebookdirectory)
        file = 'auth.ipynb'

        try:
            pm.execute_notebook(os.path.join(notebookdirectory, file), data_dir+'temp.ipynb', parameters=None)
            send_email(file, '', '')
            os.remove(data_dir+'temp.ipynb')
        except Exception:  # noqa: B902
            logging.exception('Error processing notebook %s.', notebookdirectory)
            send_email(notebookdirectory, 'ERROR', traceback.format_exc())


if __name__ == '__main__':
    start_time = datetime.utcnow()

    data_directory = os.path.join(os.getcwd(), r'data/')
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)

    # processing the files in the fold 'weekly'.
    processnotebooks('weekly', data_directory)

    end_time = datetime.utcnow()
    logging.info('job - jupyter notebook report completed in: %s', end_time - start_time)
    sys.exit()
