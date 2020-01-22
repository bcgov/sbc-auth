#!/bin/bash

# Login to 1Password.
# Assumes you have installed the OP CLI and performed the initial configuration
# For more details see https://support.1password.com/command-line-getting-started/
eval $(echo "$3" | op signin registries.1password.ca $1 $2)

# My setup uses a 1Password type of 'Password' and stores all records within a
# single section. The label is the key, and the value is the value.
ev=`op get item --vault=relationship $4`
app=Auth-api

# Convert to base64 for multi-line secrets.
# The schema for the 1Password type 'Password' uses t as the label, and v as the value.
for row in $(echo ${ev} | jq -r -c '.details.sections[] | select(.title=='\"${app}\"') | .fields[] | @base64'); do
    _envvars() {
        echo ${row} | base64 --decode | jq -r ${1}
    }
    echo "Setting environment variable $(_envvars '.t')"
    export $(echo "$(_envvars '.t')=$(_envvars '.v')")
done

eval $(echo env)
