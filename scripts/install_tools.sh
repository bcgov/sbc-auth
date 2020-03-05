#!/bin/bash

sudo curl -sLo /tmp/oc.tar.gz https://github.com/openshift/origin/releases/download/v3.11.0/openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit.tar.gz
sudo tar xzvf /tmp/oc.tar.gz -C /tmp/
sudo mv /tmp/openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit/oc /usr/local/bin/
sudo rm -rf /tmp/oc.tar.gz /tmp/openshift-origin-client-tools-v3.11.0-0cbc58b-linux-64bit
sudo chmod +x /usr/local/bin/oc

sudo apt install curl unzip jq --yes
sudo curl -o 1password.zip https://cache.agilebits.com/dist/1P/op/pkg/v0.8.0/op_linux_amd64_v0.8.0.zip
sudo unzip 1password.zip -d /usr/local/bin
sudo rm 1password.zip
sudo chmod +x /usr/local/bin/op
