aws-usage-reporter
------------------

Builds a report of our current aws instances and collates a report with their accrued cost.

The report can either be sent to the console and or via email.

Install dependancies

```
pip install -r requirements.txt
```

```
usage: aws_reporter.py [-h] [-aws-access-key AWS_ACCESS_KEY]
                       [-aws-secret-key AWS_SECRET_KEY]
                       [--email-password EMAIL_PASSWORD]
                       [--email-from EMAIL_FROM] [--email-to EMAIL_TO]
                       [--reports REPORTS]

Collates a report of running AWS instances

optional arguments:
  -h, --help            show this help message and exit
  -aws-access-key AWS_ACCESS_KEY
                        AWS Access Key (can also be specified using
                        AWS_ACCESS_KEY environment variable)
  -aws-secret-key AWS_SECRET_KEY
                        AWS Secret Key (can also be specified using
                        AWS_SECRET_KEY environment variable)
  --email-password EMAIL_PASSWORD
                        Gmail Email password (can also be specified using
                        EMAIL_PASSWORD environment variable)
  --email-from EMAIL_FROM
                        From email address (can also be specified using
                        EMAIL_FROM environment variable)
  --email-to EMAIL_TO   Comma seperated list of email recipients (can also be
                        specified using EMAIL_TO environment variable)
  --reports REPORTS     Comma seperated list from from the following -
                        Console, Email (can also be specified using REPORTS
                        environment variable)
```

To report to the console

```
python aws_reporter.py --aws-secret-key {REDACTED} --aws-access-key {REDACTED}
```

To send an email (only gmail supported) plus report to the console and email

```
python aws_reporter.py --aws-secret-key {REDACTED} --aws-access-key REDACTED --email-password {REDACTED} --email-from abc@abc.com --email-to one@abc.com,two@abc.com --reports Email,Console
```

Runing via docker

```
docker run --env AWS_ACCESS_KEY={REDACTED} --env AWS_SECRET_KEY={REDACTED} {IMAGE_NAME}
```
