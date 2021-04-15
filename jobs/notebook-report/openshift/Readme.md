# buildconfig
oc process -f openshift/templates/bc.yaml -o yaml | oc apply -f - -n 6e0e49-tools
# cronjob
oc process -f openshift/templates/cronjob.yaml -o yaml | oc apply -f - -n 6e0e49-dev
oc process -f openshift/templates/cronjob.yaml -p TAG=test -o yaml | oc apply -f - -n 6e0e49-test
oc process -f openshift/templates/cronjob.yaml -p TAG=prod -o yaml | oc apply -f - -n 6e0e49-prod

