###############
# BUILD IMAGE #
###############
FROM python:3.8.2-slim-buster AS build

# set root user
USER root

# virtualenv
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# add and install requirements
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

#################
# RUNTIME IMAGE #
#################
FROM python:3.8.2-slim-buster AS runtime

# create app directory
RUN mkdir -p /usr/src/app

# copy from build image
COPY --from=build /opt/venv /opt/venv

# set working directory
WORKDIR /usr/src/app

# disables lag in stdout/stderr output
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Path
ENV PATH="/opt/venv/bin:$PATH"

# Run streamlit
CMD streamlit run project/app.py
