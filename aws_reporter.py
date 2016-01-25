#!/usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser
from aws.price import PriceNotFoundError, AWSPricingStore
from aws.instance import AWSRunningInstances, AWSInstance
from reporter import HtmlEmailTemplateReportWriter, ConsoleReporter
from datetime import datetime
import json 
import logging
import math
from pprint import pprint

regions = ['us-east-1','us-west-1','us-west-2','eu-west-1','sa-east-1',
            'ap-southeast-1','ap-southeast-2','ap-northeast-1']

class Whitelist(object):

    def __init__(self, whitelistfile = 'whitelist.json'):
        # REVIEW : is it okay if this just throws
        with open(whitelistfile) as data_file:
            json_contents = json.load(data_file)
            self._data = map(lambda i: i['identifier'] , json_contents['items'])

    def ok(self, identifier) :
        return not identifier in self._data

def main():

    # Brief
    # daily email to everyone in the engineering team containing: 
    # AWS instance id,  Description, Key-Pair, Tags, Launch date (over 24h), type of instance, Cost since launch 
    # $99 id-238773     m3.xlarge    25/12/2015 10:10:10 Key-Pair Test Instance Tags: { 'name': 'lixo' } 
    # Preferably delivered as a docker instance that I can run on a t2.micro or any other platform. 
    # Must allow for whitelisting instance-ids for services meant to run 24/7 

    # format email
    # send to mailing list

    parser = ArgumentParser(
        'aws_reporter.py', description="Collates a report of running AWS instances"
    )
    parser.add_argument(
        '--aws-access-key', required=True
    )
    parser.add_argument(
        '--aws-secret-key', required=True
    )
    parser.add_argument(
        '--email-password', required=True
    )
    parser.add_argument(
        '--reports', default="Console", 
        help="Comma seperated list frawn from the following - Console, Email"
    )

    opts = parser.parse_args()

    now = datetime.utcnow()
    grace_period_in_hours = 24
    whitelist = Whitelist()
    price_store = AWSPricingStore()
    instance_manager = AWSRunningInstances()
    costed_instances = []

    for region in regions :

        for instance in instance_manager.instances(opts.aws_access_key, opts.aws_secret_key, region) :

            if whitelist.ok(instance.identifier) and _running_before_min_age(now, instance.createdAtUtc, grace_period_in_hours):

                try :
                    price = price_store.cost_per_hour(instance.aws_region, instance.aws_instance_type)
                    instance.calculate_cost(price)
                    costed_instances.append(instance)

                except PriceNotFoundError:
                    logging.warning("Price not found for {} ({} in {} running since {})".format(instance.identifier, 
                                                                                        instance.aws_instance_type, 
                                                                                        instance.aws_region, 
                                                                                        instance.createdAtUtc))

    for report_type in opts.reports.split(","):

        if report_type == "Console" :
            consolereporter = ConsoleReporter()
            consolereporter.report(costed_instances)
        elif report_type == "Email" :
            # "jorge.costa@clusterhq.com",
            email_reporter = HtmlEmailTemplateReportWriter("mark.devilliers@clusterhq.com", ["markdevilliers@gmail.com"], opts.email_password)  
            email_reporter.report(costed_instances)

def _running_before_min_age(now, created_at, grace_period_in_hours):
    return (now - created_at).total_seconds() > (grace_period_in_hours * 60 * 60)

if __name__ == '__main__':
    main()