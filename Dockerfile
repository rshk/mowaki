# syntax=docker/dockerfile:1.0.0-experimental

ARG PYTHON_VERSION=3.7
ARG NODE_VERSION=10


FROM python:${PYTHON_VERSION}-alpine AS mowaki-app-apiserver-dev

# TODO: run system upgrade as well?

# Install system dependencies
RUN apk add --no-cache --update build-base libffi-dev postgresql-dev

# Create non-privileged user to run the app
RUN adduser --home /home/adduser --disabled-password appuser

# Install Python dependencies
RUN pip install pipenv
RUN mkdir -p /src /src/api /src/reqs
COPY Pipfile Pipfile.lock /src/reqs/
WORKDIR /src/reqs
RUN pipenv install --system --dev

WORKDIR /src/api
EXPOSE 5000/tcp
USER appuser
CMD python -m app run --host 0.0.0.0 --port 5000 --debugger --reload


FROM node:${NODE_VERSION}-alpine AS mowaki-app-webserver-dev

# Create non-privileged user to run the app
RUN adduser --home /home/adduser --disabled-password appuser

# Install nodejs dependencies
RUN mkdir -p /src /src/web
COPY ./web/package.json ./web/package-lock.json /src/web/
VOLUME /src/web/node_modules
WORKDIR /src/web
ENV NODE_ENV=development
RUN npm install .

# Development server
WORKDIR /src/web
# ENV NPM_CONFIG_PREFIX=/src/reqs/node_modules
# ENV NODE_PATH=/src/reqs/node_modules
ENV SERVER_HOST=0.0.0.0
ENV SERVER_PORT=8000
EXPOSE 8000/tcp
USER appuser
CMD npm run start
