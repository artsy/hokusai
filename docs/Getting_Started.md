## Getting Started

Hokusai aims to provide a smooth CI workflow on a per-project basis.  As such, it is designed to be configured and run from a shell within a project's git repo.

We will assume you have already installed Hokusai and run `hokusai configure`, as detailed in [Setup](#Setup).

1) Set up Hokusai for a Rails project
  ```bash
  cd ./path/to/my/rails/project/git/repo
  hokusai setup --aws-account-id 12345 --project-type ruby-rails
  ```

  Note: If you set the environment variable `AWS_ACCOUNT_ID` in your shell, you can omit the `--aws-account-id` option.

  `hokusai setup` will create:
  - A `Dockerfile` in your project root
  - A configuration folder `./hokusai`.  This folder contains:
      * `./hokusai/config.yml` - contains Hokusai project configuration
      * `./hokusai/common.yml` - a Docker Compose YAML file imported by `development.yml` and `test.yml`
      * `./hokusai/development.yml`- a Docker Compose YAML file for the development environment
      * `./hokusai/test.yml` - a Docker Compose YAML file for the test environment
      * `./hokusai/staging.yml` - a Kubernetes YAML file for the staging environment
      * `./hokusai/production.yml` - a Kubernetes YAML file for the production environment
  - An ECR repository for your project

  The files in `./hokusai` as well as the `Dockerfile` are meant to be a starting point for development of your specific application's dependencies, and can / should be freely modified, as you customize your Docker build, add service dependencies to your environments, introduce environment variables, or change the container runtime commands.

2) Check that Hokusai is correctly configured for your project

  `hokusai check` will run a series of tests and warn you if it finds anything improperly configured.

3) Run the development stack

  `hokusai dev start` will build a Docker image, then start a Docker Compose stack defined by `./hokusai/development.yml`

  If this command throws no errors, try interacting with the running stack with:

  ```bash
  hokusai dev status
  hokusai dev logs
  hokusai dev shell
  ```

  To shut down the stack's running containers, run `hokusai dev stop`

  Container filesystems will be preserved between stack starts and stops, unless you run:

  `hokusai dev clean`, in which case the container filesystems will be deleted.


4) Run the test suite in the test stack

  `hokusai test` will build a Docker image, start a Docker Compose stack defined by `./hokusai/test.yml`, run the defined test command in the main (project-name) container to completion, and return its exit code.

  See [Writing Docker Compose YAML files](./Configuration.md#Writing Docker Compose YAML files) if you want to modify your test stack's configuration.

5) Build and push an image to ECR

  `hokusai push` will build and push an image to ECR.  By default, it tags the image as the SHA1 of the HEAD of your current git branch (by calling `git rev-parse HEAD`).  You can override this behavior with the `--tag` option, although this is not recommended as creating builds matched to the SHA1 of Git tags gives you a clean view of your ECR project repository and deployment history.

  The command will also tag the image as `latest`.  This image tag should not be referenced in any Kubernetes YAML configuration, but serves only as a pointer, which is referenced when creating a Kubernetes stack.

  The command aborts if any of the following conditions is met:
  - The working directory is not clean (you have uncommitted changes)
  - The working directory contains any files specified in your `.gitignore` file
  - The ECR project repository already contains the specified tag

  The reason for these conditional checks is that when building, Docker will copy your _entire_ working directory into the container image, which can produce unexpected results when building images locally, destined for production environments!  The reason Hokusai aborts if it detects the working directory is unclean, or any ignored files or directories are present, is because it attempts to prevent any local configuration leaking into container images.

  Once an image is pushed, you can list the images and tags in the ECR project repository with: `hokusai images`.

6) Create the Kubernetes staging environment
  ```bash
  hokusai env create --staging
  hokusai env set FOO=bar --staging
  ```

7) Create the Kubernetes staging stack with `hokusai stack create --staging`

  `hokusai stack status --staging` should eventually (once Kubernetes creates a load balancer for your project), output the ELB's DNS record.

  Get logs by running `hokusai logs --staging` and see deployment history with `hokusai history --staging`

8) Create the Kubernetes production environment

  ```bash
  hokusai env create --production
  hokusai env set FOO=baz --production
  ```

9) Create the Kubernetes production stack

  ```bash
  hokusai stack create --production
  hokusai stack status --production
  hokusai logs --production
  hokusai history --production
  ```

10) Create a new commit and push it to the remote repo with `hokusai push` as before.

11) Deploy the new commit to staging with `hokusai deploy {TAG} --staging` where TAG is the tag of the commit you just made.

12) Promote the tag just deployed on staging to production
  ```bash
  hokusai promote
  ```
