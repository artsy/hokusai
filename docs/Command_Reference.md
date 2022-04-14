## Command Reference

For any command, you can access the help documentation via the CLI:

```bash
hokusai --help
hokusai {command} --help
```

You can add `-v` / `--verbose` to most commands which will show you details of the individual commands Hokusai will run.

For an interactive console session, run `hokusai console`.  All commands are available within the session.  Use TAB to autocomplete Hokusai commands and `:help` for console help.

### Configuring Hokusai for your organization

* `hokusai configure` - installs and configures kubectl

Required options:
  - `--kubectl-version`:  The version of your Kubernetes clusters
  - `--s3-bucket`: The S3 bucket containing your organization's kubectl config file
  - `--s3-key`: The S3 key of your organization's kubectl config file

Hokusai uses `kubectl` to connect to Kubernetes and the [boto3](https://github.com/boto/boto3) library to interact with AWS ECR.

Make sure you have set the environment variables `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY` in your shell / `~/.bash_profile`.

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
* `hokusai build` - Build the docker image defined in ./hokusai/build.yml.


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

* `hokusai [staging|production] deploy` - Update the project's deployment(s) for a given environment to reference the given image tag and update the tag (staging/production) to reference the same image. Patch each deployment's `app.kubernetes.io/version` label which is used to track the version of the app deployed. Use the digest for the label's value. Due to Kubernetes' 63 characters limit on a label, only 2nd half of the digest string is used.
* `hokusai [staging|production] [refresh|restart]` - Refresh the project's deployment(s) by recreating the currently running containers.

* `hokusai [staging|production] env` - Interact with the runtime environment for the application
  - `hokusai [staging|production] env get` - Print environment variables stored on the Kubernetes server
  - `hokusai [staging|production] env set` - Set environment variables on the Kubernetes server. Environment variables are stored for the project as key-value pairs in the Kubernetes configmap object `{project_name}-environment`
  - `hokusai [staging|production] env unset` - Remove environment variables stored on the Kubernetes server

* `hokusai [staging|production] run` - Launch a container and run a given command. It exits with the status code of the command run in the container (useful for `rake` tasks, etc). Use single quotes around your command string if it contains whitespace.
  - Use the flag `--tty` to attach your terminal, if your command is interactive. E.g. `hokusai production run --tty 'bundle exec rails c'` launches an interactive console for a Rails project.
  - The flag `--help` shows other flags that might be helpful.
* `hokusai [staging|production] logs` - Print the logs from your application containers


### Working with review apps

Review apps can be created and managed with `hokusai review_app`.

See full details in the [Review App reference](Review_Apps.md).

### Working with the Staging -> Production pipeline

* `hokusai pipeline` - Interact with the project's' staging -> production pipeline
  - `hokusai pipeline gitdiff` - Print a git diff between the tags deployed on production vs staging.
  - `hokusai pipeline gitlog`  - Print a git log comparing the tags deployed on production vs staging, can be used to see what commits are going to be promoted.
  - `hokusai pipeline gitcompare --org-name <your org name in githug>` - Print a git compare url for comparing whats on staging with production.
  - `hokusai pipeline promote` - Update the project's deployment(s) on production with the image tag currently deployed on staging and update the production tag to reference the same image. Update `app.kubernetes.io/version` label as mentioned for `hokusai [staging|production] deploy`.

### A note on deployment rollouts

When running `hoksuai [staging|production] deploy` or `hokusai pipeline promote`, Hokusai takes the following steps:
1) Selects all the project's deployments (those matching the label selectors "app={project_name},layer=application").
2) Attempts to run a `--migration` command, if specified.  If this command fails, Hokusai exits with the return code of this command.
3) Attempts to run a `pre-deploy` hook, if specified.  If this command fails, Hokusai exits with the return code of this command.
4) Patches the deployment's containers that run the application image (those that contain the project's repository in their `image` field) with the new deeployment tag.
5) Waits for the deployment to roll out.  If the deployment fails to rollout withing the provided `--timeout` (default 10 minutes), Hokusai runs a `kubectl rollout undo` to roll all deployments back automatically, then exits with `1`.
6) Attempts to run a `post-deploy` hook, if defined.  If it fails, Hokusai prints a warning and continues.
7) Attempts to push deployment tags to the project registry.  If it fails, Hokusai prints a warning and continues.
8) Attempts to push deployment tags to Git if `git-remote` is defined in the project's config.  If it fails, Hokusai prints a warning and continues.
9) Finally, Hokusai exits `0` if all steps were successful.  If any of steps `6`, `7` or `8` failed, it exits with `1`.

### How to do a rollback

You can use the command `hokusai registry images` to get a list of all images for your current project. They order from most recent to oldest. To do a rollback use `hokusai production deploy [image_tag]` to get back to a particular version. 

For example, to roll back a problematic production deploy to the last image that was deployed to production, you would do the following:

```bash
$ # List out tags of images pushed to production
$ hokusai registry images --filter-tags production

Image Pushed At           | Image Tags
----------------------------------------------------------
2022-01-27 12:15:21-05:00 | staging--2022-01-27--19-05-54, 9718ddb9334c3e9b2a0a0ffa5d744e1ca91d5cb3, production--2022-01-27--19-43-45, production
2022-01-26 06:16:16-05:00 | staging--2022-01-26--11-55-47, production--2022-01-26--14-17-47, 84fd6dcd9b115482e2b1d2981c31f4c8bc97a015
2022-01-25 11:02:42-05:00 | fcf109fa7db52c538755a4eac1b103ecf83dddce, staging--2022-01-25--16-57-31, production--2022-01-25--17-54-15
...

81 more images available
```

Notice that we filter by the `production` tag with `--filter-tags production`, and that currently image `9718ddb9334c3e9b2a0a0ffa5d744e1ca91d5cb3` is currently in production. Only the current one will have the `production` tag but previous images will have `production-<timestamp>`.
 
If current production image is causing issues, pick the prior production image, in this case it's right below tagged as `production--2022-01-26--14-17-47`
```bash
$ # Time to rollback 
$ hokusai production deploy production--2022-01-26--14-17-47
```
