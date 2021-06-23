# TMH Registry API

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg)](https://github.com/Orfium/drf-template/)

This repository implements the API for the Tanzanian Mesh Hernia Registry.

## Getting Started

These instructions will get you a copy of the project up and running.

### Installing

A step by step series of examples that tell you how to get a development env running.

For local development, we use [Docker Compose](https://docs.docker.com/compose/).

First install the prerequisite software:

1. Install [Docker](https://hub.docker.com/search?q=&type=edition&offering=community&sort=updated_at&order=desc) and [Docker Compose](https://docs.docker.com/compose/install/)
2. Install Python 3, pip, and [pre-commit](https://pre-commit.com/)

### First time only

Create a virtual environment for this project.

If you are using [pyenv](https://github.com/pyenv/pyenv):
```
pyenv virtualenv registry-api
pyenv activate registry-api
```

Install project dependencies:
```
make dep
```


### Start Developing

Spin up the project:
```
make run
```

Run migrations (every time you update Django models):
```
make migrate
```

Run tests:
```
make test
```

Everything you need for this project is under [Makefile](./Makefile). Take a look at the commands by running `make`.

### Setting up PyCharm (Optional)

Set Up Docker([detailed guide](https://www.jetbrains.com/help/pycharm/docker.html#managing-images)):
1. Go to `File` -> `Settings` -> `Build, Execution, Deployment` -> `Docker`
2. Press the `+` button to create a Docker configuration if one does not already exist.
3. Connect to Docker Daemon with your preferred setting and make sure you see a "Connection successful" message.

Set up remote interpreter with Docker-Compose([detailed guide](https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#docker-compose-remote)):
1. Go to `File` -> `Settings` -> `Project: registry-api` -> `Python Interpreter`.
2. In the upper right corner, click the cog icon and select `Add..`.
3. In the `Configuration file` option, choose the `local.yml` file.
4. In the `Service` option, choose `tmh_registry_local_django`.
5. Click `OK`.

Set up Django Server([detailed guide](https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#run)):
1. Go to `Run` -> `Edit Configurations`.
2. Press the `+` button and choose `Django Server`.
3. Change the host to `0.0.0.0`.
4. Choose the Python Interpreter you created in the previous step.
5. Click `OK`.

# Releasing

This project follows [Semantic Versioning](https://semver.org/) for releases.

Feel free to use any commit messages you like in the PR. However, please always squash and merge the PR with commit
messages that follow the [Conventional Commits specification](https://www.conventionalcommits.org/en/v1.0.0/).

# Troubleshooting

### Permission Denied in migration files

Generating migration files with the `make migrate` command, results in files which have the `root` account as their
owner. In order to be able to run pre-commit on them and commit them, you need to change the owner to your user:

`sudo chown <your_user>:<your_user> <migration_file>`
