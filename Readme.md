aws-usage-reporter
------------------

Builds a report of out current aws instance and collates a report with their accrued usage.

The report can either be sent to the console and or via email.

To report to the console

```
python aws_reporter.py --aws-secret-key {REDACTED} --aws-access-key {REDACTED}
```

To send an email (only gmail supported) plus report to the console and email

```
python aws_reporter.py --aws-secret-key {REDACTED} --aws-access-key REDACTED --email-password {REDACTED} --email-from abc@abc.com --email-to one@abc.com,two@abc.com --reports Email,Console
```
