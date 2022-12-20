# pg-backup-api release notes

© Copyright EnterpriseDB UK Limited 2021-2022 - All rights reserved.

## 1.1.0 (2023-01-27)

### Notable changes

- Adding two new endpoints to perform recoveries with barman.

- The baseurl is /servers/<server_name>/operations and it can be used to
  display all operations and to create new ones. An <operation_id> can be added
  to get the status of an operation created as in
  /servers/<server_name>/operations/<operation_id>

- `recovery` as option was added to the command line in order to run barman
  recovery `pg-backup-api recovery --server-name SERVER_NAME --operation-id ID`

## 1.0.0 (2022-10-13)

### Notable changes

- Support for running as a WSGI application under Gunicorn.

### Minor changes

- Changes to the Barman configuration are now included in the /diagnose output
  without requiring a restart of pg-backup-api.

- Barman configuration options added in Barman 3.1.0 are now included in the
  /diagnose output.

- Fields relating to pgespresso are removed from the /diagnose output.

### Bugfixes

- Fix the monotonic increase of memory usage caused by every /diagnose response
  being retained in the Barman output writer.

- Various schema fixes.

## 0.2.0 (2022-06-23)

### Notable changes

- Support for Barman 3.0.0

## 0.1.0 (2022-03-31)

### Notable changes

- Initial release

