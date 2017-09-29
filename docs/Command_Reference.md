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

### Setting up a project

* `hokusai setup` - Writes hokusai project config to `hokusai/config.yml`, creates test, development and production YAML files alongside it, adds a Dockerfile to the current directory, and creates a project ECR repo.

Required options:
  - `--aws-account-id`: Your AWS account ID - can be found in your AWS account console.
  - `--project-type`: `ruby-rack`, `ruby-rails`, `nodejs`, `elixir`, or `python-wsgi`.

* `hokusai check` - Checks that Hokusai dependencies are correctly installed and configured for the current project.

### Working locally

* `hokusai dev <start|stop|status|logs|shell|clean>`

  - `hokusai dev start` - Start the development stack defined in `./hokusai/development.yml`.
  - `hokusai dev stop` - Stop the development stack defined in `./hokusai/development.yml`.
  - `hokusai dev status` - Print the status of the development stack.
  - `hokusai dev logs` - Print logs from the development stack.
  - `hokusai dev shell` - Attach a shell session to the stack's primary project container.
  - `hokusai dev clean` - Stop and remove all containers in the stack.

### Working with CI

* `hokusai build` - Build the docker image defined in ./hokusai/common.yml.
* `hokusai test` - Start the testing stack defined `hokusai/test.yml` and exit with the return code of the test command.
* `hokusai push` - Build and push an image to the AWS ECR project repo.
* `hokusai images` - Print image builds and tags in the AWS ECR project repo.

### Working with Kubernetes

Hokusai uses `kubectl` to connect to Kubernetes. Hokusai `configure` provides basic setup for installing and configuring kubectl:

```bash
hokusai configure --help
```

The recommended approach is to upload your `kubectl` config to S3 and use following command to install it:

```bash
hokusai configure --kubectl-version <kubectl version> --s3-bucket <bucket name> --s3-key <file key>
```

When running `hokusai setup` `staging.yml` and `production.yml` are created in the `./hokusai` project directory. These files define what Hokusai refers to as "stacks", and Hokusai is opinionated about a workflow between a staging and production Kubernetes context.  Hokusai commands such as `stack`, `env`, `deploy` and `logs` require invocation with either the `--staging` or `--production` flag, which references the respective stack YAML file and interacts with the respective Kubernetes context.

### Working with environment variables

* `hokusai env <create|get|set|unset|delete>`

  - `hokusai env create` - Create the Kubernetes configmap object `{project_name}-environment`
  - `hokusai env get` - Print environment variables stored on the Kubernetes server
  - `hokusai env set` - Set environment variables on the Kubernetes server. Environment variables are stored for the project as key-value pairs in the Kubernetes configmap object `{project_name}-environment`
  - `hokusai env unset` - Remove environment variables stored on the Kubernetes server
  - `hokusai env delete` - Delete the Kubernetes configmap object `{project_name}-environment`

Note: Environment variables will be automatically injected into containers created by the `hokusai run` command but must be explicitly referenced in the stack container yaml definition using `envFrom`.

### Working with stacks

* `hokusai stack <create|update|delete|status>`

  - `hokusai stack create` - Create a stack.
  - `hokusai stack update` - Update a stack.
  - `hokusai stack delete` - Delete a stack.
  - `hokusai stack status` - Print the stack status.

### Working with deployments

* `hokusai deploy` - Update the Kubernetes deployment to a given image tag.
* `hokusai promote` - Update the Kubernetes deployment on production to match the deployment running on staging.
* `hokusai refresh` - Refresh the project's deployment(s).
* `hokusai history` - Print the project's deployment(s) history.
* `hokusai gitdiff` - Print a git diff between the tags deployed on production vs staging.
* `hokusai gitlog`  - Print a git log comparing the tags deployed on production vs staging, can be used to see what commits are going to be promoted.

### Running a command

* `hokusai run` - Launch a container and run a given command. It exits with the status code of the command run in the container (useful for `rake` tasks, etc).

### Retrieving container logs

* `hokusai logs` - Print the logs from your application containers
