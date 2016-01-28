
from __future__ import print_function

import boto.ec2
from datetime import datetime
import math


class AWSRunningInstances(object):
    """Retreives a list of running instances"""

    """

    :param aws_access_key
    :param aws_secret_key
    :param state one of running, terminated, stopped

    :returns: AWSInstance

    """
    def instances(self, aws_access_key, aws_secret_key,
                  aws_region, state="running"):

        ec2_conn = boto.ec2.connect_to_region(aws_region,
                                              aws_access_key_id=aws_access_key,
                                              aws_secret_access_key=aws_secret_key)

        reservations = ec2_conn.get_all_reservations()

        for reservation in reservations:

            for instance in reservation.instances:

                if instance.state == state:
                    launchedAtUtc = self._parse_date_time(instance.launch_time)
                    identifier = instance.id

                    yield AWSInstance(identifier=identifier,
                                      launchedAtUtc=launchedAtUtc,
                                      aws_region=aws_region,
                                      aws_instance_type=instance.instance_type,
                                      keyname=instance.key_name,
                                      tags=instance.tags)

    def _parse_date_time(self, datetime_str):
        # example - 2016-01-13T15:42:25.000Z
        return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.000Z')


class AWSInstance(object):

    def __init__(self, identifier, launchedAtUtc, aws_region,
                 aws_instance_type, keyname, tags=[]):
        self.identifier = identifier
        self.cost = 0.0
        self.cost_per_hour = 0.0
        self.launchedAtUtc = launchedAtUtc
        self.aws_region = aws_region
        self.aws_instance_type = aws_instance_type
        self.keyname = keyname
        self.tags = tags

    def calculate_cost(self, cost_per_hour):
        """Given a cost per hour will calculate the total cost since creation.

        Note : total cost is rounded up to the nearest completed hour.
        """
        elapsed_hours_since_creation = self._total_hours_since_creation()
        self.cost = cost_per_hour * elapsed_hours_since_creation
        self.cost_per_hour = cost_per_hour

    def _total_hours_since_creation(self):
        now = datetime.utcnow()
        delta_since_last_update = now - self.launchedAtUtc
        total_seconds = delta_since_last_update.total_seconds()
        return math.ceil(total_seconds / 3600)
