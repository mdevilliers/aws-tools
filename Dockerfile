FROM raphiz/ubuntu-cron

RUN apt-get update && \
	apt-get install -qy python-pip && \
	apt-get clean && \
 	rm -rf /var/lib/apt/lists/*

ADD . /aws_reporter/
WORKDIR /aws_reporter

RUN pip install -r /aws_reporter/requirements.txt

ENTRYPOINT python aws_reporter.py