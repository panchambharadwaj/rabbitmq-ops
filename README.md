RabbitMQ Ops
=====================

Sends email alerts when Threshold and Ack rate limits are breached for a queue. This can be added as a job to cron under Linux or Unix.

    Syntax:
    ------
 
    python rabbitmq-alerts.py -host %s -port %s -vhost %s -usr %s -pwd %s -queue %s -qalias %s -threshold %s -ack %s -efrom %s -epwd %s -eto %s -ehost %s -eport %s
 
    Example:
    -------

    python rabbitmq-alerts.py -host prod-rmq.company.nm1 -port 12345 -vhost / -usr user -pwd password -queue SomeQueueName -qalias "Queue Alias" -threshold 1000 -ack 0.2 -efrom from@abc.com -epwd password123 -eto to01@abc.com,to02@abc.com -ehost smtp.gmail.com -eport 587
    
    Usage:
    ------
    usage: rabbitmq-alerts.py [-h] -host HOST -port PORT -vhost VHOST -usr USER
                          -pwd PASSWORD -queue QUEUE_NAME -queueAlias
                          QUEUE_ALIAS -threshold THRESHOLD_MESSAGES_COUNT
                          -ackRate THRESHOLD_ACK_RATE -emailFrom
                          EMAIL_FROM_ADDRESS [-emailPwd EMAIL_FROM_PASSWORD]
                          -emailTo EMAIL_TO_ADDRESS -emailHost EMAIL_HOST
                          -emailPort EMAIL_PORT

    Script to get RabbitMQ Email Alerts
    
    optional arguments:
      -h, --help            show this help message and exit
      -host HOST, --host HOST
                            RabbitMQ Host Name
      -port PORT, --port PORT
                            RabbitMQ Port Number
      -vhost VHOST, --vhost VHOST
                            RabbitMQ vhost
      -usr USER, --user USER
                            RabbitMQ Login User
      -pwd PASSWORD, --password PASSWORD
                            RabbitMQ Login Password
      -queue QUEUE_NAME, --queue_name QUEUE_NAME
                            RabbitMQ Queue Name
      -queueAlias QUEUE_ALIAS, --queue_alias QUEUE_ALIAS
                            RabbitMQ Queue Alias (No spaces)
      -threshold THRESHOLD_MESSAGES_COUNT, --threshold_messages_count THRESHOLD_MESSAGES_COUNT
                            RabbitMQ Messages Count Threshold (int). Pass 0 to get
                            alerts when there are messages in the queue (used for
                            sideline alerts)
      -ackRate THRESHOLD_ACK_RATE, --threshold_ack_rate THRESHOLD_ACK_RATE
                            RabbitMQ Ack Rate Threshold (float). Ignored when 0 is
                            passed to rabbitmq_threshold_messages_count
      -emailFrom EMAIL_FROM_ADDRESS, --email_from_address EMAIL_FROM_ADDRESS
                            From Email ID
      -emailPwd EMAIL_FROM_PASSWORD, --email_from_password EMAIL_FROM_PASSWORD
                            From Email ID's password. Pass 'None' if there is no
                            password required
      -emailTo EMAIL_TO_ADDRESS, --email_to_address EMAIL_TO_ADDRESS
                            To Email ID. Must be separated by commas (without
                            spaces) in case of multiple IDs
      -emailHost EMAIL_HOST, --email_host EMAIL_HOST
                            Email ID Host
      -emailPort EMAIL_PORT, --email_port EMAIL_PORT
                            Email ID Port
