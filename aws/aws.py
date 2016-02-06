
from __future__ import print_function

import boto.ec2
from datetime import datetime
import math
from price import AWSPricingStore


class AWS(object):

    def __init__(self, aws_access_key, aws_secret_key,
                 aws_region):

        self._connection = boto.ec2.connect_to_region(aws_region,
                                                      aws_access_key_id=aws_access_key,
                                                      aws_secret_access_key=aws_secret_key)
        self._region = aws_region
        self._price_store = AWSPricingStore()
    """Retreives a list of instances

    :param state one of running, terminated, stopped
    :returns: AWSInstance

    """
    def instances(self, state="running"):

        reservations = self._connection.get_all_reservations()


        for reservation in reservations:

            for instance in reservation.instances:

                if instance.state == state:
                    launchedAtUtc = self._parse_date_time(instance.launch_time)
                    cost_per_hour = self._price_store.instance_cost_per_hour(self._region, instance.instance_type)

                    yield AWSInstance(identifier=instance.id,
                                      launchedAtUtc=launchedAtUtc,
                                      aws_region=self._region,
                                      aws_instance_type=instance.instance_type,
                                      keyname=instance.key_name,
                                      cost_per_hour=cost_per_hour,
                                      tags=instance.tags)

    """Retreives a list of volumes

    :param state one of running, terminated, stopped
    :returns: AWSVolume

    """
    def volumes(self):

        volumes = self._connection.get_all_volumes()

        for volume in volumes:
            createdAtUtc = self._parse_date_time(volume.create_time)
            cost_per_gb, iops_cost = self._price_store.volume_costs(self._region, volume.type)

            yield AWSVolume(volume.id, volume.size, volume.type, self._region, volume.iops, createdAtUtc, cost_per_gb, iops_cost)

    def _parse_date_time(self, datetime_str):
        # example - 2016-01-13T15:42:25.000Z
        return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ')


class AWSVolume(object):

    def __init__(self, identifier, size, volume_type, aws_region, iops, createdAtUtc, cost_per_gb, iops_cost):
        self.identifier = identifier
        self.size = size
        self.type = volume_type
        self.aws_region = aws_region,
        self.provisioned_iops = iops
        self.createdAtUtc = createdAtUtc
        self.cost_per_gb = cost_per_gb
        self.iops_cost = iops_cost
        self.cost = 0.0

    def calculate_cost(self):
        # https://aws.amazon.com/ebs/pricing/

        # EBS General Purpose (SSD) Volumes

        # Volume storage for General Purpose (SSD) volumes is charged by 
        # the amount you provision in GB per month, until you release the 
        # storage. I/O is included in the price of General Purpose (SSD) 
        # volumes, so you pay only for each GB of storage you provision.

        # EBS Provisioned IOPS (SSD) Volumes

        # Volume storage for EBS Provisioned IOPS (SSD) volumes is charged 
        # by the amount you provision in GB per month, until you release 
        # the storage. 

        # With Provisioned IOPS (SSD) volumes, you are also 
        # charged by the amount you provision in IOPS (input/output operations 
        # per second) multiplied by the percentage of days you provision 
        # for the month. For example, if you provision a volume with 1000 IOPS, 
        # and keep this volume for 15 days in a 30 day month, then in a Region 
        # that charges $0.10 per provisioned IOPS-month, you would be charged 
        # $50 for the IOPS that you provision 
        # ($0.10 per provisioned IOPS-month * 1000 IOPS provisioned * 15 days/30).  
        # You will be charged for the IOPS provisioned on a EBS Provisioned IOPS 
        # (SSD) volume even when the volume is detached from an instance.
        
        # EBS Magnetic Volumes
        # Volume storage for EBS Magnetic volumes is charged by the amount you provision 
        # in GB per month, until you release the storage. Volume I/O for EBS Magnetic 
        # volumes is charged by the number of requests you make to your volume. 


        # http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html
        # loookup   nice name               data name
        # gp2       General Purpose (SSD)   Amazon EBS General Purpose (SSD) volumes
        # io1       Provisioned IOPS (SSD)  Amazon EBS Provisioned IOPS (SSD) volumes
        # standard  Magnetic                Amazon EBS Magnetic volumes
        # if self.type is 'gp2':
        #     pass

        # The EBS standard volume costs $0.10 per GB per month and $0.10 per one million I/O requests. 
        # The EBS provisioned volume costs $0.125 per GB per month and $0.10 per provisioned IOPs per month. 
        if self.type == 'standard':
            self.cost = self.cost_per_gb * self.size
        if self.type == 'gp2':
            self.cost = self.cost_per_gb * self.size
        if self.type == 'io1':
            self.cost = (self.cost_per_gb * self.size) + ( self.provisioned_iops * self.iops_cost)


class AWSInstance(object):

    def __init__(self, identifier, launchedAtUtc, aws_region,
                 aws_instance_type, keyname, cost_per_hour, tags=[]):
        self.identifier = identifier
        self.cost_per_hour = cost_per_hour
        self.launchedAtUtc = launchedAtUtc
        self.aws_region = aws_region
        self.aws_instance_type = aws_instance_type
        self.keyname = keyname
        self.tags = tags
        self.cost = 0.0

    def calculate_cost(self):
        """Given a cost per hour will calculate the total cost since creation.

        Note : total cost is rounded up to the nearest completed hour.
        """
        elapsed_hours_since_creation = self._total_hours_since_creation()
        self.cost = self.cost_per_hour * elapsed_hours_since_creation
        self.cost_per_hour = self.cost_per_hour

    def _total_hours_since_creation(self):
        now = datetime.utcnow()
        delta_since_last_update = now - self.launchedAtUtc
        total_seconds = delta_since_last_update.total_seconds()
        return math.ceil(total_seconds / 3600)
