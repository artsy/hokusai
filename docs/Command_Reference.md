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

* `hokusai [staging|production] deploy` - Update the project's deployment(s) for a given environment to reference the given image tag and update the tag (staging/production) to reference the same image.
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
  - `hokusai pipeline promote` - Update the project's deployment(s) on production with the image tag currently deployed on staging and update the production tag to reference the same image.

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
2022-01-25 06:21:59-05:00 | staging--2022-01-25--12-03-28, production--2022-01-25--14-24-53, 2db717382fa14af5e4bf9c01b62f75afdb0f04d0
2022-01-24 11:38:27-05:00 | production--2022-01-24--19-41-44, staging--2022-01-24--17-24-07, a8227694da735dc03c8ba50928325d84e4b2846b
2022-01-24 04:28:35-05:00 | staging--2022-01-24--09-54-36, production--2022-01-24--13-24-20, 0a5e50afe4abf4bb684a7600ce781ac8b1482d3d
2022-01-21 06:27:31-05:00 | staging--2022-01-21--11-50-53, production--2022-01-21--16-36-31, a9328fd344a7e0168244b18d38e14364bc6270fb
2022-01-19 21:14:11-05:00 | staging--2022-01-20--02-45-36, 77c6021a1dc0838b42023bf5ceef06937d10fdfe, production--2022-01-20--13-18-53
2022-01-17 09:54:35-05:00 | production--2022-01-18--14-33-27, 6e6fa628360df94a9457a5df1bbf0b8d772f02cd, staging--2022-01-17--15-54-39
2022-01-14 10:46:31-05:00 | staging--2022-01-14--16-18-02, 6576adaf6b668b1ce9f2582120b3ac780bad10ac, production--2022-01-17--13-21-50
2022-01-12 17:54:19-05:00 | production--2022-01-13--15-46-22, 5ff56d377f58e3a2fae5e496101e11cbeb232025, staging--2022-01-12--23-22-45
2022-01-12 09:43:28-05:00 | c22af9b552f0b906ec675c87be70413f451b011c, production--2022-01-12--19-57-46, staging--2022-01-12--15-25-18
2022-01-11 15:37:24-05:00 | production--2022-01-12--13-22-21, staging--2022-01-11--21-08-37, 611a371e6ccce44eebfb7fb1db54a661ed3564b6
2022-01-10 08:54:49-05:00 | staging--2022-01-10--14-53-55, a4ed90bfa0ff962fb5dc3970945c1b58860145ce, production--2022-01-10--15-17-14
2022-01-07 12:32:08-05:00 | 59fe678ba18fb2101ff442dea4dc85f9a8209e3c, production--2022-01-10--13-21-20, staging--2022-01-07--18-12-40
2022-01-05 14:53:52-05:00 | staging--2022-01-05--20-35-15, production--2022-01-05--20-58-02, 6559b22c88bc756dc591238c7c7ffe25a552830d
2022-01-03 07:11:47-05:00 | 1dff1e54711d7e562a478fa512539efe70f1921d, production--2022-01-03--12-51-09, staging--2022-01-03--12-38-50
2021-12-27 07:50:58-05:00 | 0a4abbffe1f66164c0275ed1b380bb8963aec443, production--2021-12-27--13-34-19, staging--2021-12-27--13-19-45
2021-12-22 15:28:05-05:00 | ea0b4414606745bc2216bcb054a5a2bd381781e5, production--2021-12-24--13-19-00, staging--2021-12-22--20-52-01
2021-12-22 03:05:39-05:00 | production--2021-12-22--13-24-23, f761a4713e9550dc9eceaed1ef10754d26addd33, staging--2021-12-22--08-30-28

81 more images available
```

Notice that we filter by the `production` tag with `--filter-tags production`, and that currently image `9718ddb9334c3e9b2a0a0ffa5d744e1ca91d5cb3` is currently in production. Only the current one will have the `production` tag but previous images will have `production-<timestamp>`.
 
If current production image is causing issues, pick the prior production image, in this case it's right below: `84fd6dcd9b115482e2b1d2981c31f4c8bc97a015` (also tagged as `production--2022-01-26--14-17-47` and `staging--2022-01-26--11-55-47`)
```bash
$ # Time to rollback 
$ hokusai production deploy 84fd6dcd9b115482e2b1d2981c31f4c8bc97a015
```
This will also work:
```bash
$ # Rollback with a more readable tag
$ hokusai production deploy production--2022-01-26--14-17-47
```