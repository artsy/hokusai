HOKUSAI
-------

Artsy Docker Development Toolkit

<img height="300" src="hokusai.jpg">

## Requirements

1) [Docker](https://docs.docker.com/)

2) [Docker Compose](https://docs.docker.com/compose/) If you install Docker for Mac, `docker-compose` is also installed. Otherwise install with: `sudo pip install docker-compose`

3) [AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/installing.html) Install with: `pip install awscli`

4) [kubectl](http://kubernetes.io/docs/user-guide/prereqs/) Install the `kubectl` binary and kubectl configuration in `~/.kube/config` for your Kubernetes cluster - make sure the version of the `kubectl` binary matches your cluster

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

Required options:
  - `--aws-account-id`: Your AWS account ID - can be found in your AWS account console
  - `--framework`: Either "rack" or "nodejs"
  - `--base-image`: The base docker image for the project `Dockerfile` - i.e. "ruby:2.2" or "ruby:2.2-alpine" - see [Docker Hub](https://hub.docker.com/) for valid base images

### Checking dependencies

`hokusai check` makes sure everything is set up correctly in your local environment and for your project - the `--interactive` flag prompts to install `docker-compose`, `aws` and `kubectl`, if missing

### Development

`hokusai dev` boots a development stack as defined in `hokusai/development.yml`

### Testing

`hokusai test` boots a testing stack as defined in `hokusai/test.yml` and exits with the return code of the test command


### Working with images

#### Building an image

`hokusai build` builds the latest docker image for the project

#### Pulling images

`hokusai pull` pulls images and tags for your project from your AWS account's ECR repo for the named project

#### Pushing an image

`hokusai push` pushes a locally built image to your AWS account's ECR repo for the named project

#### Listing images

`hokusai images` lists all project images in your local docker registry


### Working with secrets

#### Creating secrets

`hokusai add_secret {CONTEXT} {KEY} {VALUE}` adds a secret to Kubernetes for the given context.  The secrets created are added to the Kubernetes secret object `{project}-secrets`


### Working with Kubernetes

#### Launching a stack

`hokusai stack up {CONTEXT}` launches the stack defined in `hokusai/{CONTEXT}.yml' for the given Kubernetes context

#### Deleting a stack

`hokusai stack down {CONTEXT}` deletes the stack defined in `hokusai/{CONTEXT}.yml' for the given Kubernetes context

#### Checking a stack status

`hokusai stack status {CONTEXT}` prints the stack status defined in `hokusai/{CONTEXT}.yml' for the given Kubernetes context

#### Deploying

`hokusai deploy {CONTEXT} {TAG}` updates the Kubernetes deployment for the given context to the given image tag

#### Running a console

`hokusai console {CONTEXT}` launches a container and attaches a shell session in the given context

#### Running a command

`hokusai run {CONTEXT} {COMMAND}` launches a container and runs the given command in the given context.  It exits with the status code of the command run in the container (useful for `rake` tasks, etc)
