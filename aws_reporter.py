#!/usr/bin/env python

from __future__ import print_function

from argparse import ArgumentParser, Action

from aws.price import PriceNotFoundError, AWSPricingStore
from aws.aws import AWS
from reports import ConsoleReporter, HtmlEmailTemplateReportWriter

from datetime import datetime
import json
import logging
import os
import sys

regions = ['us-east-1', 'us-west-1', 'us-west-2', 'eu-west-1', 'sa-east-1',
           'ap-southeast-1', 'ap-southeast-2', 'ap-northeast-1']


def main():

    parser = ArgumentParser(
        'aws_reporter.py',
        description="Collates a report of running AWS instances"
    )
    parser.add_argument(
        '-aws-access-key', required=True,
        action=EnvDefault, envvar='AWS_ACCESS_KEY',
        help='AWS Access Key (or AWS_ACCESS_KEY environment variable)'
    )
    parser.add_argument(
        '-aws-secret-key', required=True,
        action=EnvDefault, envvar='AWS_SECRET_KEY',
        help='AWS Secret Key (or AWS_SECRET_KEY environment variable)'
    )
    parser.add_argument(
        '--email-password', default=None, required=False,
        action=EnvDefault, envvar='EMAIL_PASSWORD',
        help='Gmail Email password (or EMAIL_PASSWORD environment variable)'
    )
    parser.add_argument(
        '--email-from', default=None, required=False,
        action=EnvDefault, envvar='EMAIL_FROM',
        help='From email address (or EMAIL_FROM environment variable)'
    )
    parser.add_argument(
        '--email-to', default=None, required=False,
        action=EnvDefault, envvar='EMAIL_TO',
        help='Comma seperated email recipients (or EMAIL_TO environment variable)'
    )
    parser.add_argument(
        '--reports', default='Console', required=False,
        action=EnvDefault, envvar='REPORTS',
        help='Comma seperated list from from - Console, Email (or REPORTS environment variable)'
    )

    opts = parser.parse_args()

    if "Email" in opts.reports:
            if opts.email_from is None or opts.email_to.split(",") is None or opts.email_password is None:
                print("Email reports require --email-password, --email-from and --email-to")
                parser.print_help()
                sys.exit(2)
                return
    # go get the data
    instances, volumes = _execute_report(opts.aws_access_key, opts.aws_secret_key)

    # format and send the reports
    _output_reports(instances, volumes, opts.reports.split(","), opts)


def _execute_report(aws_access_key, aws_secret_key):

    now = datetime.utcnow()
    grace_period_in_hours = 24
    whitelist = Whitelist()
    price_store = AWSPricingStore()
    costed_instances = []
    costed_volumes = []

    for region in regions:

        aws = AWS(aws_access_key, aws_secret_key, region)
        
        for volume in aws.volumes():

            costed_volumes.append(volume)

        for instance in aws.instances():

            if whitelist.ok(instance.identifier) and _running_before_min_age(now, instance.launchedAtUtc, grace_period_in_hours):

                try:
                    price = price_store.cost_per_hour(instance.aws_region, instance.aws_instance_type)
                    instance.calculate_cost(price)
                    costed_instances.append(instance)

                except PriceNotFoundError:
                    logging.warning("Price not found for {} ({} in {} running since {})".format(instance.identifier,
                                                                                                instance.aws_instance_type,
                                                                                                instance.aws_region,
                                                                                                instance.launchedAtUtc))
    return costed_instances, costed_volumes

def _output_reports(instances, volumes, report_list, opts):

    for report_type in report_list:

        if report_type == "Console":
            reporter = ConsoleReporter()
            reporter.write(instances, volumes)
        elif report_type == "Email":
            reporter = HtmlEmailTemplateReportWriter(opts.email_from,
                                                     opts.email_to.split(","),
                                                     opts.email_password)
            reporter.write(instances, volumes)


def _running_before_min_age(now, launched_at, grace_period_in_hours):
    diff = (now - launched_at).total_seconds()
    return diff > (grace_period_in_hours * 60 * 60)


class Whitelist(object):
    """Maintains a white list of instances which are
    to be excluded from the reports"""
    def __init__(self, whitelistfile='data.whitelist.json'):
        # REVIEW : is it okay if this just throws
        with open(whitelistfile) as data_file:
            json_contents = json.load(data_file)
            self._data = map(lambda i: i['identifier'], json_contents['items'])

    def ok(self, identifier):
        return identifier not in self._data


# http://stackoverflow.com/questions/10551117/setting-options-from-environment-variables-when-using-argparse
class EnvDefault(Action):
    """Inspects the environment for a variable
    before looking for a command line value"""
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


if __name__ == '__main__':
    main()
