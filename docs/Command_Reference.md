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

Required options:
  - `--aws-account-id`: Your AWS account ID - can be found in your AWS account console.
  - `--project-type`: `ruby-rack`, `ruby-rails`, `nodejs`, `elixir`, or `python-wsgi`.

When running `hokusai setup` `staging.yml` and `production.yml` are created in the `./hokusai` project directory. These files define configuration for a staging / production Kubernetes context that you are assumed to have available, and Hokusai is opinionated about a workflow between a staging and a production Kubernetes context.

Note: `hokusai staging` `hokusai production` subcommands such as `create`, `update`, `env`, `deploy` and `logs` reference the respective environment YAML file and interacts with the respective Kubernetes context.

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

### Working with remotely deployed Kubernetes environments

* `hokusai [staging|production]` - Interact with remote Kubernetes resources.

* `hokusai [staging|production] create` - Create the Kubernetes resources defined in the environment config, either `./hokusai/staging.yml` or `./hokusai/production.yml`.
* `hokusai [staging|production] update` - Update the Kubernetes resources defined in the environment config.
* `hokusai [staging|production] delete` - Delete the Kubernetes resources defined in the environment config.
* `hokusai [staging|production] status` - Print the Kubernetes resources status defined in the environment config.

* `hokusai [staging|production] deploy` - Update the project's deployment(s) for a given environment to reference the given image tag and update the tag (staging/production) to reference the same image.
* `hokusai [staging|production] history` - Print the project's deployment history in terms of revision number, creation time, container name and image tag for a given environment.
* `hokusai [staging|production] refresh` - Refresh the project's deployment(s) by recreating the currently running containers. 

* `hokusai [staging|production] env` - Interact with the runtime environment for the application
  - `hokusai [staging|production] env create` - Create the Kubernetes configmap object `{project_name}-environment`
  - `hokusai [staging|production] env get` - Print environment variables stored on the Kubernetes server
  - `hokusai [staging|production] env set` - Set environment variables on the Kubernetes server. Environment variables are stored for the project as key-value pairs in the Kubernetes configmap object `{project_name}-environment`
  - `hokusai [staging|production] env unset` - Remove environment variables stored on the Kubernetes server
  - `hokusai [staging|production] env delete` - Delete the Kubernetes configmap object `{project_name}-environment`

* `hokusai [staging|production] run` - Launch a container and run a given command. It exits with the status code of the command run in the container (useful for `rake` tasks, etc). Use single quotes around your command string if it contains whitespace.
  - Use the flag `--tty` to attach your terminal, if your command is interactive. E.g. `hokusai production run --tty 'bundle exec rails c'` launches an interactive console for a Rails project.
  - The flag `--help` shows other flags that might be helpful.
* `hokusai [staging|production] logs` - Print the logs from your application containers


### Working with review apps
Hokusai provides a command for managing review apps. Review apps are useful for testing feature branches that are not yet ready to be deployed to staging but we do want to test them on a staging-like environment.
In order to start a review app you will need to follow these steps:
1) Create new review app
```shell
hokusai review_app create <name> # we recommend using branch name or pr number as name
```
This command will create a new `<name>.yaml` under `hokusai/` folder.

2) Check newly created `<name>.yaml` file and make sure everything looks good. Note that we use Kubernetes [`namespace`](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) for review apps. Basically each review app will end up being in its own namespace to not collide with staging.

3) Push an image with this review app tag:
```shell
hokusai registry push --tag <name>
```

4) Create new deployment on k8s:
```shell
hokusai review_app apply <name>
```

### Working with the Staging -> Production pipeline

* `hokusai pipeline` - Interact with the project's' staging -> production pipeline
  - `hokusai pipeline gitdiff` - Print a git diff between the tags deployed on production vs staging.
  - `hokusai pipeline gitlog`  - Print a git log comparing the tags deployed on production vs staging, can be used to see what commits are going to be promoted.
  - `hokusai pipeline promote` - Update the project's deployment(s) on production with the image tag currently deployed on staging and update the production tag to reference the same image.
