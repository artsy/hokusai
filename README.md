HOKUSAI [![CircleCI](https://circleci.com/gh/artsy/hokusai/tree/master.svg?style=svg)](https://circleci.com/gh/artsy/hokusai/tree/master)
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

If you installed Docker for Mac, `docker-compose` is also installed. Otherwise install with: `pip install docker-compose`.

4) [Git](https://git-scm.com/)


## Setup

1) Install Hokusai via pip with `pip install hokusai` and `hokusai` will be installed on your `PATH`.

Note: If installing via pip fails due to pip failing to upgrade your system Python packages, try running `pip install hokusai --ignore-installed`.

Alternatively, you can workaround a pure Python installation and install a binary for OSX by simply downloading it from https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-{version}-{platform}-x86_64 and adding it to your `$PATH`, i.e. to download the latest version, run:

```
curl --silent https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-latest-$(uname -s)-$(uname -m) -o /usr/local/bin/hokusai && chmod +x /usr/local/bin/hokusai
```


2) [Configure your AWS credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#configuring-credentials).

3) Run `hokusai configure --kubectl-version <kubectl version> --s3-bucket <bucket name> --s3-key <file key>`.  You'll need to provide the kubectl version matching your Kubernetes deployments, as well as the S3 bucket name and key of your org's kubectl config file. System administrators: see [Administering Hokusai](./docs/Administering_Hokusai.md) for instructions on preparing AWS, Kubernetes, and publishing a kubectl config file. Artsy devs: see [these artsy/README docs](https://github.com/artsy/README/blob/master/playbooks/hokusai.md) for the current way to install and configure hokusai.

To enable bash autocompletion: `eval "$(_HOKUSAI_COMPLETE=source hokusai)"`


## Getting Started

See [Getting Started.md](./docs/Getting_Started.md) to start using Hokusai for your project.


## Command Reference

A full command reference can be found in [Command Reference.md](./docs/Command_Reference.md).


## Developing Hokusai

To work on Hokusai itself, set up your local development environment like so:

- As above, install `python`, `pip`, `docker`, `docker-compose` and `git`.

To install the Hokusai package in "editable mode" from a checkout of this repository, you can run `pip install -e .`  This works well in combination with [Virtualenv/Virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) as you can install the project in editable mode within a virtualenv, and from a release in your default system environment.


## Testing Hokusai

Install dependencies: `pip install -r requirements.txt`.

All tests can be run with `python -m unittest discover test`.

Only run unit tests: `python -m unittest discover test.unit`
Only run integration tests: `python -m unittest discover test.integration`

Tests for specific modules, TestClasses, or even methods can be run with `python -m unittest test.unit.test_module.TestClass.test_method`

Set the `DEBUG=1` environment variable to print boto logging

## Review Apps

Hokusai can be used to simplify the process of spinning up a "review app" instance of your project, based on a feature branch or pull request.

Full details are in the [Review App reference](./docs/Review_Apps.md).

## Distributing Hokusai

Merges to master automatically distribute Pyinstaller versions for beta testing at https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-head-Darwin-x86_64 and https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-head-Linux-x86_64 respectively.

To create a new release, bump the version by editing the `./hokusai VERSION` file, create an entry in CHANGELOG.md and open a PR from `master` to the `release` branch of this repo.

## The Name

The project is named for the great Japanese artist [Katsushika Hokusai](https://www.artsy.net/article/artsy-editorial-7-things-hokusai-creator-great-wave) (1760-1849).
