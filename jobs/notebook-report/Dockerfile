FROM python:3.12.2
USER root

ARG VCS_REF="missing"
ARG BUILD_DATE="missing"

ENV VCS_REF=${VCS_REF}
ENV BUILD_DATE=${BUILD_DATE}

LABEL org.label-schema.vcs-ref=${VCS_REF} \
    org.label-schema.build-date=${BUILD_DATE}

USER root

ARG APP_ENV \
    # Needed for fixing permissions of files created by Docker:
    UID=1000 \
    GID=1000

ENV APP_ENV=${APP_ENV} \
    # python:
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PYTHONDONTWRITEBYTECODE=1 \
    # pip:
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_ROOT_USER_ACTION=ignore \
    # poetry:
    POETRY_VERSION=1.3.2 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'

SHELL ["/bin/bash", "-eo", "pipefail", "-c"]

# Install system dependencies
RUN apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    bash \
    brotli \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
    wait-for-it \
    && curl -sSL 'https://install.python-poetry.org' | python - \
    && poetry --version \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Setup the application directory
WORKDIR /code
RUN groupadd -g "${GID}" -r web \
    && useradd -d '/code' -g web -l -r -u "${UID}" web \
    && chown web:web -R '/code'

# Copy the application code and scripts
COPY --chown=web:web . /code
RUN chmod 755 /code/run.sh

# Echo the current Poetry configuration
RUN echo "Checking Poetry configurations..." \
    && poetry config --list

# Initialize project and install dependencies
RUN --mount=type=cache,target="$POETRY_CACHE_DIR" \
    echo "Installing dependencies under APP_ENV=$APP_ENV..." \
    && poetry run pip install -U pip \
    && poetry install $(if [ -z ${APP_ENV+x} ] || [ "$APP_ENV" = 'production' ]; then echo '--only main'; fi) \
    --no-interaction --no-ansi

# Switch to the non-root user
USER web

EXPOSE 8080

CMD [ "/bin/sh", "/code/run.sh" ]