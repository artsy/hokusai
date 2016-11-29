hokusai
-------

Artsy Docker Development Toolkit

## Requirements

1) Docker via either:
  - Docker for Mac
  - Dinghy

2) Docker Compose
  If you install Docker for Mac, `docker-compose` is also installed
  Otherwise: `sudo pip install docker-compose`

## Setup

Run either `pip install .` or `python setup.py install`

`hokusai` should be installed on your PATH.

## Usage

`hokusai --help` lists all available commands

### Scaffolding

`hokusai scaffold` writes a Dockerfile, development.yml and test.yml in teh current directory

### Development

`hokusai dev` boots a development stack as defined in development.yml

### Testing

`hokusai test` boots a testing stack as defined in test.yml and exits with the return code of the test suite defined as the command of the "test" service
