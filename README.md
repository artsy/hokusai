HOKUSAI
-------

Artsy Docker Development Toolkit

<a href="https://www.artsy.net/article/artsy-editorial-7-things-you-didn-t-know-about-hokusai-painter-of-the-great-wave"><img height="300" src="hokusai.jpg"></a>

## About

Hokusai works with [Kubernetes](https://kubernetes.io/) and [Docker](https://www.docker.com/) to manage a container driven workflow, from development to testing and deployment.

## Requirements

1) [Docker](https://docs.docker.com/)

If you use homebrew, install Docker for Mac with: `brew tap caskroom/cask && brew cask install docker`

2) [Docker Compose](https://docs.docker.com/compose/)

If you installed Docker for Mac, `docker-compose` is also installed. Otherwise install with: `(sudo) pip install docker-compose`.

## Setup

Install Hokusai with `(sudo) pip install .` and `hokusai` will be installed on your PATH.

Ensure the environment variables `$AWS_ACCESS_KEY_ID`, `$AWS_SECRET_ACCESS_KEY`, `$AWS_REGION` and optionally, `$AWS_ACCOUNT_ID` are set in your shell.

Run `hokusai install` to install Hokusai's dependencies.  You'll need to provide the S3 bucket name and key of your org's kubectl config file.

To upgrade to the latest changes in this repo, run `(sudo) pip install --upgrade .`

## Use

```
hokusai --help
hokusai {command} --help
```

You can add `-v` (Verbose) to most commands which will show you details of the individual commands Hokusai will run.

### Installing Dependencies

* `hokusai install` - installs and configures kubectl

Required options:
  - `--s3-bucket`: The S3 bucket containing your org's kubectl config file
  - `--s3-key`: The S3 key of your org's kubectl config file

### Setting up an existing project

* `hokusai setup` - Writes hokusai project config to `hokusai/config.yml`, creates test, development and production yml files alongside it, and adds a Dockerfile to the current directory.

Required options:
  - `--aws-account-id`: Your AWS account ID - can be found in your AWS account console.
  - `--framework`: "rack", "nodejs", or "elixir".

* `hokusai check` - Checks that Hokusai dependencies are correctly installed and configured for the current project

### Development

* `hokusai dev` - Boot a development stack as defined in `hokusai/development.yml`.
* `hokusai test` - Boot a testing stack as defined in `hokusai/test.yml` and exits with the return code of the test command.


### Working with Images

* `hokusai push` - Build and push and image to the AWS ECR project repo.
* `hokusai tags` - List all image tags in the AWS ECR project repo.

### Working with Kubernetes
Hokusai uses `kubectl` to connect to Kubernetes. You first need to make sure `kubectl` is installed and you have proper config setup for connecting to your Kubernetes. Hokusai `install` commands provide basic setup for this:
```bash
hokusai install --help
```
Recommended approach is to upload your `kubectl` config to S3 and use following command to install it:
```bash
hokusai install --s3-bucket <bucket name> --s3-key <file key>
```

The following commands refer to a Kubernetes context.  By convention, Hokusai looks for both a `staging` and a `production` context available to `kubectl` (usually in `~/.kube/config`).

When running `hokusai setup` `staging.yml` and `production.yml` are created in the hokusai project directory, which Hokusai then matches to its respective context.  These files define what Hokusai calls "Stacks".

Similarly, Hokusai creates "Secrets" within a given context by managing a Kubernetes secret object named `{project-name}-secrets`.  Hokusai is not limited to these two contexts, and you can add other contexts as well as other yml files to support them.

Run `hokusai check` to check that `staging` and `production` contexts are available to `kubectl`.

### Working with Secrets

* `hokusai secrets get` - Prints secrets stored on the Kubernetes server
* `hokusai secrets set` - Sets secrets on the Kubernetes server. Secrets are stored for the project as key-value pairs in the Kubernetes Secret object `{project_name}-secrets`
* `hokusai secrets unset` - Removes secrets stored on the Kubernetes server

Note: Secrets will be automatically injected into containers created by the `hokusai run` command but must be explicity referenced in the stack container environment via `secretKeyRef`.

### Working with Stacks

* `hokusai stack create` - Create a stack in the given Kubernetes context.
* `hokusai stack update` - Update a stack in the given Kubernetes context.
* `hokusai stack delete` - Delete a stack in the given Kubernetes context.
* `hokusai stack status` - Print the stack status in the given Kubernetes context.

### Deployment

* `hokusai deploy` - Update the Kubernetes deployment to a given image tag.
* `hokusai promote` - Update the Kubernetes deployment in a given context to match the deployment in another context

### Running a console

* `hokusai run` - Launch a container and run a given command. It exits with the status code of the command run in the container (useful for `rake` tasks, etc).

## Development

Install development packages: `pip install -r requirements.txt`

## Testing

`python -m unittest discover test`

Use the `DEBUG=1` flag for boto logging
