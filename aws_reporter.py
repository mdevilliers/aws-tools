#!/usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser, Action

from aws.price import PriceNotFoundError, AWSPricingStore
from aws.instance import AWSRunningInstances, AWSInstance
from reports import HtmlEmailTemplateReportWriter, ConsoleReporter

from datetime import datetime
import json 
import logging
import math
import os
import sys

regions = ['us-east-1','us-west-1','us-west-2','eu-west-1','sa-east-1',
            'ap-southeast-1','ap-southeast-2','ap-northeast-1']

class Whitelist(object):
    """Maintains a white list of instances which ren't included in the reports"""
    def __init__(self, whitelistfile = 'data.whitelist.json'):
        # REVIEW : is it okay if this just throws
        with open(whitelistfile) as data_file:
            json_contents = json.load(data_file)
            self._data = map(lambda i: i['identifier'] , json_contents['items'])

    def ok(self, identifier) :
        return not identifier in self._data

# http://stackoverflow.com/questions/10551117/setting-options-from-environment-variables-when-using-argparse
class EnvDefault(Action):
    """Will inspect the environment for a variable before looking for a command line value"""
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, 
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

def main():

    parser = ArgumentParser(
        'aws_reporter.py', description="Collates a report of running AWS instances"
    )
    parser.add_argument(
        '-aws-access-key', required=True,
        action=EnvDefault, envvar='AWS_ACCESS_KEY',
        help='AWS Access Key (can also be specified using AWS_ACCESS_KEY environment variable)' 
    )
    parser.add_argument(
        '-aws-secret-key', required=True, 
        action=EnvDefault, envvar='AWS_SECRET_KEY',
        help='AWS Secret Key (can also be specified using AWS_SECRET_KEY environment variable)'
    )
    parser.add_argument(
        '--email-password', default=None, required=False,
        action=EnvDefault, envvar='EMAIL_PASSWORD',
        help='Gmail Email password (can also be specified using EMAIL_PASSWORD environment variable)'
    )
    parser.add_argument(
        '--email-from', default=None, required=False,
        action=EnvDefault, envvar='EMAIL_FROM',
        help='From email address (can also be specified using EMAIL_FROM environment variable)'
    )
    parser.add_argument(
        '--email-to', default=None, required=False,
        action=EnvDefault, envvar='EMAIL_TO',
        help='Comma seperated list of email recipients (can also be specified using EMAIL_TO environment variable)'
    )
    parser.add_argument(
        '--reports', default='Console', required=False,
        action=EnvDefault, envvar='REPORTS',  
        help='Comma seperated list from from the following - Console, Email (can also be specified using REPORTS environment variable)'
    )

    opts = parser.parse_args()

    if "Email" in opts.reports :
            if opts.email_from == None or opts.email_to.split(",") == None or opts.email_password == None :
                print("Email reports require --email-password, --email-from and --email-to")
                parser.print_help()
                sys.exit(2)
                return
    # go get the data
    instances = _execute_report(opts.aws_access_key, opts.aws_secret_key)

    # format and send the reports
    _output_reports(instances, opts.reports.split(","), opts)

def _execute_report(aws_access_key, aws_secret_key):

    now = datetime.utcnow()
    grace_period_in_hours = 24
    whitelist = Whitelist()
    price_store = AWSPricingStore()
    instance_manager = AWSRunningInstances()
    costed_instances = []

    for region in regions :

        for instance in instance_manager.instances(aws_access_key, aws_secret_key, region) :

            if whitelist.ok(instance.identifier) and _running_before_min_age(now, instance.launchedAtUtc, grace_period_in_hours):

                try :
                    price = price_store.cost_per_hour(instance.aws_region, instance.aws_instance_type)
                    instance.calculate_cost(price)
                    costed_instances.append(instance)

                except PriceNotFoundError:
                    logging.warning("Price not found for {} ({} in {} running since {})".format(instance.identifier, 
                                                                                        instance.aws_instance_type, 
                                                                                        instance.aws_region, 
                                                                                        instance.launchedAtUtc))
    return costed_instances

def _output_reports(instances, report_list, opts):

    for report_type in report_list:

        if report_type == "Console" :
            consolereporter = ConsoleReporter()
            consolereporter.report(instances)
        elif report_type == "Email" :
            email_reporter = HtmlEmailTemplateReportWriter( opts.email_from, 
                                                            opts.email_to.split(","), 
                                                            opts.email_password)  
            email_reporter.report(instances)

def _running_before_min_age(now, created_at, grace_period_in_hours):
    return (now - created_at).total_seconds() > (grace_period_in_hours * 60 * 60)

if __name__ == '__main__':
    main()