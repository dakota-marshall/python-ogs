# OGS Python Library


[![pipeline status](https://gitlab.com/dakota.marshall/ogs-python/badges/prod/pipeline.svg)](https://gitlab.com/dakota.marshall/ogs-python/-/commits/prod)  [![Latest Release](https://gitlab.com/dakota.marshall/ogs-python/-/badges/release.svg)](https://gitlab.com/dakota.marshall/ogs-python/-/releases) [![PyPI version](https://badge.fury.io/py/ogsapi.svg)](https://badge.fury.io/py/ogsapi) 

## Summary

An API wrapper written in python for the Online-Go Server's (OGS) REST API and Realtime (SocketIO) API

**NOTE** While the project is mostly functional, this is still a work in progress, and is not yet ready for production use.

## Documentation

The documentation is built automatically using mkdocs and mkdocstrings.

Read the documentation here for more info: https://ogs-python.dakotamarshall.net/

## Install

### Pip Package

```bash
python3 -m pip install ogsapi
```

### Manual

Installing the specific versions in `requirements.txt` is **REQUIRED**, the OGS API does not support newer versions, and these versions of socketio and engineio are tested to be compatible with each other.

```bash
pip3 install -r requirements.txt
```

If you install the wrong version by accident, you *must* uninstall and re-install.

```bash
pip3 uninstall python-engineio python-socketio
pip3 install -r requirements.txt
```
## Usage

```python
from ogsapi.client import OGSClient

ogs = OGSClient('your_client_id', 'your_client_secret', 'your_username', 'your_password')
```
This will authenticate you to OGS using your API credentials, and connect you to the Realtime API Socket. You can now call the usable functions.

## Implemented API Functions
*NOTE* All usernames are case sensitive

Look at the [documentation](https://ogs-python.dakotamarshall.net/api/) to see what methods are available under `OGSClient` and `OGSSocket` / `OGSGame`

See the [checklist](https://ogs-python.dakotamarshall.net/checklist) for a rough list of what is left to be implemented