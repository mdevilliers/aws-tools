
from __future__ import print_function

import json


class PriceNotFoundError(Exception):
    def __init__(self, aws_region, aws_type):
        self.aws_region = aws_region
        self.aws_type = aws_type


class AWSPricingStore(object):
    """Stores current prices for AWS things."""

    def __init__(self, instance_price_file='data.aws.ondemand.json',
                        ebs_price_file='data.aws.ebs.json'):

        # REVIEW : is it okay if this just throws
        with open(instance_price_file) as data_file:
            self._instance_data = json.load(data_file)
        with open(ebs_price_file) as data_file:
            self._ebs_data = json.load(data_file)

    def volume_costs(self, aws_region, ebs_type):
        """
        For a given region and type retrieves a cost per hour in USD

        :param aws_region
        :param aws_type

        :returns: cost per hour, iops_rate (both in USD) 

        """
        return self._find_volume_price_in_data(aws_region, ebs_type)

    def instance_cost_per_hour(self, aws_region, aws_type):
        """
        For a given region and type retrieves a cost per hour in USD

        :param aws_region
        :param aws_type

        :returns: cost per hour (in USD)

        """
        return self._find_instance_cost(aws_region, aws_type)

    def _find_instance_cost(self, aws_region, aws_type):

        found, cost = self._previous_generation_instance_look_up(aws_region, aws_type)

        if found:
            return cost

        found, cost = self._find_instance_price_in_data(aws_region, aws_type)

        if found:
            return cost

        raise PriceNotFoundError(aws_region, aws_type)

    # https://aws.amazon.com/ec2/previous-generation/
    def _previous_generation_instance_look_up(self, aws_region, aws_type):
        if aws_region == "us-east-1" and aws_type == "m1.medium":
            return True, 0.087
        if aws_region == "us-west-2" and aws_type == "t1.micro":
            return True, 0.02
        if aws_region == "eu-west-1" and aws_type == "m1.medium":
            return True, 0.095
        return False, 0.0

    def _find_instance_price_in_data(self, aws_region, aws_type):
        regions = self._first_or_none(
                        filter(
                            lambda r: r['region'] == aws_region,
                            self._instance_data['regions']))

        if regions is None:
            return False, 0.00

        instance_types = self._first_or_none(
                filter(
                    lambda r: r['type'] == aws_type, regions['instanceTypes']))

        if instance_types is None:
            return False, 0.00

        return True, instance_types['price']

    def _find_volume_price_in_data(self, aws_region, ebs_type):
        # http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EBSVolumeTypes.html
        # loookup   nice name               data name
        # gp2       General Purpose (SSD)   Amazon EBS General Purpose (SSD) volumes
        # io1       Provisioned IOPS (SSD)  Amazon EBS Provisioned IOPS (SSD) volumes
        # standard  Magnetic                Amazon EBS Magnetic volumes
        if ebs_type == 'gp2':
             return self._get_volume_prices(aws_region, 'Amazon EBS General Purpose (SSD) volumes')
        if ebs_type == 'io1':
            return self._get_volume_prices(aws_region, 'Amazon EBS Provisioned IOPS (SSD) volumes')
        if ebs_type == 'standard':
            return self._get_volume_prices(aws_region, 'Amazon EBS Magnetic volumes')

        return PriceNotFoundError(aws_region, ebs_type)

    # ugly
    def _get_volume_prices(self, aws_region, type_long_name):
        region = self._first_or_none(
                        filter(
                            lambda r: r['region'] == aws_region, self._ebs_data['config']['regions']
                        ))

        if region is None:
            PriceNotFoundError(aws_region, ebs_type)

        types = region['types']

        values = filter(lambda t: t['name'] == 'Amazon EBS Magnetic volumes', types)
        perGBrate = filter(lambda p: p['rate'] == 'perGBmoProvStorage', values[0]['values'])
        iops = filter(lambda p: p['rate'] == 'perMMIOreq', values[0]['values'])
        return float(perGBrate[0]['prices']['USD']), float(iops[0]['prices']['USD'])

    # REVIEW : this must already exist in the stdlib ?
    def _first_or_none(self, some_list):
        return some_list[0] if some_list else None
