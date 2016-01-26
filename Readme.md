aws-usage-reporter
------------------

Builds a report of our current aws instances and collates a report with their accrued cost.

The report can either be sent to the console and or via email.

Install dependancies

```
pip install -r requirements.txt
```

```
usage: aws_reporter.py [-h] -aws-access-key AWS_ACCESS_KEY -aws-secret-key
                       AWS_SECRET_KEY [--email-password EMAIL_PASSWORD]
                       [--email-from EMAIL_FROM] [--email-to EMAIL_TO]
                       [--reports REPORTS]

Collates a report of running AWS instances

optional arguments:
  -h, --help            show this help message and exit
  -aws-access-key AWS_ACCESS_KEY
  -aws-secret-key AWS_SECRET_KEY
  --email-password EMAIL_PASSWORD
  --email-from EMAIL_FROM
  --email-to EMAIL_TO   Comma seperated list of email recipients
  --reports REPORTS     Comma seperated list frawn from the following -
                        Console, Email
```


To report to the console

```
python aws_reporter.py --aws-secret-key {REDACTED} --aws-access-key {REDACTED}
```

To send an email (only gmail supported) plus report to the console and email

```
python aws_reporter.py --aws-secret-key {REDACTED} --aws-access-key REDACTED --email-password {REDACTED} --email-from abc@abc.com --email-to one@abc.com,two@abc.com --reports Email,Console
```
