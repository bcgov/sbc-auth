#!/bin/bash


# =================================================================================================================
# Usage:
# -----------------------------------------------------------------------------------------------------------------
usage() {
  cat <<-EOF
  A helper script to get the secrcts from 1password' vault and set it to environment.
  Usage: . ./setenv_1pass.sh [-h -d <subdomainName> -u <accountName>] -k <secretKey> -p <masterPassword> -v <vaultName>
  -e <environment> -a <applicationName>
  OPTIONS:
  ========
    -d The subdomain name of the 1password account, default is registries.1password.ca.
    -u The account name of the 1password account, default is bcregistries.devops@gmail.com.
    -k The secret key of the 1password account.
    -p The master password of the 1password account.
    -v The vault name of the 1password account, for example relationship.
    -e The environment of the vault, for example dev/test/prod.
    -a The application name of the vault.
    -h prints the usage for the script
EOF
exit
}

# -----------------------------------------------------------------------------------------------------------------
# Initialization:
# -----------------------------------------------------------------------------------------------------------------
while getopts d:u:k:p:v:e:a:h FLAG; do
  case $FLAG in
    d ) DOMAIN_NAME=$OPTARG ;;
    u ) USERNAME=$OPTARG ;;
    k ) SECRET_KEY=$OPTARG ;;
    p ) MASTER_PASSWORD=$OPTARG ;;
    v ) VAULT=$OPTARG ;;
    e ) ENVIRONMENT=$OPTARG ;;
    a ) APPLICATION=$OPTARG ;;
    h ) usage ;;
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

if [ -z "${SECRET_KEY}" ] || [ -z "${MASTER_PASSWORD}" ] || [ -z "${VAULT}" ]  ||  [ -z "${ENVIRONMENT}" ]; then
  echo -e \\n"Missing parameters - secret key, master password, vault or environment"\\n
  usage
fi

# Login to 1Password.
# Assumes you have installed the OP CLI and performed the initial configuration
# For more details see https://support.1password.com/command-line-getting-started/
eval $(echo "${MASTER_PASSWORD}" | op signin ${DOMAIN_NAME} ${USERNAME} ${SECRET_KEY})

# My setup uses a 1Password type of 'Password' and stores all records within a
# single section. The label is the key, and the value is the value.
ev=`op get item --vault=${VAULT} ${ENVIRONMENT}`

# Convert to base64 for multi-line secrets.
# The schema for the 1Password type uses t as the label, and v as the value.
for row in $(echo ${ev} | jq -r -c '.details.sections[] | select(.title=='\"${APPLICATION}\"') | .fields[] | @base64'); do
    _envvars() {
        echo ${row} | base64 --decode | jq -r ${1}
    }
    echo "Setting environment variable $(_envvars '.t')"
    echo ::set-env name=$(_envvars '.t')::$(_envvars '.v')
done
