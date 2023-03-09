# pg-backup-api
A server that provides an HTTP API to interact with Postgres backups

## Installation
tbd

## Running the Flask app

### Manually

Install `pg-backup-api` and change to the Barman user, then run

`pg-backup-api serve` 

or `pg-backup-api serve --port N` if you want to use a different port than the default (which is 7480).

### Service

If running from a local source directory, copy `pg-backup-api/packaging/pg-backup-api.service` to `/etc/systemd/system/`. If you've installed
pg-backup-api as a package, installation will put the service file in the right place for you.

Then run
`systemctl enable pg-backup-api`
`systemctl start pg-backup-api`

to run it.

### Verify the app

`pg-backup-api status` returns "OK" if the app is up and running.

## Testing
tbd

## Releasing

Follow the process documented in the [pg-backup-api-packaging repo](https://github.com/EnterpriseDB/pg-backup-api-packaging).
