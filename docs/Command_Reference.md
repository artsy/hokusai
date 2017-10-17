## Command Reference

```bash
hokusai --help
hokusai {command} --help
```

You can add `-v` (Verbose) to most commands which will show you details of the individual commands Hokusai will run.

### Configuring Hokusai for your organization

* `hokusai configure` - installs and configures kubectl

Required options:
  - `--kubectl-version`:  The version of your Kubernetes clusters
  - `--s3-bucket`: The S3 bucket containing your organization's kubectl config file
  - `--s3-key`: The S3 key of your organization's kubectl config file

Hokusai uses `kubectl` to connect to Kubernetes and the [boto3](https://github.com/boto/boto3) library to interact with AWS ECR.

Make sure you have set the environment variables `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY` and optionally, `$AWS_DEFAULT_REGION` and `$AWS_ACCOUNT_ID` in your shell / `~/.bash_profile`.

`hokusai configure` provides basic setup for installing and configuring kubectl:

```bash
hokusai configure --help
```

The recommended approach is to upload your `kubectl` config to S3 and use following command to install it:

```bash
hokusai configure --kubectl-version <kubectl version> --s3-bucket <bucket name> --s3-key <file key>
```

### Setting up a project

* `hokusai setup` - Writes hokusai project config to `hokusai/config.yml`, creates test, development and production YAML files alongside it, adds a Dockerfile to the current directory, and creates a project ECR repo.

When running `hokusai setup` `staging.yml` and `production.yml` are created in the `./hokusai` project directory. These files define remote environments, and Hokusai is opinionated about a workflow between a staging and a production Kubernetes context.

`hokusai remote` commands such as `create`, `update`, `env`, `deploy` and `logs` require invocation with either the `--staging` or `--production` flag, which references the respective environment YAML file and interacts with the respective Kubernetes context.

Required options:
  - `--aws-account-id`: Your AWS account ID - can be found in your AWS account console.
  - `--project-type`: `ruby-rack`, `ruby-rails`, `nodejs`, `elixir`, or `python-wsgi`.

* `hokusai check` - Checks that Hokusai dependencies are correctly installed and configured for the current project.

### Hokusai local

* `hokusai local` - Interact with your local project and Docker engine

* `hokusai local dev` - Interact with docker-compose targeting the development environment defined in ./hokusai/development.yml

  - `hokusai local dev start` - Start the development environment defined in `./hokusai/development.yml`.
  - `hokusai local dev stop` - Stop the development environment defined in `./hokusai/development.yml`.
  - `hokusai local dev status` - Print the status of the development environment.
  - `hokusai local dev logs` - Print logs from the development environment.
  - `hokusai local dev run` - Run a command in the development environment's container with the name 'project-name' in hokusai/config.yml.
  - `hokusai local dev clean` - Stop and remove all containers in the environment.

* `hokusai local build` - Build the docker image defined in ./hokusai/common.yml.
* `hokusai local test` - Start the testing environment defined `hokusai/test.yml` and exit with the return code of the test command.

### Hokusai registry

* `hokusai registry` - Interact with the project registry

* `hokusai registry push` - Build and push an image to the project registry.
* `hokusai registry images` - Print image builds and tags in the project registry.

### Hokusai remote

* `hokusai remote` - Interact with remote Kubernetes resources.

* `hokusai remote create` - Create the Kubernetes remote resources defined in ./hokusai/{staging/production}.yml.
* `hokusai remote update` - Update the Kubernetes remote resources defined in ./hokusai/{staging/production}.yml.
* `hokusai remote delete` - Delete the Kubernetes remote resources defined in ./hokusai/{staging/production}.yml.
* `hokusai remote status` - Print the Kubernetes remote resources status defined in ./hokusai/{staging/production}.yml.

* `hokusai remote deployment` - Interact with the project's' remote Kubernetes deployment(s)

  - `hokusai remote deployment update` - Update the project's deployment(s) for a given remote environment to reference the given image tag and update the tag (staging/production) to reference the same image.
  - `hokusai remote deployment history` - Print the project's deployment history in terms of revision number, creation time, container name and image tag for a given remote environment.
  - `hokusai remote deployment refresh` - Refresh the project's deployment(s) by recreating the currently running containers.
  - `hokusai remote deployment promote` - Update the project's deployment(s) on production with the image tag currently deployed on staging and update the production tag to reference the same image.

* `hokusai remote env` - Interact with the runtime environment for the application

  - `hokusai remote env create` - Create the Kubernetes configmap object `{project_name}-environment`
  - `hokusai remote env get` - Print environment variables stored on the Kubernetes server
  - `hokusai remote env set` - Set environment variables on the Kubernetes server. Environment variables are stored for the project as key-value pairs in the Kubernetes configmap object `{project_name}-environment`
  - `hokusai remote env unset` - Remove environment variables stored on the Kubernetes server
  - `hokusai remote env delete` - Delete the Kubernetes configmap object `{project_name}-environment`

* `hokusai remote gitdiff` - Print a git diff between the tags deployed on production vs staging.
* `hokusai remote gitlog`  - Print a git log comparing the tags deployed on production vs staging, can be used to see what commits are going to be promoted.
* `hokusai remote run` - Launch a container and run a given command. It exits with the status code of the command run in the container (useful for `rake` tasks, etc).
* `hokusai remote logs` - Print the logs from your application containers
