#!/bin/bash

# dev
gsutil cors set gcs-auth-accounts-dev-cors.json gs://auth-accounts-dev
gsutil cors get gs://auth-accounts-dev

gsutil cors set gcs-auth-static-resources-dev-cors.json gs://auth-static-resources-dev
gsutil cors get gs://auth-static-resources-dev

# test
gsutil cors set gcs-auth-accounts-test-cors.json gs://auth-accounts-test
gsutil cors get gs://auth-accounts-test

gsutil cors set gcs-auth-static-resources-test-cors.json gs://auth-static-resources-test
gsutil cors get gs://auth-static-resources-test

# prod
gsutil cors set gcs-auth-accounts-prod-cors.json gs://auth-accounts-prod
gsutil cors get gs://auth-accounts-prod

gsutil cors set gcs-auth-static-resources-prod-cors.json gs://auth-static-resources-prod
gsutil cors get gs://auth-static-resources-prod

# sandbox
gsutil cors set gcs-auth-accounts-sandbox-cors.json gs://auth-accounts-sandbox
gsutil cors get gs://auth-accounts-sandbox
