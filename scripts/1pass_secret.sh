#!/bin/bash


# =================================================================================================================
# Usage:
# -----------------------------------------------------------------------------------------------------------------
usage() {
  cat <<-EOF
  A helper script to get the secrcts from 1password' vault and set it to openshift secret.
  Usage: ./1pass_secret.sh [-h -d <subdomainName> -u <accountName>]
                             -k <secretKey>
                             -p <masterPassword>
                             -e <environment>
                             -v <vaultDetails>
                             -a <appName>

  OPTIONS:
  ========
    -h prints the usage for the script.
    -a Openshift application name, for example: auth-api-dev
    -d The subdomain name of the 1password account, default is registries.1password.ca.
    -u The account name of the 1password account, default is bcregistries.devops@gmail.com.
    -k The secret key of the 1password account.
    -p The master password of the 1password account.
    -e The environment of the vault, for example pytest/dev/test/prod.
    -v A list of vault and application name of the 1password account, for example:
       [
          {
              "vault": "shared",
              "application": [
                  "keycloak",
                  "email"
              ]
          },
          {
              "vault": "relationship",
              "application": [
                  "auth-api",
                  "notify-api",
                  "status-api"
              ]
          }
      ]

EOF
exit
}

# -----------------------------------------------------------------------------------------------------------------
# Initialization:
# -----------------------------------------------------------------------------------------------------------------
while getopts h:a:d:u:k:p:v:e: FLAG; do
  case $FLAG in
    h ) usage ;;
    a ) APP_NAME=$OPTARG ;;
    d ) DOMAIN_NAME=$OPTARG ;;
    u ) USERNAME=$OPTARG ;;
    k ) SECRET_KEY=$OPTARG ;;
    p ) MASTER_PASSWORD=$OPTARG ;;
    v ) VAULT=$OPTARG ;;
    e ) ENVIRONMENT=$OPTARG ;;
    \? ) #unrecognized option - show help
      echo -e \\n"Invalid script option: -${OPTARG}"\\n
      usage
      ;;
  esac
done

# Shift the parameters in case there any more to be used
shift $((OPTIND-1))
# echo Remaining arguments: $@

if [ -z "${DOMAIN_NAME}" ]; then
  DOMAIN_NAME=registries.1password.ca
fi

if [ -z "${USERNAME}" ]; then
  USERNAME=bcregistries.devops@gmail.com
fi

if [ -z "${APP_NAME}" ] || [ -z "${SECRET_KEY}" ] || [ -z "${MASTER_PASSWORD}" ] || [ -z "${VAULT}" ]  ||  [ -z "${ENVIRONMENT}" ]; then
  echo -e \\n"Missing parameters - secret key, master password, vault or environment"\\n
  usage
fi

# Login to 1Password../s
# Assumes you have installed the OP CLI and performed the initial configuration
# For more details see https://support.1password.com/command-line-getting-started/
eval $(echo "${MASTER_PASSWORD}" | op signin ${DOMAIN_NAME} ${USERNAME} ${SECRET_KEY})

# create application secrets
oc create secret generic ${APP_NAME}-secret > /dev/null 2>&1 &

for vault_name in $(echo "${VAULT}" | jq -r '.[] | @base64' ); do
  _jq() {
     echo ${vault_name} | base64 --decode | jq -r ${1}
  }
  for application_name in $(echo "$(_jq '.application')" | jq -r '.[]| @base64' ); do
    _jq_app() {
      echo ${application_name} | base64 --decode
    }

    # My setup uses a 1Password type of 'Password' and stores all records within a
    # single section. The label is the key, and the value is the value.
    ev=`op get item --vault=$(_jq .vault) ${ENVIRONMENT}`

    # Convert to base64 for multi-line secrets.
    # The schema for the 1Password type uses t as the label, and v as the value.
    # Set secrets to secret in Openshift
    for row in $(echo ${ev} | jq -r -c '.details.sections[] | select(.title=='\"$(_jq_app)\"') | .fields[] | @base64'); do
        _envvars() {
            echo ${row} | base64 --decode | jq -r ${1}
        }

        # Set secret key and value from 1password
        oc get secret ${APP_NAME}-secret -o json \
          | jq ". * $(oc create secret generic ${APP_NAME}-secret --from-literal=$(_envvars '.t')=$(_envvars '.v') --dry-run -o json)" \
          | oc apply -f -

    done
  done
done

# Set environment variable of deployment config
oc set env dc/${APP_NAME} --overwrite --from=secret/${APP_NAME}-secret --containers=${APP_NAME} ENV-  > /dev/null 2>&1 &
