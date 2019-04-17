[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)


 - #### Common
    - [ ] Proper naming conventions followed on variables, classes, definitions etc.
    - [ ] Proper logging levels are used in the code 
 - #### REST 
    - [ ] Endpoints follows agreed pattern and organized around resources
    - [ ] Conform to http semantics
    - [ ] Proper filtering and pagination is provided for large amounts of data
 - #### Code structure
    - [ ] Routes is used for request payload processing, validations, response codes, messages etc.
    - [ ] Service is used for business logic, 3rd party communication management. Maintains proper folder structure.
    - [ ] Model is used for database models.
    - [ ] Schemas is used for json schema
    - [ ] Util contains commonly used utility functions, constants
 - #### Test Cases
    - [ ] Unit test cases with happy and sad path for service, model (?) layers
    - [ ] Endpoints test cases with happy and sad path for routes
    - [ ] Mocking of services (mainly 3rd party dependencies) provided if applicable
    - [ ] Postman collection tests provided for endpoints with happy path
 - #### Code Quality
    - [ ] Proper code coverage for all the layers (percentage 80, 90 ?)
    - [ ] Linting
- #### DB Migrations
    - [ ] Alembic is used to manage database migration. Refer https://github.com/bcgov/namex/blob/master/docs/database.md


