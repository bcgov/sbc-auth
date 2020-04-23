
# Registries Keycloak theme

The keycloak theme for BC Registries Keycloak service.

## Update Theme in Keycloak

1. Bilding Theme in Openshift;
    ```
    oc login xxxxxx
    oc project 1rdehl-tools
    oc new-build --name auth-keycloak-theme --binary --strategy docker
    oc start-build auth-keycloak-theme --from-dir=.
    ```
2. Restart auth-keycloak (Statful Sets) in Openshift;
