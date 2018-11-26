# dbrepo
Database Repository Management Tool

**A tool for managing a metainformation for databases

DbRepo is a application developed with Flask.

## Installation

```
git clone https://github.com/tmas0/dbrepo.git

cd dbrepo

python3 -m venv venv

virtualenv venv

source venv/bin/activate

pip install -r requeriments.txt
```

**Configuration

```
export DATABASE_URL=postgresql://user:password@host/db
export PGMB_EDBUSER=user
```

Install and execute gunicorn.

***Example of dbrepo service

```
vi /lib/systemd/system/dbrepo.service
```

And put these:
```
[Unit]
Description=DbRepo
After=network.target

[Service]
User=dbrepo
WorkingDirectory=/home/dbrepo/dbrepo
Environment="PATH=/home/dbrepo/dbrepo/venv/bin"
EnvironmentFile=/home/dbrepo/env
Restart=on-failure
ExecStart=/usr/local/bin/gunicorn -b localhost:8000 -w 4 dbrepo:app
RestartSec=10s

[Install]
WantedBy=multi-user.target
```