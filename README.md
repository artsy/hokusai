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

4) [kubectl](http://kubernetes.io/docs/user-guide/prereqs/) Install the `kubectl` binary and configuration for your Kubernetes cluster

4) Set the `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY` environment variables.  You should have permissions to evaluate the `aws ecr get-login` comamnd for your ECR region and push access to your ECR repositories

## Setup

Ensure `docker`, `docker-compose` and `aws` are installed to your PATH

Ensure Python-development headers are installed - (on Debian run `sudo apt-get install python-dev`)

Run either `pip install .` or `python setup.py install`

`hokusai` should be installed on your PATH

To upgrade to the latest changes in this repo, run: `pip install --upgrade .`

## Use

`hokusai --help` lists all available commands

See `hokusai {command} --help` for command-specific options

### Initializing a project

`hokusai init` writes hokusai project config to `hokusai/config.yml`, creates `hokusai/test.yml', `hokusai/development.yml' and `hokusai/production.yml' and creates a Dockerfile in the current directory

### Checking dependencies

`hokusai check` makes sure everything is set up correctly in your local environment and for your project - the `--interactive` flag prompts to install `docker-compose`, `aws` and `kubectl`, if missing

### Development

`hokusai dev` boots a development stack as defined in `hokusai/development.yml`

### Testing

`hokusai test` boots a testing stack as defined in `hokusai/test.yml` and exits with the return code of the test command

### Production

#### Pushing an image

`hokusai push` builds an image and pushes it to your AWS account's ECR repo for the named project

#### Creating secrets

`hokusai add_secret {CONTEXT} {KEY} {VALUE}` adds a secret to Kubernetes for the given context.  The secrets created are added to the Kubernetes secret object `{project}-secrets`

#### Launching a stack

`hokusai stack_up {CONTEXT}` launches the stack defined in `hokusai/production.yml' for the given Kubernetes context

#### Deleting a stack

`hokusai stack_down {CONTEXT}` deletes the stack defined in `hokusai/production.yml' for the given Kubernetes context

#### Rolling deployments

`hokusai deploy {CONTEXT}` updates the Kubernetes deployment for the given context to `latest` or the given image tag
