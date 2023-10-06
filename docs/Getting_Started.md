# Getting Started

Here's how to setup Hokusai for say a Rails project.

We assume you have already installed Hokusai and the [Setup steps](../README.md#Setup) have been performed.

## Bootstrap Hokusai for a Rails project

```bash
cd ./path/to/my/git/rails/project-repo
hokusai setup
```

It will:

- Create an ECR repository for the project
- Create the following files under the project's root dir
  - Dockerfile
  - .dockerignore
- Create the following files under the project's root dir
  - hokusai/config.yml
  - hokusai/build.yml
  - hokusai/development.yml
  - hokusai/test.yml
  - hokusai/staging.yml
  - hokusai/production.yml

The yml files are described in [Hokusai Files](./hokusai_files.md).

## Check that Hokusai is correctly configured for your project

Run:

`hokusai check`

It will run a series of tests and warn you of any problems.


## Run the development environment

Run:

`hokusai dev start`

It will build a Docker image, then start a Docker Compose environment defined by `(project-repo)/hokusai/development.yml`

If no errors, interact with the running environment with:

```
hokusai dev status
hokusai dev logs
hokusai dev run bash
```

Shut down the environment with:

`hokusai dev stop`

This command does not delete container filesystems. To delete them, run:

`hokusai dev clean`


## Run the test suite in the test environment

Run:

`hokusai test`

It will build a Docker image, start a Docker Compose environment defined by `(project-repo)/hokusai/test.yml`, run the defined test command in the main (project-name) container to completion, and return its exit code.


## Build and push an image to ECR

Run:

`hokusai registry push`

It will build and push an image to ECR. By default, it tags the image as the SHA1 of the HEAD of your current git branch. The command will also tag the image as `latest`.

Once an image is pushed, list the images and tags in the registry with:

`hokusai registry images`


## Create the Kubernetes staging environment

Run:

`hokusai staging create`

Check resources with:

`hokusai staging status`

Show logs with:

`hokusai staging logs`


## Set Kubernetes staging environment and environment variables

Run:

```
hokusai staging env set FOO=bar
```

Make pods pick up the varr by:

```
hokusai staging refresh
```


## Create the Kubernetes production environment

```
hokusai production create
hokusai production status
hokusai production logs
```

## Set Kubernetes production environment and environment variables

```
hokusai production env set FOO=bar
```

Make pods upudate by:

```
hokusai production refresh
```

## Deploy changes to the Kubernetes staging environment

Make a commit, build new image, and push it to the registry, as mentioned above.

Deploy the new commit to staging with:

`hokusai production deploy {TAG}`

where TAG is the tag of the commit you just made.


## Promote the tag deployed on staging to production

```
hokusai pipeline promote
```
