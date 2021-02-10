FROM python:3.9.1-buster

# Set working directory
WORKDIR /app

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install pip requirements
COPY ./config/requirements.txt /app/config/requirements.txt
RUN python -m pip install -r /app/config/requirements.txt
COPY ./config/requirements-dev.txt /app/config/requirements-dev.txt
RUN python -m pip install -r /app/config/requirements-dev.txt

# install python's interactive shells
RUN python -m pip install ipython bpython
# RUN pip install -U "celery[redis]"

COPY ./ /app

# Add group and user
RUN groupadd -g 1000 appuser
RUN useradd -u 1000 -ms /bin/bash -g appuser appuser

# Add permission to appuser (non-root) for access to the /app directory
RUN chown -R appuser:appuser /app

# switch to a appuser
USER appuser
