aws-tools
---------

Collection of helpers developed to devops the AWS

installation
------------

Install dependancies

```
pip install -r requirements.txt
```

aws-ami-copier
--------------

Copy ami images accross regions.

```
usage: aws_ami_copier.py [-h] -aws-access-key AWS_ACCESS_KEY -aws-secret-key
                         AWS_SECRET_KEY -ami AMI -image_type IMAGE_TYPE
                         -region REGION

Tool to copy an ami image to all of the regions.

optional arguments:
  -h, --help            show this help message and exit
  -aws-access-key AWS_ACCESS_KEY
                        AWS Access Key (or AWS_ACCESS_KEY environment
                        variable)
  -aws-secret-key AWS_SECRET_KEY
                        AWS Secret Key (or AWS_SECRET_KEY environment
                        variable)
  -ami AMI              AMI to copy (or AMI environment variable)
  -image_type IMAGE_TYPE
                        Image type e.g. centos or ubuntu (or IMAGE_TYPE
                        environment variable)
  -region REGION        Region to copy from (or REGION environment variable)

```

aws-usage-reporter
------------------

Build a report of your current aws instances along side their accrued cost.

The report can either be sent to the console and or via email.



```
usage: aws_reporter.py [-h] -aws-access-key AWS_ACCESS_KEY -aws-secret-key
                       AWS_SECRET_KEY [--email-password EMAIL_PASSWORD]
                       [--email-from EMAIL_FROM] [--email-to EMAIL_TO]
                       [--reports REPORTS]

Collates a report of running AWS instances

optional arguments:
  -h, --help            show this help message and exit
  -aws-access-key AWS_ACCESS_KEY
                        AWS Access Key (or AWS_ACCESS_KEY environment
                        variable)
  -aws-secret-key AWS_SECRET_KEY
                        AWS Secret Key (or AWS_SECRET_KEY environment
                        variable)
  --email-password EMAIL_PASSWORD
                        Gmail Email password (or EMAIL_PASSWORD environment
                        variable)
  --email-from EMAIL_FROM
                        From email address (or EMAIL_FROM environment
                        variable)
  --email-to EMAIL_TO   Comma seperated email recipients (or EMAIL_TO
                        environment variable)
  --reports REPORTS     Comma seperated list from from - Console, Email (or
                        REPORTS environment variable)
```

To report to the console

```
python aws_reporter.py --aws-secret-key {REDACTED} --aws-access-key {REDACTED}
```

To send an email (only Gmail supported) plus report to the console and email

```
python aws_reporter.py --aws-secret-key {REDACTED} --aws-access-key REDACTED --email-password {REDACTED} --email-from abc@abc.com --email-to one@abc.com,two@abc.com --reports Email,Console
```

Runing via docker

```
docker run --env AWS_ACCESS_KEY={REDACTED} --env AWS_SECRET_KEY={REDACTED} {IMAGE_NAME}
```
