# pg-backup-api release notes

© Copyright EnterpriseDB UK Limited 2021-2022 - All rights reserved.

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

