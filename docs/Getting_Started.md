## Getting Started

Hokusai aims to provide a smooth CI workflow on a per-project basis.  As such, it is designed to be configured and run from a shell within a project's git repo.

We will assume you have already installed Hokusai and run `hokusai configure`, as detailed in [Setup](../README.md#Setup).

1) Setup Hokusai for a Rails project

```bash
cd ./path/to/my/rails/project/git/repo
hokusai setup
```

(`hokusai setup --help` can report the list of all available options.)

`hokusai setup` will create:
- An ECR repository for your project
- A `Dockerfile` in your project's root directory
- A `.dockerignore` file in your project's root directory
- A configuration folder `./hokusai`.  This folder contains:
  * `config.yml` - Hokusai project configuration
  * `build.yml` - a Docker Compose YAML file used by `hokusai build` and imported by `development.yml` and `test.yml`
  * `development.yml`- a Docker Compose YAML file used by `hokusai dev`
  * `test.yml` - a Docker Compose YAML file used by `hokusai test`
  * `staging.yml` - a Kubernetes YAML file used by `hokusai staging`
  * `production.yml` - a Kubernetes YAML file used by `hokusai production`

The files in `./hokusai` as well as the `Dockerfile` / `.dockerignore` files are meant to be a starting point for development of your specific application's dependencies, and can / should be freely modified, as you customize your Docker build, add service dependencies to your environments, introduce environment variables, or change the container runtime commands.  See [Configuration Options](./Configuration_Options.md) if you want to modify your project's configuration.

You are able to define your own [Jinja templates](http://jinja.pocoo.org/docs/2.10/) and load them from a local directory with the `--template-dir` option, or specify a remote git repository with `--template-remote` and point to a remote path in that repository with `--template-dir`.

See [Artsy Hokusai Templates](https://github.com/artsy/artsy-hokusai-templates) for recommended templates. For example, bootstrap a Rails/Puma project:
```shell
hokusai setup --template-remote git@github.com:artsy/artsy-hokusai-templates.git --template-dir rails-puma
```


Running without these options provides a default configuration.  All other template directories should provide this structure:

- Dockerfile.j2
- .dockerignore.j2
- hokusai/build.yml.j2
- hokusai/development.yml.j2
- hokusai/test.yml.j2
- hokusai/staging.yml.j2
- hokusai/production.yml.j2

All templates are rendered with `project_name` and `project_repo` template variables.  You can reference them like so: `{{ project_name }}`. Additionally, you can pass in custom template variables to `hokusai setup` with the `--var` option.

Any additional `.j2` template files in the template directory and its child directories will be rendered with the provided template variables, and any other regular files will also be copied with the paths relative to the root of the project when running `hokusai setup`.

Artsy devs can find more information on our org-specific templates [in the artsy-hokusai-templates repo](https://github.com/artsy/artsy-hokusai-templates).

2) Check that Hokusai is correctly configured for your project

`hokusai check` will run a series of tests and warn you if it finds anything improperly configured.

3) Run the development environment

`hokusai dev start` will build a Docker image, then start a Docker Compose environment defined by `./hokusai/development.yml`

If this command throws no errors, try interacting with the running environment with:

```bash
hokusai dev status
hokusai dev logs
hokusai dev run bash
```

To shut down the environment's running containers, run `hokusai dev stop`

Container filesystems will be preserved between environment starts and stops, unless you run `hokusai dev clean`, in which case the container filesystems will be deleted.

See [Configuration Options](./Configuration_Options.md) if you want to modify your development environment's configuration.


4) Run the test suite in the test environment

`hokusai test` will build a Docker image, start a Docker Compose environment defined by `./hokusai/test.yml`, run the defined test command in the main (project-name) container to completion, and return its exit code.

See [Configuration Options](./Configuration_Options.md) if you want to modify your test environment's configuration.

5) Build and push an image to ECR

`hokusai registry push` will build and push an image to ECR.  By default, it tags the image as the SHA1 of the HEAD of your current git branch (by calling `git rev-parse HEAD`).  You can override this behavior with the `--tag` option, although this is not recommended as creating builds matched to the SHA1 of Git tags gives you a clean view of your ECR project repository and deployment history.

The command will also tag the image as `latest`.  This image tag should not be referenced in any Kubernetes YAML configuration, but serves only as a pointer, which is referenced when creating a Kubernetes environment.

The command aborts if any of the following conditions is met:
- The working directory is not clean (you have uncommitted changes)
- The working directory contains any files specified in your `.gitignore` file. Running `git status --ignored` will list. 
- The project registry already contains the specified tag

The reason for these conditional checks is that when building, Docker will copy your _entire_ working directory into the container image, which can produce unexpected results when building images locally, destined for production environments!  Hokusai aborts if it detects the working directory is unclean, or any ignored files or directories are present, as it attempts to prevent any local configuration leaking into container images.

Once an image is pushed, you can list the images and tags in the project registry with: `hokusai registry images`.


6) Create the Kubernetes staging environment with `hokusai staging create`

`hokusai staging status` should show all the resources defined in staging.yml.

Get logs by running `hokusai staging logs`

7) Set Kubernetes staging environment and environment variables

```bash
hokusai staging env set FOO=bar
```

After setting environment variables you need to run:

```bash
hokusai staging refresh
```

See [Configuration Options](./Configuration_Options.md) if you want to modify your staging environment's configuration.


8) Create the Kubernetes production environment

```bash
hokusai production create
hokusai production status
hokusai production logs
```

9) Set Kubernetes production environment and environment variables

```bash
hokusai production env set FOO=bar
```

After setting environment variables you need to run:

```bash
hokusai production refresh
```

10) Deploy changes to the Kubernetes staging environment

Create a new commit and push it to the registry with `hokusai registry push` as before.

Deploy the new commit to staging with `hokusai production deploy {TAG}` where TAG is the tag of the commit you just made.

11) Promote the tag deployed on staging to production

```bash
hokusai pipeline promote
```
