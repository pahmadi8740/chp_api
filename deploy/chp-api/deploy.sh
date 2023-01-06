#!/bin/bash

# variables 
projectName="chp-api"
namespace="chp"
# replace place_holder with values from env var
# env var's key needs to be the same as the place_holder
toReplace=('BUILD_VERSION')

# export .env values to env vars
# export $(egrep -v '^#' .env)

# printenv

# replace variables in values.yaml with env vars

for item in "${toReplace[@]}";
do
  sed -i.bak \
      -e "s/${item}/${!item}/g" \
      values.yaml
  rm values.yaml.bak
done

sed -i.bak \
    -e "s/SECRET_KEY_VALUE/$SECRET_KEY/g" \
    -e "s/ENGINE_VALUE/$ENGINE/g;s/DBNAME_VALUE/$DBNAME/g" \
    -e "s/USERNAME_VALUE/$USERNAME/g;s/PASSWORD_VALUE/$PASSWORD/g" \
    -e "s/HOST_VALUE/$HOST/g;s/PORT_VALUE/$PORT/g" \
    configs/settings.py
rm configs/settings.py.bak 

kubectl apply -f namespace.yaml

# deploy helm chart
helm -n ${namespace} upgrade --install ${projectName} -f values-ncats.yaml ./