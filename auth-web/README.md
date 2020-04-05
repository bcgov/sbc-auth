# AUTH WEB (auth-web)

BC Registries authentication and authorization interface.

## Prerequisites
- Node.js (> v13.6.x)
- [Vue Cli](https://cli.vuejs.org/)

## Development setup

- Fork and checkout this repository in to your local.
- Open terminal or cmd.
- Go to the **auth-web** folder (`cd /auth-web`)
- install the dependencies by running the command: **`npm install`**

## Running the environment in development mode
Run the following command on the root(auth-web) folder:
```
npm run serve
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
Once the build is successful, check the **/dist** folder for the build files.

---
## Customize webpack configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

----

## Openshift Environment
View the document [here](/docs/build-deploy.md#webui-runtime)
