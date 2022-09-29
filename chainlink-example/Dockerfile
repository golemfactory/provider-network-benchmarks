FROM python:3.9-slim
VOLUME /golem/in /golem/out
COPY chainlink_request.py /golem/run/chainlink_request.py
RUN chmod +x /golem/run/*
ENTRYPOINT ["sh"]
