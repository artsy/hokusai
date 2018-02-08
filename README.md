HOKUSAI
-------

<a href="https://en.wikipedia.org/wiki/Hokusai"><img height="300" src="hokusai.jpg"></a>

Hokusai is a Docker + Kubernetes CLI for application developers.

Hokusai "dockerizes" applications and manages their lifecycle throughout development, testing, and release cycles.

Hokusai wraps calls to [kubectl](https://kubernetes.io/), [docker](https://www.docker.com/), [docker-compose](https://docs.docker.com/compose/) and [git](https://git-scm.com/) with a CLI, and defines a CI workflow.

Hokusai currently only supports Kubernetes deployments on AWS, configured to pull from ECS container repositories (ECR), although other providers may be added in the future.

### Why Hokusai?

At [Artsy](http://www.artsy.net), as we began working with Kubernetes, while impressed with its design, capabilities, and flexibility, we were in need of tooling we could deliver to agile development teams that addressed the day-to-day tasks of application development, delivery, introspection and maintenance, while providing a clean and uncomplicated interface.

Transitioning teams to the Docker / Kubernetes ecosystem can be intimidating, and comes with a steep learning curve.  We set out to create a Heroku-like CLI that would shepherd the application developer into the ecosystems of Docker and Kubernetes, and while introducing new tooling and concepts, outlining a clear practice for dependency management, local development, testing and CI,  image repository structure, deployment and orchestration.


## Requirements

1) [Python 2.x](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installing/)

2) [Docker](https://docs.docker.com/)

If you use homebrew on OSX, install Docker for Mac with: `brew tap caskroom/cask && brew cask install docker`

3) [Docker Compose](https://docs.docker.com/compose/)

If you installed Docker for Mac, `docker-compose` is also installed. Otherwise install with: `(sudo) pip install docker-compose`.

4) [Git](https://git-scm.com/)


## Setup

1) Install Hokusai via pip with `(sudo) pip install hokusai` and `hokusai` will be installed on your `PATH`.

Note: If installing via pip fails due to pip failing to upgrade your system Python packages, try running `(sudo) pip install hokusai --ignore-installed`.

2) Set the environment variables `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY` in your shell / `~/.bash_profile`.

3) Run `hokusai configure --kubectl-version <kubectl version> --s3-bucket <bucket name> --s3-key <file key>`.  You'll need to provide the kubectl version matching your Kubernetes deployments, as well as the S3 bucket name and key of your org's kubectl config file. (System administrators, see [Administering Hokusai](./docs/Administering_Hokusai.md) for instructions on preparing AWS, Kubernetes, and publishing a kubectl config file.)

To enable bash autocompletion: `eval "$(_HOKUSAI_COMPLETE=source hokusai)"`


## Getting Started

See [Getting Started.md](./docs/Getting_Started.md) to start using Hokusai your project.


## Command Reference

A full command reference can be found in [Command Reference.md](./docs/Command_Reference.md).


## Developing Hokusai

To work on Hokusai itself, set up your local development environment like so:

- As above, install `python`, `pip`, `docker`, `docker-compose` and `git`.

- Install Python development packages: `pip install -r requirements.txt`.

Finally, to install the Hokusai package to your system's `PATH` from a checkout of this repository, you can run `(sudo) pip install --upgrade .`

Alternatively, you can invoke Hokusai directly with `python bin/hokusai`.


## Testing Hokusai

All tests can be run with `python -m unittest discover test`.

Only run unit tests: `python -m unittest discover test.unit`
Only run integration tests: `python -m unittest discover test.integration`

Tests for specific modules, TestClasses, or even methods can be run with `python -m unittest test.unit.test_module.TestClass.test_method`

Set the `DEBUG=1` environment variable to print boto logging

## The Name

The project is named for the great Japanese artist [Katsushika Hokusai](https://www.artsy.net/article/artsy-editorial-7-things-hokusai-creator-great-wave) (1760-1849).
