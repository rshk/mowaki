ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION} AS base

RUN adduser --home /home/appuser --disabled-password appuser

RUN mkdir -p /app /app/src /app/venv
RUN python -m venv /app/venv
COPY --chown=appuser:appuser . /app/src/


FROM base as runtime

RUN /app/venv/bin/pip install -r /app/src/requirements.txt

ENV PATH="/app/venv/bin:${PATH}"
ENV PYTHONPATH="/app/src/"
WORKDIR /app/src/
EXPOSE 8080/tcp
USER appuser
CMD ["python", "-m", "app.webapi.server"]


FROM base AS development

RUN /app/venv/bin/pip install -r /app/src/requirements-dev.txt

ENV PATH="/app/venv/bin:${PATH}"
ENV PYTHONPATH="/app/src/"
WORKDIR /app/src/
EXPOSE 8080/tcp
USER appuser
CMD ["python", "-m", "app.webapi.server"]
