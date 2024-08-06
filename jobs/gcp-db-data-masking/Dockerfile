FROM google/cloud-sdk:latest

USER root

# Create working directory
RUN mkdir /opt/app-root && chmod 755 /opt/app-root
WORKDIR /opt/app-root

COPY jobs/gcp-db-data-masking/ .

EXPOSE 8080

CMD [ "/bin/bash", "run.sh" ]
