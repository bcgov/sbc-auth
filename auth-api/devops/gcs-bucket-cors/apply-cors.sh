#!/bin/bash

# dev
gcloud storage buckets update gs://auth-accounts-dev --cors-file=gcs-auth-accounts-dev-cors.json
gcloud storage buckets describe gs://auth-accounts-dev --format="default(cors_config)"

gcloud storage buckets update gs://auth-static-resources-dev --cors-file=gcs-auth-static-resources-dev-cors.json
gcloud storage buckets describe gs://auth-static-resources-dev --format="default(cors_config)"

# test
gcloud storage buckets update gs://auth-accounts-test --cors-file=gcs-auth-accounts-test-cors.json
gcloud storage buckets describe gs://auth-accounts-test --format="default(cors_config)"

gcloud storage buckets update gs://auth-static-resources-test --cors-file=gcs-auth-static-resources-test-cors.json
gcloud storage buckets describe gs://auth-static-resources-test --format="default(cors_config)"

# prod
gcloud storage buckets update gs://auth-accounts-prod --cors-file=gcs-auth-accounts-prod-cors.json
gcloud storage buckets describe gs://auth-accounts-prod --format="default(cors_config)"

gcloud storage buckets update gs://auth-static-resources-prod --cors-file=gcs-auth-static-resources-prod-cors.json
gcloud storage buckets describe gs://auth-static-resources-prod --format="default(cors_config)"

# sandbox
gcloud storage buckets update gs://auth-accounts-sandbox --cors-file=gcs-auth-accounts-sandbox-cors.json
gcloud storage buckets describe gs://auth-accounts-sandbox --format="default(cors_config)"
