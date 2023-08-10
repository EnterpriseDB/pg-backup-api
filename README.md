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

The above comand will start up the REST API as a development server. If you
want to run the REST API as an WSGI application, use the approach described in
the `Service` section.

### Service

If you intend to run `pg-backup-api` from a local source directory, then you
need to set up the `pg-backup-api` service. You need to copy a couple files
from the [pg-backup-api-packaging repo](https://github.com/EnterpriseDB/pg-backup-api-packaging):

1. Copy `packaging/etc/systemd/system/pg-backup-api.service.in` to
   `/etc/systemd/system/pg-backup-api.service`
2. Copy `packaging/etc/pg-backup-api-config.py` to `/etc/pg-backup-api-config.py`

If you have installed the `pg-backup-api` package, the package installation puts
the service and configuration files in the right place for you.

Once the systemd services are in the right place, run the following command to
enable `pg-backup-api` startup on machine boot, and immediatelly start it:

```bash
systemctl enable pg-backup-api --now
```

**Note:** by default the `pg-backup-api` service runs on port `7480`. You can
override that behavior by changing the port in `/etc/pg-backup-api-config.py`.

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
