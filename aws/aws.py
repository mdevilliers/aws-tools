
from __future__ import print_function

import boto.ec2
from datetime import datetime
import math


class AWS(object):

    def __init__(self, aws_access_key, aws_secret_key,
                 aws_region):

        self._connection = boto.ec2.connect_to_region(aws_region,
                                              aws_access_key_id=aws_access_key,
                                              aws_secret_access_key=aws_secret_key)
        self._region = aws_region

    """Retreives a list of running instances

    :param state one of running, terminated, stopped
    :returns: AWSInstance

    """
    def instances(self, state="running"):

        reservations = self._connection.get_all_reservations()

        for reservation in reservations:

            for instance in reservation.instances:

                if instance.state == state:
                    launchedAtUtc = self._parse_date_time(instance.launch_time)

                    yield AWSInstance(identifier=instance.id,
                                      launchedAtUtc=launchedAtUtc,
                                      aws_region=self._region,
                                      aws_instance_type=instance.instance_type,
                                      keyname=instance.key_name,
                                      tags=instance.tags)
    def volumes(self):

        volumes = self._connection.get_all_volumes()

        for volume in volumes:
            createdAtUtc = self._parse_date_time(volume.create_time)
 
            yield AWSVolume(volume.id, volume.size, volume.type, self._region, volume.iops, createdAtUtc)


    def _parse_date_time(self, datetime_str):
        # example - 2016-01-13T15:42:25.000Z
        return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')


class AWSVolume(object):

    def __init__(self, identifier, size, volume_type, aws_region, iops, createdAtUtc):
        self.identifier = identifier
        self.size = size
        self.type = volume_type
        self.aws_region = aws_region,
        self.iops = iops
        self.createdAtUtc = createdAtUtc
        self.cost = 0.0

    def calculate_cost(self, something):
        return 0.0

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
