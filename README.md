# pg-backup-api

A server that provides an REST API to interact with Barman.

## Installation

This tool is supposed to be installed in the same server where Barman is already
set up and running.

### Package installation

Configure EDB repos 2.0 and install the package `pg-backup-api` using your
package manager.

### Installation from source code

1. Clone this repository, e.g.:

```bash
git clone https://github.com/EnterpriseDB/pg-backup-api.git
```

2. Install `pg-backup-api` and its requirements:

```bash
cd pg-backup-api/pg_backup_api
sudo python3 setup.py install
```

**Note:** `pg_config` application should be in your `PATH` because `psycopg2` is
in the dependency tree. Besides that, you also need the `libpq` C library in
your system (`libpq-dev` package on Debian based, or `libpq-devel` package on
RedHat based).

## Running the Flask app

### Manually

As Barman user run:

```bash
pg-backup-api serve
```

**Note:** by default `pg-backup-api` runs on port `7480`. You can override that
behavior by passing `--port N` to `serve` command, `N` being the port to listen
on.

### Service

If you are running `pg-backup-api` from a local source directory, copy
`pg-backup-api/packaging/pg-backup-api.service` to `/etc/systemd/system/`. If
you've installed `pg-backup-api` as a package, installation puts the service
file in the right place for you.

Once the systemd services are in the right place, run the following command to
enable `pg-backup-api` startup on machine boot, and immediatelly start it:

```bash
systemctl enable pg-backup-api --now
```

### Verify the app

You can check if the application is up and running by executing this command:

```bash
pg-backup-api status
```

The command returns `"OK"` if the app is up and running.

## Testing

You can run unit tests through `pytest`:

```bash
cd pg-backup-api/pg_backup_api
python3 -m pytest
```

**Note:** install `pytest` Python module if you don't have it yet in your
environment.

## Releasing

Follow the process documented in the
[pg-backup-api-packaging repo](https://github.com/EnterpriseDB/pg-backup-api-packaging).
