HOKUSAI
-------

Artsy Docker Development Toolkit

<img height="300" src="hokusai.jpg">

## Requirements

1) Docker via either:
  - [Docker for Mac](https://docs.docker.com/docker-for-mac/)
  - [Dinghy](https://github.com/codekitchen/dinghy)

2) [Docker Compose](https://docs.docker.com/compose/) If you install Docker for Mac, `docker-compose` is also installed. Otherwise run: `sudo pip install docker-compose`

3) [AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/installing.html) `pip install awscli`

4) Set the `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY` environment variables.  You should have permissions to evaluate the `aws ecr get-login` comamnd for your ECR region and push access to your ECR repositories

## Setup

Ensure `docker` and `docker-compose` are installed to your PATH

Run either `pip install .` or `python setup.py install`

`hokusai` should be installed on your PATH

To upgrade to the latest changes in this repo, run: `pip install --upgrade .`

## Use

`hokusai --help` lists all available commands

See `hokusai {command} --help` for command-specific options

### Scaffolding

`hokusai scaffold` writes a Dockerfile, development.yml and test.yml in the current directory

### Development

`hokusai dev` boots a development stack as defined in development.yml

### Testing

`hokusai test` boots a testing stack as defined in test.yml and exits with the return code of the test suite
