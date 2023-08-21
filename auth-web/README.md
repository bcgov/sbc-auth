[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](../LICENSE)
[![Lifecycle:Stable](https://img.shields.io/badge/Lifecycle-Stable-97ca00)](<Redirect-URL>)
[![codecov](https://codecov.io/gh/bcgov/sbc-auth/branch/development/graph/badge.svg?flag=authweb)](https://codecov.io/gh/bcgov/sbc-auth/tree/development/auth-web)
![Auth Web DEV CD](https://github.com/bcgov/sbc-auth/workflows/Auth%20Web%20DEV%20CD/badge.svg)
![Auth Web TEST CD](https://github.com/bcgov/sbc-auth/workflows/Auth%20Web%20TEST%20CD/badge.svg)

# AUTH WEB (auth-web)

BC Registries authentication and authorization interface.

## Prerequisites
- Node.js (> v16.15.x)
- [VITE v4.4.9](https://vitejs.dev/)

## Development setup

- Fork and checkout this repository in to your local.
- Open terminal or cmd.
- Go to the **auth-web** folder (`cd /auth-web`)
- install the dependencies by running the command: **`npm install`**

## Running the environment in development mode
Run the following command on the root(auth-web) folder:
```
npm run dev
```

### Run your tests
Run the following command on the root folder:
```
npm run test
```

### Run and check lint
Run the following command on the root folder:
```
npm run lint
```

### Run your end-to-end tests
Run the following command on the root folder:
```
npm run test:e2e
```

### Run your unit tests
Run the following command on the root folder:
```
npm run test:unit
```
---
## For Production Build
Run the following command in the root folder:

```
npm run build
```
Once the build is successful, check the **/dist** folder for the build files

---
## Customize webpack configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

----

## Openshift Environment
View the document [here](/docs/build-deploy.md#webui-runtime)
