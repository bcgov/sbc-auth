# auth-web

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### How to Get environment related configs 

process.env doesnt work well with openshift since application is deployed in caddy as a static bundle.
So the work around is to have a config map in open shift and mount it to caddy .
The json is later read and saved to session storage.

### How to do axios call

Do not use the full url's since Caddy is doing the redirection. 
Caddy knows the full url of services .

[Axio calls will look like](/src/services/login.services.ts)


[Caddy rules](/openshift/Caddyfile)

 

### Compiles and minifies for production
```
npm run build
```

### Run your tests
```
npm run test
```

### Lints and fixes files
```
npm run lint
```

### Run your end-to-end tests
```
npm run test:e2e
```

### Run your unit tests
```
npm run test:unit
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
