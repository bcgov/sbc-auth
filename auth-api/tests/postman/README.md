# Auth-api postman test

## Test setup

```npm
npm install newman
```

## Test run help

```newman
newman run -h
```

## Test run

You should put the environment json in your own path.

```newman
newman run auth-api.postman_collection.json -e ${path}/auth-api.postman_environment.json -d auth-api.passcode.postman_data.json
```
