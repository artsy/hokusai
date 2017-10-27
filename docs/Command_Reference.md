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


### Local development

* `hokusai dev` - Interact with docker-compose targeting the development environment defined in ./hokusai/development.yml
  - `hokusai dev start` - Start the development environment defined in `./hokusai/development.yml`.
  - `hokusai dev stop` - Stop the development environment defined in `./hokusai/development.yml`.
  - `hokusai dev status` - Print the status of the development environment.
  - `hokusai dev logs` - Print logs from the development environment.
  - `hokusai dev run` - Run a command in the development environment's container with the name 'project-name' in hokusai/config.yml.
  - `hokusai dev clean` - Stop and remove all containers in the environment.


### Testing and building images

* `hokusai test` - Start the testing environment defined `hokusai/test.yml` and exit with the return code of the test command.
* `hokusai build` - Build the docker image defined in ./hokusai/common.yml. 


### Managing images in the registry

* `hokusai registry` - Interact with the project registry.
  - `hokusai registry push` - Build and push an image to the project registry.
  - `hokusai registry images` - Print image builds and tags in the project registry.


### Working with the Kubernetes staging environment

* `hokusai staging` - Interact with staging Kubernetes resources.

* `hokusai staging create` - Create the Kubernetes resources defined in ./hokusai/staging.yml.
* `hokusai staging update` - Update the Kubernetes resources defined in ./hokusai/staging.yml.
* `hokusai staging delete` - Delete the Kubernetes resources defined in ./hokusai/staging.yml.
* `hokusai staging status` - Print the Kubernetes resources status defined in ./hokusai/staging.yml.

* `hokusai staging deploy` - Update the project's deployment(s) for a given staging environment to reference the given image tag and update the tag (staging/production) to reference the same image.
* `hokusai staging history` - Print the project's deployment history in terms of revision number, creation time, container name and image tag for a given staging environment.
* `hokusai staging refresh` - Refresh the project's deployment(s) by recreating the currently running containers. 

* `hokusai staging env` - Interact with the runtime environment for the application
  - `hokusai staging env create` - Create the Kubernetes configmap object `{project_name}-environment`
  - `hokusai staging env get` - Print environment variables stored on the Kubernetes server
  - `hokusai staging env set` - Set environment variables on the Kubernetes server. Environment variables are stored for the project as key-value pairs in the Kubernetes configmap object `{project_name}-environment`
  - `hokusai staging env unset` - Remove environment variables stored on the Kubernetes server
  - `hokusai staging env delete` - Delete the Kubernetes configmap object `{project_name}-environment`

* `hokusai staging run` - Launch a container and run a given command. It exits with the status code of the command run in the container (useful for `rake` tasks, etc).
* `hokusai staging logs` - Print the logs from your application containers


### Working with the Kubernetes production environment

* `hokusai production` - Interact with production Kubernetes resources.

* `hokusai production create` - Create the Kubernetes resources defined in ./hokusai/production.yml.
* `hokusai production update` - Update the Kubernetes resources defined in ./hokusai/production.yml.
* `hokusai production delete` - Delete the Kubernetes resources defined in ./hokusai/production.yml.
* `hokusai production status` - Print the Kubernetes resources status defined in ./hokusai/production.yml.

* `hokusai production deploy` - Update the project's deployment(s) for a given production environment to reference the given image tag and update the tag (production/production) to reference the same image.
* `hokusai production history` - Print the project's deployment history in terms of revision number, creation time, container name and image tag for a given production environment.
* `hokusai production refresh` - Refresh the project's deployment(s) by recreating the currently running containers. 

* `hokusai production env` - Interact with the runtime environment for the application
  - `hokusai production env create` - Create the Kubernetes configmap object `{project_name}-environment`
  - `hokusai production env get` - Print environment variables stored on the Kubernetes server
  - `hokusai production env set` - Set environment variables on the Kubernetes server. Environment variables are stored for the project as key-value pairs in the Kubernetes configmap object `{project_name}-environment`
  - `hokusai production env unset` - Remove environment variables stored on the Kubernetes server
  - `hokusai production env delete` - Delete the Kubernetes configmap object `{project_name}-environment`

* `hokusai production run` - Launch a container and run a given command. It exits with the status code of the command run in the container (useful for `rake` tasks, etc).
* `hokusai production logs` - Print the logs from your application containers


### Working with the Staging -> Production pipeline

* `hokusai pipeline` - Interact with the project's' staging -> production pipeline
  - `hokusai gitdiff` - Print a git diff between the tags deployed on production vs staging.
  - `hokusai gitlog`  - Print a git log comparing the tags deployed on production vs staging, can be used to see what commits are going to be promoted.
  - `hokusai promote` - Update the project's deployment(s) on production with the image tag currently deployed on staging and update the production tag to reference the same image.
