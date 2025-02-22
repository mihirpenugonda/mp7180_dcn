FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN groupadd -g 799 nyu && \
    useradd -r -u 999 -g nyu nyu

RUN pip install Flask

USER nyu

COPY --chown=nyu:nyu . .

CMD [ "python", "./run.py" ]