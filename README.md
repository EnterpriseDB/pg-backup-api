# pg-backup-api

A server that provides an REST API to interact with Postgres backups.

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

When running `pg-backup-api` as a service we set up the application to run
through `gunicorn`. Please install `gunicorn` before proceeding if it is missing
in your environment.

If you intend to run `pg-backup-api` from a local source directory, then you
need to set up the `pg-backup-api` service. Follow these steps:

1. Create the gunicorn configuration file at `/etc/pg-backup-api-config.py` with
the following content:

```ini
#Log and error access file
accesslog = "/var/log/barman/barman-api-access.log"
errorlog = "/var/log/barman/barman-api-error.log"

timeout = 60                    # seconds

bind = "localhost:7480"         # By default the service binds on localhost only
                                # If you need to change it and listen to in all interfaces,
                                # you could set "bind 0.0.0.0:7480"
```

2. Create the systemd unit at `/etc/systemd/system/pg-backup-api.service` with
   the following content:

```ini
[Unit]
Description=Postgres Backup API

[Service]
Type=simple
User=barman
Group=barman
ExecStart=/usr/bin/gunicorn -c /etc/pg-backup-api-config.py pg_backup_api.app
Restart=always

[Install]
WantedBy=multi-user.target
```

If you have installed the `pg-backup-api` package, the package installation puts
the service and configuration files in the right place for you.

Once the systemd services are in place, run the following command to enable
`pg-backup-api` startup on machine boot, and immediatelly start it:

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
