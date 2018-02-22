#!/usr/bin/env python
import argparse
import datetime
import smtplib
import sys
import syslog
import traceback
import urllib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests


def check_arg(args=None):
    parser = argparse.ArgumentParser(description="Script to get RabbitMQ Email Alerts")
    parser.add_argument("-host", "--arg_host",
                        help="RabbitMQ Host Name",
                        required="True")
    parser.add_argument("-port", "--arg_port",
                        help="RabbitMQ Port Number",
                        required="True")
    parser.add_argument("-vhost", "--arg_vhost",
                        help="RabbitMQ vhost",
                        required="True")
    parser.add_argument("-usr", "--arg_user",
                        help="RabbitMQ Login User",
                        required="True")
    parser.add_argument("-pwd", "--arg_password",
                        help="RabbitMQ Login Password",
                        required="True")
    parser.add_argument("-queue", "--arg_queue_name",
                        help="RabbitMQ Queue Name",
                        required="True")
    parser.add_argument("-queueAlias", "--arg_queue_alias",
                        help="RabbitMQ Queue Alias (No spaces)",
                        required="True")
    parser.add_argument("-threshold", "--arg_threshold_messages_count",
                        type=int,
                        help="RabbitMQ Messages Count Threshold (int). Pass 0 to get alerts when there are messages in the queue (used for sideline alerts)",
                        required="True")
    parser.add_argument("-ackRate", "--arg_threshold_ack_rate",
                        type=float,
                        help="RabbitMQ Ack Rate Threshold (float). Ignored when 0 is passed to rabbitmq_threshold_messages_count",
                        required="True")
    parser.add_argument("-emailFrom", "--arg_email_from_address",
                        help="From Email ID",
                        required="True")
    parser.add_argument("-emailPwd", "--arg_email_from_password",
                        help="From Email ID's password. Pass 'None' if there is no password required",
                        default="None")
    parser.add_argument("-emailTo", "--arg_email_to_address",
                        help="To Email ID. Must be separated by commas (without spaces) in case of multiple IDs",
                        required="True")
    parser.add_argument("-emailHost", "--arg_email_host",
                        help="Email ID Host",
                        required="True")
    parser.add_argument("-emailPort", "--arg_email_port",
                        help="Email ID Port",
                        required="True")

    results = parser.parse_args(args)

    return (results.arg_host,
            results.arg_port,
            urllib.quote(results.arg_vhost, safe=''),
            (results.arg_user, results.arg_password),
            results.arg_queue_name,
            results.arg_queue_alias,
            results.arg_threshold_messages_count,
            results.arg_threshold_ack_rate,
            results.arg_email_from_address,
            results.arg_email_from_password,
            results.arg_email_to_address.split(","),
            results.arg_email_host,
            results.arg_email_port)


def get_rmq_queue_details(grqd_host, grqd_port, grqd_vhost, grqd_queue_name, grqd_rabbitmq_authentication):
    try:
        rmq_response = requests.get(api_rabbitmq_queues % (grqd_host, grqd_port, grqd_vhost, grqd_queue_name),
                                    auth=grqd_rabbitmq_authentication)
        if rmq_response.status_code == 200:
            return rmq_response.json()
        else:
            syslog.syslog(syslog.LOG_ERR,
                          "Failed to get RabbitMQ queue details. Response: " + str(rmq_response) + ". Exiting..")
            print("Failed to get RabbitMQ queue details. Response: " + str(rmq_response) + ". Exiting..")
            exit()
    except Exception:
        syslog.syslog(syslog.LOG_ERR,
                      "Failed to get RabbitMQ queue details. Response: " + str(traceback.format_exc()) + ". Exiting..")
        print("Failed to get RabbitMQ queue details. Response: " + str(traceback.format_exc()) + ". Exiting..")
        exit()


def alert_by_mail(abm_from_email, abm_from_email_password, abm_to_email, abm_queue_name, abm_queue_alias,
                  abm_email_host, abm_email_port, abm_messages_count, abm_ack_rate, abm_mail_subject):
    try:
        from_address = abm_from_email
        to_address = abm_to_email
        message = MIMEMultipart()
        message["From"] = from_address
        message["To"] = ", ".join(to_address)
        message["Subject"] = abm_mail_subject % (abm_queue_alias, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        body = "Queue: %s (%s)\nMessages: %s\nAck rate: %s" % (
            abm_queue_name, abm_queue_alias, abm_messages_count, abm_ack_rate)
        message.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP(abm_email_host, abm_email_port)
        server.ehlo()
        if abm_from_email_password != "None":
            server.login(abm_from_email, abm_from_email_password)
        text = message.as_string()
        server.sendmail(from_address, to_address, text)
        server.quit()
    except Exception:
        syslog.syslog(syslog.LOG_ERR,
                      "Failed to send alert mail. Exception: %s\n\n" % (traceback.format_exc()))
        print("Failed to send alert mail. Exception: %s\n\n" % (traceback.format_exc()))

if __name__ == '__main__':

    api_rabbitmq_queues = "http://%s:%s/api/queues/%s/%s"

    try:
        rabbitmq_host, rabbitmq_port, rabbitmq_vhost, rabbitmq_authentication, rabbitmq_queue_name, rabbitmq_queue_alias, rabbitmq_threshold_messages_count, rabbitmq_threshold_ack_rate, email_from_address, email_from_password, email_to_address, email_host, email_port = check_arg(
            sys.argv[1:])
        rabbitmq_queue_result = get_rmq_queue_details(rabbitmq_host, rabbitmq_port, rabbitmq_vhost, rabbitmq_queue_name,
                                                      rabbitmq_authentication)
        rabbitmq_messages_count = int(rabbitmq_queue_result['messages'])
        rabbitmq_ack_rate = float(rabbitmq_queue_result['message_stats']['ack_details']['rate'])
        syslog.syslog(syslog.LOG_INFO,
                      "RMQ Alert -> Messages: " + str(rabbitmq_messages_count) + " | Ack rate: " + str(rabbitmq_ack_rate))
        print("Messages: " + str(rabbitmq_messages_count) + " | Ack rate: " + str(rabbitmq_ack_rate))
        if rabbitmq_threshold_messages_count == 0:
            if rabbitmq_messages_count != 0:
                mail_subject = "[RabbitMQ Alert] Sideline in %s at around %s"
                alert_by_mail(email_from_address, email_from_password, email_to_address, rabbitmq_queue_name,
                              rabbitmq_queue_alias, email_host, email_port, rabbitmq_messages_count, "N/A",
                              mail_subject)
        else:
            if (rabbitmq_messages_count >= rabbitmq_threshold_messages_count) and (rabbitmq_ack_rate <= rabbitmq_threshold_ack_rate):
                mail_subject = "[RabbitMQ Alert] Low throughput in %s at around %s"
                alert_by_mail(email_from_address, email_from_password, email_to_address, rabbitmq_queue_name,
                              rabbitmq_queue_alias, email_host, email_port, rabbitmq_messages_count, rabbitmq_ack_rate,
                              mail_subject)
    except Exception:
        syslog.syslog(syslog.LOG_ERR,
                      "RMQ Alert -> Error: " + traceback.format_exc())
        print(traceback.format_exc())
