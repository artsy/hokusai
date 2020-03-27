## HOKUSAI [![CircleCI](https://circleci.com/gh/artsy/hokusai/tree/master.svg?style=svg)](https://circleci.com/gh/artsy/hokusai/tree/master)

<a href="https://en.wikipedia.org/wiki/Hokusai"><img height="300" src="hokusai.jpg"></a>

Hokusai is a Docker + Kubernetes CLI for application developers.

Hokusai "dockerizes" applications and manages their lifecycle throughout development, testing, and release cycles.

Hokusai wraps calls to [kubectl](https://kubernetes.io/), [docker](https://www.docker.com/), [docker-compose](https://docs.docker.com/compose/) and [git](https://git-scm.com/) with a CLI, and defines a CI workflow.

Hokusai currently only supports Kubernetes deployments on AWS, configured to pull from ECS container repositories (ECR), although other providers may be added in the future.

### Why Hokusai?

At [Artsy](http://www.artsy.net), as we began working with Kubernetes, while impressed with its design, capabilities, and flexibility, we were in need of tooling we could deliver to agile development teams that addressed the day-to-day tasks of application development, delivery, introspection and maintenance, while providing a clean and uncomplicated interface.

Transitioning teams to the Docker / Kubernetes ecosystem can be intimidating, and comes with a steep learning curve. We set out to create a Heroku-like CLI that would shepherd the application developer into the ecosystems of Docker and Kubernetes, and while introducing new tooling and concepts, outlining a clear practice for dependency management, local development, testing and CI, image repository structure, deployment and orchestration.

## Requirements

1. [Python 2.x](https://www.python.org/downloads/) and [pip](https://pip.pypa.io/en/stable/installing/)

It's recommended that you use [`pyenv`](https://github.com/pyenv/pyenv) to install the correct version of python.

```
# Only if you don't already have pyenv installed
brew install pyenv

pyenv install -s
```

Before installing pythons via pyenv, make sure you are using brew-installed libraries `openssl`, `readline` and xcode-installed `zlib` and these libraries are correctly linked.  For example:

```
brew install openssl

If you need to have openssl@1.1 first in your PATH run:
  echo 'export PATH="/usr/local/opt/openssl@1.1/bin:$PATH"' >> ~/.bash_profile

For compilers to find openssl@1.1 you may need to set:
  export LDFLAGS="-L/usr/local/opt/openssl@1.1/lib"
  export CPPFLAGS="-I/usr/local/opt/openssl@1.1/include"

For pkg-config to find openssl@1.1 you may need to set:
  export PKG_CONFIG_PATH="/usr/local/opt/openssl@1.1/lib/pkgconfig"
```

Now, when installing pythons (see `.python-version` for the current version to install for Hokusai development) you should see the following output.

```
$ pyenv install 2.7.16

python-build: use openssl from homebrew
python-build: use readline from homebrew

Downloading Python-2.7.16.tar.xz...
-> https://www.python.org/ftp/python/2.7.16/Python-2.7.16.tar.xz
Installing Python-2.7.16...
python-build: use readline from homebrew
python-build: use zlib from xcode sdk

Installed Python-2.7.16 to /Users/isacpetruzzi/.pyenv/versions/2.7.16
```

2. [Pipenv](https://github.com/pypa/pipenv)

If you use homebrew

```
brew install pipenv
```

Install dev dependencies via `pipenv`

```
`pipenv install --dev`.
```

Other installation methods can be found in the project's repo

3. [Docker](https://docs.docker.com/)

If you use homebrew on OSX, install Docker for Mac with: `brew tap caskroom/cask && brew cask install docker`

4. [Docker Compose](https://docs.docker.com/compose/)

If you installed Docker for Mac, `docker-compose` is also installed. Otherwise install with: `pip install docker-compose`.

5. [Git](https://git-scm.com/)

## Installation

If you're on OSX, the preferred installation method is via homebrew:

```
$ brew tap artsy/formulas
$ brew install hokusai
```

If you've previously installed hokusai via an alternate installation method, you may need to force the `link` step. If you installed hokusai via pip, you may also want to cleanup that installation:

```
$ pip uninstall hokusai
$ brew link --overwrite hokusai
```

### Alternate Installation Methods

#### Via pip

Note: If installing via pip fails due to pip failing to upgrade your system Python packages, try running `pip install hokusai --ignore-installed`.

#### Via curl

Note: You may need to adjust the target destination to match a directory in your `$PATH`.

```
curl --silent https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-latest-$(uname -s)-$(uname -m) -o /usr/local/bin/hokusai && chmod +x /usr/local/bin/hokusai
```

## Setup

1. [Configure your AWS credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#configuring-credentials).
1. Run `hokusai configure --kubectl-version <kubectl version> --s3-bucket <bucket name> --s3-key <file key>`. You'll need to provide the kubectl version matching your Kubernetes deployments, as well as the S3 bucket name and key of your org's kubectl config file. System administrators: see [Administering Hokusai](./docs/Administering_Hokusai.md) for instructions on preparing AWS, Kubernetes, and publishing a kubectl config file. Artsy devs: see [these artsy/README docs](https://github.com/artsy/README/blob/master/playbooks/hokusai.md) for the current way to install and configure hokusai.

To enable bash autocompletion: `eval "$(_HOKUSAI_COMPLETE=source hokusai)"`

## Getting Started

See [Getting Started.md](./docs/Getting_Started.md) to start using Hokusai for your project.

## Command Reference

A full command reference can be found in [Command Reference.md](./docs/Command_Reference.md).

## Developing Hokusai

To work on Hokusai itself, set up your local development environment like so:

- As above, install `python`, `pipenv`, `docker`, `docker-compose` and `git`.

To install the Hokusai package in "editable mode" from a checkout of this repository, you can run `pip install --editable .` This works well in combination with [Virtualenv/Virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) as you can install the project in editable mode within a virtualenv, and from a release in your default system environment.

## Testing Hokusai

Install pipenv (see above)

Install dependencies: `pipenv install --dev`.

All tests can be run with `pipenv run tests`.

Only run unit tests: `pipenv run unit-tests`
Only run integration tests: `pipenv run integration-tests`

Tests for specific modules, TestClasses, or even methods can be run with `pipenv run test test.unit.test_module.TestClass.test_method`

Set the `DEBUG=1` environment variable to print boto logging

## Review Apps

Hokusai can be used to simplify the process of spinning up a "review app" instance of your project, based on a feature branch or pull request.

Full details are in the [Review App reference](./docs/Review_Apps.md).

## Distributing Hokusai

Merges to master automatically distribute Pyinstaller versions for beta testing at https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-head-Darwin-x86_64 and https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-head-Linux-x86_64 respectively.

To create a new release, bump the version by editing the `./hokusai VERSION` file, create an entry in CHANGELOG.md and open a PR from `master` to the `release` branch of this repo.

## The Name

The project is named for the great Japanese artist [Katsushika Hokusai](https://www.artsy.net/article/artsy-editorial-7-things-hokusai-creator-great-wave) (1760-1849).

## About Artsy

<a href="https://www.artsy.net/">
  <img align="left" src="https://avatars2.githubusercontent.com/u/546231?s=200&v=4"/>
</a>

This project is the work of engineers at [Artsy][footer_website], the world's
leading and largest online art marketplace and platform for discovering art.
One of our core [Engineering Principles][footer_principles] is being [Open
Source by Default][footer_open] which means we strive to share as many details
of our work as possible.

You can learn more about this work from [our blog][footer_blog] and by following
[@ArtsyOpenSource][footer_twitter] or explore our public data by checking out
[our API][footer_api]. If you're interested in a career at Artsy, read through
our [job postings][footer_jobs]!

[footer_website]: https://www.artsy.net/
[footer_principles]: https://github.com/artsy/README/blob/master/culture/engineering-principles.md
[footer_open]: https://github.com/artsy/README/blob/master/culture/engineering-principles.md
[footer_blog]: https://artsy.github.io/
[footer_twitter]: https://twitter.com/ArtsyOpenSource
[footer_api]: https://developers.artsy.net/
[footer_jobs]: https://www.artsy.net/jobs
