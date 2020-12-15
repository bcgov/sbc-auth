#!/bin/sh
docker-compose up -d

echo "waiting for keycloak start..."

until $(curl --output /dev/null --silent --head --fail http://localhost:8081/auth/realms/demo); do
    printf '.';
    sleep 5;
done

