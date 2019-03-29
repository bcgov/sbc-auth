# Postman Collection
Postman Collection to load the passcode users to KeyCloak.

## Flow
This job will perform the following,
1. Iterate over the csv/json input file
2. Creates an access token for the request using client_credentials
3. Create User record in KeyCloak using REST API with Inc Number as the user name. Adds 2 attributes to the user profile (incNumber and source (PASSCODE))
4. Retrieves the user record
5. Updates user record with password as passcode
6. Finds the default group to add
7. Adds user under the default group

## Pre-requisites
1. Install POSTMAN 
2. Create a csv file as in the 'Passcodes.csv' or as json in the 'Passcodes.json'. Make sure the IncNumber is in small letters (KeyCloak doesn't support user name in caps)

## Running the Collection
1. Import the collection (Load_Users_To_Keycloak.json) using import option in POSTMAN
2. Import the environment (Dev KeyCloak Environment.json)
3. Open the Run window in POSTMAN collection
4. Select Environment and upload csv/json file under 'Data'
5. Click on Run...

