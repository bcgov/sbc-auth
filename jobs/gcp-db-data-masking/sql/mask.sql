CREATE EXTENSION IF NOT EXISTS anon CASCADE;
SELECT anon.init();

SECURITY LABEL FOR anon ON COLUMN users.last_name
  IS 'MASKED WITH FUNCTION anon.fake_last_name()';

SECURITY LABEL FOR anon ON COLUMN users.first_name
  IS 'MASKED WITH FUNCTION anon.fake_first_name()';

SECURITY LABEL FOR anon ON COLUMN contacts.phone
  IS 'MASKED WITH FUNCTION anon.random_phone()';

SECURITY LABEL FOR anon ON COLUMN contacts.email
  IS 'MASKED WITH FUNCTION anon.fake_email()';

SELECT anon.anonymize_database();
