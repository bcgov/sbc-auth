# Passcode user import through postman

## Export data as json file(passcode.postman_data.json) from Oracle database

```sql
select corp_num,temp_password,corp_typ_cd from corporation where corp_typ_cd='CP'  and temp_password is not null;
```

## Newman setup

```npm
npm install newman
```

## Import data

You should put the environment json in your own path.

```newman
newman run passcode_user_importer.postman_collection.json -e ${path}/auth-api.postman_environment.json -d passcode.postman_data.json
```
