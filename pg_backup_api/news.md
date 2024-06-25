# pg-backup-api release notes

© Copyright EnterpriseDB UK Limited 2021-2024 - All rights reserved.

## 2.1.1 (2024-06-29)

### Buxfixes

- Functions/methods signatures updates to fix regression with Barman <= 3.9

## 2.1.0 (2024-01-25)

### Notable changes

- Barman now supports changes in the configuration whilst it's running. This
  pg-backup-api release adds the required endpoints to trigger that switch
  when requested.

## 2.0.0 (2023-10-03)

### Notable changes

- BREAKING: The `/servers/server_name/operations` endpoint now returns a list
  of dictionaries containing keys `id` and `type` instead of the list of
  operation IDs which was returned by previous versions.

- BREAKING: The `/servers/server_name/operations/operation_id` endpoint now
  returns `operation_id` and `status` instead of `recovery_id` and `status`
  which were returned by previous versions.

### Minor changes

- Improved help strings and documentation for command line options.

### Bugfixes

- Allow pg-backup-api subcommands such as `status` to work regardless of
  whether pg-backup-api was installed from source or from packages.

- Fix exit code for `pg-backup-api status` so that it is zero if the command
  completes successfully and non-zero otherwise.

- Fix the `Backup <BACKUP> does not exist` error message so it includes the ID
  of the requested backup.

## 1.3.0 (2023-07-13)

### Notable changes

- Ability to parse and recognise Barman shortcuts like `latest` or `oldest`.

- Access to barman-api.log is now only required when running under a WSGI
  server. This means pg-backup-api commands like status will no longer fail
  if they are executed by a user that cannot access barman-api.log.`

## 1.2.0 (2023-03-29)

### Notable changes

- Drop support for python 2.7. The earliest python version supported is now
  3.6.

## 1.1.1 (2023-03-01)

### Notable changes

- Displaying the right message when pg-backup-api received no args.

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

