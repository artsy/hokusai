HOKUSAI
-------

Artsy Docker Development Toolkit

<img height="300" src="hokusai.jpg">

## About

Hokusai works with [Kubernetes](https://kubernetes.io/) and [Docker](https://www.docker.com/) to manage a container driven workflow, from development to testing and deployment.

## Requirements

1) [Docker](https://docs.docker.com/)

2) [Docker Compose](https://docs.docker.com/compose/)

If you install Docker for Mac, `docker-compose` is also installed. Otherwise install with: `sudo pip install docker-compose`.

3) [AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/installing.html) 

Install with: `pip install awscli`. Set the `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY` environment variables. You should have permissions to evaluate the `aws ecr get-login` comamnd for your ECR region and push access to your ECR repositories.

4) [kubectl](http://kubernetes.io/docs/user-guide/prereqs/)

Install the `kubectl` binary and kubectl configuration in `~/.kube/config` for your Kubernetes cluster - make sure the version of the `kubectl` binary matches your cluster.

## Setup

Ensure `docker`, `docker-compose`, `kubectl` and `aws` are installed to your PATH.

Ensure Python-development headers are installed. On Debian run

```
sudo apt-get install python-dev
```

Now package Hokusai with

```
pip install .
```

And `hokusai` should now be installed on your PATH.

Now run

```
hokusai check --interactive
```

to ensure everything is set up correctly.

To upgrade to the latest changes in this repo, just run

```
pip install --upgrade .
```

## Use

```
hokusai --help
hokusai {command} --help
```

### Initializing a project

Run

```
hokusai init
```

This writes hokusai project config to `hokusai/config.yml`, creates test, development and production yaml files alongside it, and adds a Dockerfile to the current directory.

Required options:
  - `--aws-account-id`: Your AWS account ID - can be found in your AWS account console.
  - `--framework`: Either "rack" or "nodejs".
  - `--base-image`: The base docker image for the project `Dockerfile` - i.e. "ruby:2.2" or "ruby:2.2-alpine" - see [Docker Hub](https://hub.docker.com/) for valid base images.


### Development

* `hokusai dev` - Boot a development stack as defined in `hokusai/development.yml`.
* `hokusai test` - Boot a testing stack as defined in `hokusai/test.yml` and exits with the return code of the test command.


### Working with Images

* `hokusai build` - Build the latest docker image for the project.
* `hokusai pull` - Pull images for your project from your AWS ECR repo.
* `hokusai push` - Push a locally built image to your AWS ECR repo.
* `hokusai images` - List all project images in your local docker registry.

### Working with ConfigMaps

* `hokusai config pull` - Pulls config from the Kubernetes server and writes to the `hokusai` directory.
* `hokusai config push` - Pushes config from the hokusai directory to the Kubernetes server. Config is created for the project as the Kubernetes ConfigMap object `{project}-config`


### Working with Secrets

* `hokusai secrets get` - Prints secrets stored on the Kubernetes server
* `hokusai secrets set` - Sets secrets on the Kubernetes server. Secrets are stored for the project as key-value pairs in the Kubernetes Secret object `{project}-secrets`
* `hokusai secrets unset` - Removes secrets stored on the Kubernetes server

### Working with Stacks

* `hokusai stack up` - Launch a stack for a given Kubernetes context.
* `hokusai stack down` - Delete a stack defined for a given Kubernetes context.
* `hokusai stack status` - Print the stack status.

### Deployment

* `hokusai deploy` - Update the Kubernetes deployment to a given image tag.
* `hokusai promote` - Update the Kubernetes deployment in a given context to match the deployment in another context

### Running a console

* `hokusai console` - Launch a container and attach a shell session.
* `hokusai run` - Launch a container and run a given command. It exits with the status code of the command run in the container (useful for `rake` tasks, etc).
