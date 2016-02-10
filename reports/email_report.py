

from __future__ import print_function

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


class HtmlEmailTemplateReportWriter(object):

    def __init__(self, from_email_address, recipients, email_password):
        self._from_email_address = from_email_address
        self._recipients = recipients
        self._email_password = email_password

    def write(self, instances, volumes):

        instances.sort(key=lambda x: x.cost, reverse=True)

        total_cost = 0
        total_cost_per_hour = 0

        html = "<html><head></head><body><table border='1'>"
        html += "<tr><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th><th>{}</th></tr>".format(
                    "Launched",
                    "Cost",
                    "Identifier",
                    "Type",
                    "Region",
                    "Keyname",
                    "Tags"
                )

        for instance in instances:

            total_cost += instance.cost
            total_cost_per_hour += instance.cost_per_hour

            row = "<tr><td>{}</td><td>${:.2f}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td width='45%'>{}</td><tr>".format(
                                instance.launchedAtUtc,
                                instance.cost,
                                instance.identifier,
                                instance.aws_instance_type,
                                instance.aws_region,
                                instance.keyname,
                                instance.tags)
            html += row

        html += "</table>"
        html += "</br> Ongoing (hour) : ${:.2f}<br />Ongoing (day) : ${:.2f}<br /> Ongoing (30 day month) : ${:.2f}<br />Total accrued cost : ${:.2f} <br / >".format(
            total_cost_per_hour,
            total_cost_per_hour * 24,
            total_cost_per_hour * 24 * 30,
            total_cost)

        volumes_cost_per_month = 0

        for volume in volumes:
            volumes_cost_per_month += volume.cost

        html += "Volumes (total): {} <br/> Ongoing (30 day month) : ${:.2f}</body></html>".format(
            len(volumes),
            volumes_cost_per_month)

        now = datetime.utcnow()
        title = "AWS Usage {}".format(now)
        self._send_email(title, html)
        
    def _send_email(self, title, htmlmessage):

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(self._from_email_address, self._email_password)

        msg = MIMEMultipart('alternative')
        msg['Subject'] = title
        msg['From'] = self._from_email_address
        msg['To'] = ", ".join(self._recipients)

        part1 = MIMEText(htmlmessage, 'html')
        msg.attach(part1)

        server.sendmail(self._from_email_address, self._recipients, msg.as_string())
        server.quit()
