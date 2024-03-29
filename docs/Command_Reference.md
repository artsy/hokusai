# Command Reference

This doc describes Hokusai commands in detail.


## General guide on commands

List all available commands by:

```
hokusai tree
```

Learn more about a command using `--help`:

```
hokusai --help
hokusai {command} --help
```

Run a command with `--verbose` to print more information about what Hokusai is doing under the cover (e.g. shelling out to kubectl).

Also, use Hokusai's interactive console:

`hokusai console`

In the console, tab to autocomplete commands. `:help` for help.


## Global commands

These commands are global, as in, they are not specific to a project. They can be run in any directory on user's local.


### Configuring Hokusai for your organization

* `hokusai configure` - Install and configure kubectl. Rely on config from `~/hokusai.yml` ([the global configuration file](./hokusai_files.md#hokusaiyml)). User-specified values in command line options (e.g. kubectl-dir) supercede corresponding values in `~/.hokusai.yml`. Merge command line options into `~/.hokusai.yml`.

  `~/.hokusai.yml` of course would not exist at first. The org admin is expected to [prepare an org-wide version](./Administering_Hokusai.md#create-an-org-wide-hokusai-global-config-file) which users can then obtain by:

  ```
  HOKUSAI_GLOBAL_CONFIG=s3://bucket/path/to/org/new/config/hokusai.yml hokusai configure
  ```

  `hokusai configure` will read the global config in S3 and write it to `~/.hokusai.yml`, creating the file for the first time.

  Similarly, when an org-wide config (e.g. kubectl version) has changed, the org admin should update S3, and users should re-run the above command to update. `hokusai configure` will overwrite the existing `~/.hokusai.yml`.


## Project-scoped commands

These commands are project-specific. They should be run from a project's Git repo root. Directories mentioned below are all relative to the root dir.


### Setting up a project

* `hokusai setup` - Bootstrap Hokusai for a project. Create an AWS Elastic Container Registry (ECR) for the project. Create [per-project Hokusai files](https://github.com/artsy/hokusai/blob/artsyjian/config/docs/hokusai_files.md).

  The files files are a starting point for development, and you are expected to customize them. If your org (e.g. acme) has templates for these files on Github, say for a Rails project, pull them down by:

  ```
  hokusai setup --template-remote git@github.com:acme/hokusai-templates.git --template-dir rails
  ```

* `hokusai check` - Check that Hokusai dependencies are correctly installed and configured for the current project.


### Local development

* `hokusai dev` - Interact with the development environment defined in [./hokusai/development.yml](./hokusai_files.md#developmentyml).
  - `hokusai dev start` - Start the development environment.
  - `hokusai dev stop` - Stop the development environment, but do not delete container filesystems.
  - `hokusai dev status` - Print the status of the development environment.
  - `hokusai dev logs` - Print logs from the development environment.
  - `hokusai dev run` - Run a command in the development environment's main container (one named by 'project-name' as defined in ./hokusai/config.yml).
  - `hokusai dev clean` - Stop the development environment, and remove container filesystems.


### Testing and building images

* `hokusai test` - Start the test environment defined [`./hokusai/test.yml`](./hokusai_files.md#testyml). Exit with the return code of the test command.
* `hokusai build` - Build the docker image defined in [./hokusai/build.yml](./hokusai_files.md#buildyml).


### Managing images in the registry

* `hokusai registry` - Interact with the project's ECR registry.
  - `hokusai registry push` - Build and push an image to registry.
    Image tag by default is the SHA1 of current Git branch's HEAD (i.e. `git rev-parse HEAD`). Can be overridden with `--tag` (although not recommended because SHA1 allows you to map between tags in the registry with the `image` field in the project's Kubernetes pod's spec).

    A `latest` tag is also created. This tag should not be referenced in any Kubernetes spec. It is meant to serve as a pointer, referenced by `hokusai staging/production create` command.

    The command aborts upon any of the following conditions:
    - The working directory is not clean (there are uncommitted changes)
    - The working directory contains Git-ignored files (i.e. specified in `.gitignore` file)
    - The registry already contains the specified tag

    These conditional checks are safeguards. Docker image build copies the _entire_ working directory into the container image. When building an image locally, files (e.g. `.env`) can be un-expectedly included and then persisted in the registry, and the image might be used in production!

  - `hokusai registry images` - List tags in the registry.


### Working with remotely deployed Staging or Production Kubernetes environments

* `hokusai [staging|production]` - Interact with Kubernetes resources defined in [./hokusai/staging.yml](./hokusai_files.md#stagingyml) or [./hokusai/production.yml](./hokusai_files.md#productionyml).

  - `hokusai [staging|production] create` - Create the resources.
  - `hokusai [staging|production] update` - Update the resources.
  - `hokusai [staging|production] delete` - Delete the resources.
  - `hokusai [staging|production] status` - Print the resources.

  - `hokusai [staging|production] deploy` - Update project's Kubernetes Deployment(s) to reference a certain Docker image tag, and also update the alias Docker image tags (i.e. `staging` or `production`) to point to the deployed Docker image. Patch each Deployment's `app.kubernetes.io/version` label. Use 2nd half of the Docker image digest as the label's value.

  - `hokusai [staging|production] [refresh|restart]` - Re-create project's Deployment(s) containers (without changing their Docker image reference).

  - `hokusai [staging|production] env` - Interact with the application's runtime environment (i.e. project's Kubernetes ConfigMap).
    - `hokusai [staging|production] env get` - Print environment variables.
    - `hokusai [staging|production] env set` - Set environment variables.
    - `hokusai [staging|production] env unset` - Remove environment variables.

    Note on `set` and `unset`: To have the change take effect, run `hokusai [staging|production] refresh`. It re-creates the project Deployment's containers. This is necesssary because Kubernetes does not propogate ConfigMap changes to existing containers.

  - `hokusai [staging|production] run` - Launch a container and run a given command. Exit with the status code of the command. Useful for `rake` tasks, etc. If your command string contains whitespace, single quote it.
    If your command is interactive, use `--tty` flag to attach your terminal (e.g. `hokusai production run --tty 'bundle exec rails c'`).

  - `hokusai [staging|production] logs` - Print the logs from application containers.


### Working with review apps

Review apps can be created and managed with `hokusai review_app`.

Please see [Review App reference](Review_Apps.md).


### Working with the Staging -> Production pipeline

* `hokusai pipeline` - Interact with project's' staging -> production pipeline.
  - `hokusai pipeline gitdiff` - Print a diff between the deployed production Git tag and the deployed staging Git tag.
  - `hokusai pipeline gitlog` - Print a git log comparing the Git tags deployed on production vs staging, to see what commits are going to be promoted to production.
  - `hokusai pipeline gitcompare --org-name <your org name on Github>` - Print a Github URL for staging/production Git comparison.
  - `hokusai pipeline promote` - Update project's Deployment(s) in production to use the same Docker image tag that is being used in staging. Update `production` Docker image tag to point to the same Docker image. Update `app.kubernetes.io/version` label, as mentioned above.


### A note on deployment rollouts

`hoksuai [staging|production] deploy` or `hokusai pipeline promote` perform the following:
1) Select all of the project's Deployments (those matching label selectors "app={project_name},layer=application").
2) If `--migration` command is specified, run it. If the command fails, exit with the return code of the command.
3) If `pre-deploy` hook command if specified, run it. If the command fails, exit with the return code of the command.
4) Patch the Deployment's containers with the new Docker image tag.
5) Wait for the Deployment to roll out. If rollout does not complete within `--timeout` minutes (default 10), run `kubectl rollout undo` to roll all Deployments back automatically, then exit with `1`.
6) If `post-deploy` hook command is specified, run it. If it fails, print a warning and continue.
7) Push deployment Docker tags to the registry. If it fails, print a warning and continue.
8) If `git-remote` is specified in `./hokusai/config.yml`, push deployment Git tags to Github. If it fails, print a warning and continue.
9) Finally, exit `0` if all steps were successful. If any of steps `6`, `7` or `8` failed, exit with `1`.
