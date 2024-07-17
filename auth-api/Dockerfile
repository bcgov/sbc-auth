FROM python:3.8.5-buster

ARG VCS_REF="missing"
ARG BUILD_DATE="missing"

ENV VCS_REF=${VCS_REF}
ENV BUILD_DATE=${BUILD_DATE}

LABEL org.label-schema.vcs-ref=${VCS_REF} \
      org.label-schema.build-date=${BUILD_DATE}

USER root

# Create working directory
RUN mkdir /opt/app-root && chmod 755 /opt/app-root
WORKDIR /opt/app-root

# Install dependencies and tools
RUN apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
       bash \
       build-essential \
       curl \
       git \
       libpq-dev \
    # Clean up cache
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:${PATH}"

# Copy only requirements to cache them in docker layer
COPY ./pyproject.toml ./poetry.lock /opt/app-root/

# Project initialization
RUN poetry version \
    && poetry run pip install -U pip \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the application code
COPY . .

# Install any remaining dependencies (if needed)
RUN poetry install

# Set Python path
ENV PYTHONPATH=/opt/app-root/src

# Running as non-root user
USER 1001

ENTRYPOINT ["bash", "docker-entrypoint.sh"]
