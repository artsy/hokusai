HOKUSAI
-------

<a href="https://en.wikipedia.org/wiki/Hokusai"><img height="300" src="hokusai.jpg"></a>

## About

Hokusai wraps [kubectl](https://kubernetes.io/), [docker](https://www.docker.com/), [docker-compose](https://docs.docker.com/compose/) as well as [git](https://git-scm.com/) with a CLI presenting a CI workflow.

## Requirements

1) [Docker](https://docs.docker.com/)

If you use homebrew, install Docker for Mac with: `brew tap caskroom/cask && brew cask install docker`

2) [Docker Compose](https://docs.docker.com/compose/)

3) [Git](https://git-scm.com/)

If you installed Docker for Mac, `docker-compose` is also installed. Otherwise install with: `(sudo) pip install docker-compose`.

## Setup

Install Hokusai with `(sudo) pip install hokusai` and `hokusai` will be installed on your `PATH`.

Ensure the environment variables `$AWS_ACCESS_KEY_ID`, `$AWS_SECRET_ACCESS_KEY`, `$AWS_DEFAULT_REGION` and optionally, `$AWS_ACCOUNT_ID` are set in your shell.

Run `hokusai configure` to install and configure kubectl.  You'll need to provide the kubectl version matching your Kubernetes deployments, as well as the S3 bucket name and key of your org's kubectl config file.

To enable bash autocompletion: `eval "$(_HOKUSAI_COMPLETE=source hokusai)"`

## Use

```
hokusai --help
hokusai {command} --help
```

You can add `-v` (Verbose) to most commands which will show you details of the individual commands Hokusai will run.

### Installing Dependencies

* `hokusai configure` - installs and configures kubectl

Required options:
  - `--s3-bucket`: The S3 bucket containing your org's kubectl config file
  - `--s3-key`: The S3 key of your org's kubectl config file

### Setting up an existing project

* `hokusai setup` - Writes hokusai project config to `hokusai/config.yml`, creates test, development and production YAML files alongside it, adds a Dockerfile to the current directory, and creates a project ECR repo.

Required options:
  - `--aws-account-id`: Your AWS account ID - can be found in your AWS account console.
  - `--project-type`: `ruby-rack`, `ruby-rails`, `nodejs`, `elixir`, or `python-wsgi`.

* `hokusai check` - Checks that Hokusai dependencies are correctly installed and configured for the current project.

### Development

* `hokusai dev start` - Start the development stack defined in `./hokusai/development.yml`.
* `hokusai dev stop` - Stop the development stack defined in `./hokusai/development.yml`.
* `hokusai dev status` - Print the status of the development stack.
* `hokusai dev logs` - Print logs from the development stack.
* `hokusai dev shell` - Attach a shell session to the stack's primary project container.
* `hokusai dev clean` - Stop and remove all containers in the stack.

### Testing

* `hokusai test` - Start the testing stack defined `hokusai/test.yml` and exit with the return code of the test command.


### Working with Images

* `hokusai push` - Build and push an image to the AWS ECR project repo.
* `hokusai images` - Print image builds and tags in the AWS ECR project repo.

### Working with Kubernetes
Hokusai uses `kubectl` to connect to Kubernetes. Hokusai `configure` provides basic setup for installing and configuring kubectl:
```bash
hokusai configure --help
```
Recommended approach is to upload your `kubectl` config to S3 and use following command to install it:
```bash
hokusai configure --kubectl-version <kubectl version> --s3-bucket <bucket name> --s3-key <file key>
```

When running `hokusai setup` `staging.yml` and `production.yml` are created in the `./hokusai` project directory. These files define what Hokusai calls "stacks", and Hokusai is opinionated about a workflow between a staging and production Kubernetes context.  Hokusai commands such as `stack`, `env`, `deploy` and `logs` require invocation with either the `--staging` or `--production` flag, which references the respective stack YAML file and interacts with the respective Kubernetes context.

### Working with Environment Variables

* `hokusai env create` - Create the Kubernetes configmap object `{project_name}-environment`
* `hokusai env get` - Print envrionment variables stored on the Kubernetes server
* `hokusai env set` - Set envrionment variables on the Kubernetes server. Environment variables are stored for the project as key-value pairs in the Kubernetes configmap object `{project_name}-environment`
* `hokusai env unset` - Remove envrionment variables stored on the Kubernetes server
* `hokusai env delete` - Delete the Kubernetes configmap object `{project_name}-environment`

Note: Environment variables will be automatically injected into containers created by the `hokusai run` command but must be explicity referenced in the stack container yaml definition using `envFrom`.

### Working with Stacks

* `hokusai stack create` - Create a stack.
* `hokusai stack update` - Update a stack.
* `hokusai stack delete` - Delete a stack.
* `hokusai stack status` - Print the stack status.

### Deployment

* `hokusai deploy` - Update the Kubernetes deployment to a given image tag.
* `hokusai promote` - Update the Kubernetes deployment on production to match the deployment on staging.
* `hokusai refresh` - Refresh the project's deployment(s)
* `hokusai history` - Print the project's deployment(s) history
* `hokusai diff` - Print a git diff between the tags deployed on production vs staging

### Running a command

* `hokusai run` - Launch a container and run a given command. It exits with the status code of the command run in the container (useful for `rake` tasks, etc).

### Retrieving container logs

* `hokusai logs` - Print the logs from your application containers

## Development

- Install development packages: `pip install -r requirements.txt`

- To install the package from this repo, clone it and then run `(sudo) pip install --upgrade .`  Alternatively, Hokusai can be invoked directly in this repo with `python bin/hokusai`

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

Some integration tests require `kubectl` installed and configured and minikube running locally (`minikube start`).

Only run unit tests: `python -m unittest discover test.unit`
Only run integration tests: `python -m unittest discover test.integration`

Tests for specific modules, TestClasses, or even methods can be run with `python -m unittest test.unit.test_module.TestClass.test_method`

Set the `DEBUG=1` environemnt variable to print boto logging
