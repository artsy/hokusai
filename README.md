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

Ensure the environment variables `$AWS_ACCESS_KEY_ID`, `$AWS_SECRET_ACCESS_KEY`, `$AWS_DEFAULT_REGION` and optionally, `$AWS_ACCOUNT_ID` are set in your shell.

Run `hokusai deps` to install Hokusai's dependencies.  You'll need to provide the S3 bucket name and key of your org's kubectl config file.

To upgrade to the latest changes in this repo, run `(sudo) pip install --upgrade .`

To enable bash autocompletion: `eval "$(_HOKUSAI_COMPLETE=source hokusai)"`

## Use

```
hokusai --help
hokusai {command} --help
```

You can add `-v` (Verbose) to most commands which will show you details of the individual commands Hokusai will run.

### Installing Dependencies

* `hokusai deps` - installs and configures kubectl

Required options:
  - `--s3-bucket`: The S3 bucket containing your org's kubectl config file
  - `--s3-key`: The S3 key of your org's kubectl config file

### Setting up an existing project

* `hokusai setup` - Writes hokusai project config to `hokusai/config.yml`, creates test, development and production yml files alongside it, adds a Dockerfile to the current directory, and creates a project ECR repo.

Required options:
  - `--aws-account-id`: Your AWS account ID - can be found in your AWS account console.
  - `--project-type`: "ruby-rack", "ruby-rails", "nodejs", "elixir", or "python-wsgi.

* `hokusai check` - Checks that Hokusai dependencies are correctly installed and configured for the current project

### Development

* `hokusai dev` - Boot a development stack as defined in `hokusai/development.yml`.
* `hokusai test` - Boot a testing stack as defined in `hokusai/test.yml` and exits with the return code of the test command.


### Working with Images

* `hokusai push` - Build and push and image to the AWS ECR project repo.
* `hokusai tags` - List all image tags in the AWS ECR project repo.

### Working with Kubernetes
Hokusai uses `kubectl` to connect to Kubernetes. You first need to make sure `kubectl` is installed and you have proper config setup for connecting to your Kubernetes. Hokusai `deps` commands provide basic setup for this:
```bash
hokusai deps --help
```
Recommended approach is to upload your `kubectl` config to S3 and use following command to install it:
```bash
hokusai deps --s3-bucket <bucket name> --s3-key <file key>
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

### Running a command

* `hokusai run` - Launch a container and run a given command. It exits with the status code of the command run in the container (useful for `rake` tasks, etc).

### Retrieving container logs

* `hokusai logs` - Print the logs from your application containers

## Development

- Install development packages: `pip install -r requirements.txt`

Hokusai can be run directly with `python bin/hokusai`

[Minikube](https://github.com/kubernetes/minikube)

- [Install](https://github.com/kubernetes/minikube/releases) and [Configure](https://github.com/kubernetes/minikube/blob/master/DRIVERS.md) minikube

  - On Darwin with the xhyve driver:

    ```
    brew install docker-machine-driver-xhyve
    sudo chown root:wheel /usr/local/opt/docker-machine-driver-xhyve/bin/docker-machine-driver-xhyve
    sudo chmod u+s /usr/local/opt/docker-machine-driver-xhyve/bin/docker-machine-driver-xhyve
    curl -Lo minikube https://storage.googleapis.com/minikube/releases/v0.18.0/minikube-darwin-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/
    minikube config set vm-driver xhyve
    ```

- On Debian/Ubuntu with the kvm driver:
  ```
  export DEBIAN_FRONTEND=noninteractive
  sudo curl -L https://github.com/dhiltgen/docker-machine-kvm/releases/download/v0.7.0/docker-machine-driver-kvm -o /usr/local/bin/docker-machine-driver-kvm
  sudo chmod +x /usr/local/bin/docker-machine-driver-kvm
  sudo apt-get -y install libvirt-bin qemu-kvm
  sudo usermod -a -G libvirtd $(whoami)
  newgrp libvirtd
  curl -Lo minikube https://storage.googleapis.com/minikube/releases/v0.18.0/minikube-linux-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/
  minikube config set vm-driver kvm
  ```

Test the installation by running `minikube start` then `minikube status`.  This should show `minikubeVM: Running` as well as `localkube: Running`.

Note: To access minikube's docker daemon directly. run `eval $(minikube docker-env)`.  `docker` commands should now  reference the docker daemon running on the minikube VM.  `docker ps` should show Kubernetes service component containers kube-dns and kubernetes-dashboard`

## Testing

All tests can be run with `python -m unittest discover test`.

Integration tests require `kubectl` installed and configured and minikube running locally (`minikube start`).

Only run unit tests: `python -m unittest discover test.unit`
Only run integration tests: `python -m unittest discover test.integration`

Tests for specific modules, TestClasses, or even methods can be run with `python -m unittest test.unit.test_module.TestClass.test_method`

Set the `DEBUG=1` environemnt variable for boto logging
