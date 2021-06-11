## HOKUSAI [![CircleCI](https://circleci.com/gh/artsy/hokusai/tree/master.svg?style=svg)](https://circleci.com/gh/artsy/hokusai/tree/master)

<a href="https://en.wikipedia.org/wiki/Hokusai"><img height="300" src="hokusai.jpg"></a>

Hokusai is a Docker + Kubernetes CLI for application developers.

Hokusai "dockerizes" applications and manages their lifecycle throughout development, testing, and release cycles.

Hokusai wraps calls to [kubectl](https://kubernetes.io/), [docker](https://www.docker.com/), [docker-compose](https://docs.docker.com/compose/) and [git](https://git-scm.com/) with a CLI, and defines a CI workflow.

Hokusai currently only supports Kubernetes deployments on AWS, configured to pull from ECS container repositories (ECR), although other providers may be added in the future.

### Why Hokusai?

At [Artsy](http://www.artsy.net), as we began working with Kubernetes, while impressed with its design, capabilities, and flexibility, we were in need of tooling we could deliver to agile development teams that addressed the day-to-day tasks of application development, delivery, introspection and maintenance, while providing a clean and uncomplicated interface.

Transitioning teams to the Docker / Kubernetes ecosystem can be intimidating, and comes with a steep learning curve. We set out to create a Heroku-like CLI that would shepherd the application developer into the ecosystems of Docker and Kubernetes, and while introducing new tooling and concepts, outlining a clear practice for dependency management, local development, testing and CI, image repository structure, deployment and orchestration.

## Installation

MacOS:

```
$ brew tap artsy/formulas
$ brew install hokusai
```

Linux:

```
curl -sSL https://raw.githubusercontent.com/artsy/hokusai/master/get-hokusai.sh | sudo bash
```

Pip:

```
pip install hokusai
```

## Setup

1. [Configure your AWS credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html#configuring-credentials).
1. Run `hokusai configure --kubectl-version <kubectl version> --s3-bucket <bucket name> --s3-key <file key>`. You'll need to provide the kubectl version matching your Kubernetes deployments, as well as the S3 bucket name and key of your org's kubectl config file. System administrators: see [Administering Hokusai](./docs/Administering_Hokusai.md) for instructions on preparing AWS, Kubernetes, and publishing a kubectl config file. Artsy devs: see [these artsy/README docs](https://github.com/artsy/README/blob/master/playbooks/hokusai.md) for the current way to install and configure hokusai.

To enable bash autocompletion: `eval "$(_HOKUSAI_COMPLETE=source hokusai)"`

## Getting Started

See [Getting Started.md](./docs/Getting_Started.md) to start using Hokusai for your project.

## Command Reference

A full command reference can be found in [Command Reference.md](./docs/Command_Reference.md).

## Review Apps

Hokusai can be used to simplify the process of spinning up a "review app" instance of your project, based on a feature branch or pull request.

Full details are in the [Review App reference](./docs/Review_Apps.md).

## Developing Hokusai

To develop Hokusai itself, see [Developing Hokusai](./docs/develop.md).

## Distributing Hokusai

Merges to master automatically distribute Pyinstaller versions for beta testing at https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-beta-Darwin-x86_64 and https://artsy-provisioning-public.s3.amazonaws.com/hokusai/hokusai-beta-Linux-x86_64 respectively.

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
