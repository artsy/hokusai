## v0.4.8

[Documentation](https://github.com/artsy/hokusai/blob/v0.4.6/README.md)

### Notable changes since v0.4.6

* 804eba6 Release to PyPi, DockerHub, and GitHub
* f370081 git-remote only in config file
* 87f02fa refactor config.get and use env var precedence before project yaml config
* 8be10ce refactor config.get and add run_tty config option
* d923476 add git_remote fallback to config
* b5f5c6a update config to parse either _ or -, fallback to env vars or set default values per property
* 9b4bad6 minor refactor in hokusai/services/configmap.py
* 23d3fd3 Fix install dependency make task references
* bac0f4b Release version and latest binaries for every version git tag
* 5f00acb Prevent verbosity from leaking between specs
* 4393b6c Configure CI to build and release hokusai binaries
* 831f3e7 Update Circle CI configuration to use virtualenv
* 64f8eb3 Add Circle CI config
* 4b4d6da Code review comment + update readme
* 91023b4 Add org name
* d3248c5 First pass in adding gitcompare
* 293a961 Report error when kubectl unavailable during context check
* 2c5dd5e add long description for pip repo
* 63472d5 Docker alpine build
* e9ed3a3 remove sudo recommendation from install instructions in README.md
* 4698007 Determine if AWS credentials are valid via AWS API call
* b6e2a84 Update hokusai check command to find executables via which

## v0.4.6

[Documentation](https://github.com/artsy/hokusai/blob/v0.4.6/README.md)

### Notable changes since v0.4.5

* 4a89e3d Fix build in push and add --skip-latest option and logging in build
* 8b38b51 copy non-template files on setup
* ffcfc94 add namespace to all k8s commands and small fixes
* 6726051 update output formatters for k8s_status and images
* 53eef13 rename common.yml to build.yml - maintain backwards compatibility
* 1e466e1 generalize setup further and drop port option - can be set in custom templates
* 2d472f3 Refactor setup to use git remote and path for a given project type and accept custom template variables
* 20518c9 Bust the registry cache when creating a new repository - fixes https://github.com/artsy/hokusai/issues/69
* 9417d99 always resolve git SHA1 tags in pipeline and deploy commands
* 022e2b3 update review_app commands to support all staging/production commands
* 01d226d add --deployment option to refresh / restart
* c5da8d2 Update README with Artsy-specific config link
* 76c4fa0 Fix using context on k8s_update and not use yaml_file_name


## v0.4.5

[Documentation](https://github.com/artsy/hokusai/blob/v0.4.5/README.md)

### Notable changes since v0.4.4

* 1a9822a resolve this directory in hokusai.spec
* 5746219 (origin/fea-push-git-tags, fea-push-git-tags) push tags to specified git remote if provided on deploy and promote
* b6406df remove image digest from registry images output
* 2561c03 remove history command
* 3c43592 check project repo exists before updating deployment or running a command
* 5738ff4 bugfix in hokusai/services/deployment.py
* 93219ea include Pyinstaller spec
* 10a7e12 updates to pyinstaller build steps
* ec590d7 updates to distribute with PyInstaller
* 8011f78 read VERSION from module
* 96f8f52 fix Yarn failure in CI build


## v0.4.4

[Documentation](https://github.com/artsy/hokusai/blob/v0.4.4/README.md)

### Notable changes since v0.4.3

* 3a45ed0 add interactive 'console' command with click-repl
* 74ce4da aws region fallbacks with boto2 compatibility and default to us-east-1
* aaa241a fix flag collision in logs command -- timestamps now use short flag -s
* 42b3fe7, a034af5, 45628cf update documentation


## v0.4.3

[Documentation](https://github.com/artsy/hokusai/blob/v0.4.3/README.md)

### Notable changes since v0.4.2

* ce94d62 fix ECR repo auto-discovery
* d79f707 add restart command as alias for refresh


## v0.4.2

[Documentation](https://github.com/artsy/hokusai/blob/v0.4.2/README.md)

### Notable changes since v0.4.1

* hokusai test accepts cleanup/no-cleanup option
* Add review_app command group
* update dockerignore template for Python
* remove aws-account-id and aws-ecr-region setup flags and config values and fetch from boto


## v0.4.1

[Documentation](https://github.com/artsy/hokusai/blob/v0.4.1/README.md)

### Notable changes since v0.4.0

* d7b50ce fixes to setup templates
* 9a3273f default templates
* 723c657 Convert all yml to come from templates, first pass hardcoded location.
* 159b5da rename remote_environment to kubernetes / k8s
* 58bb825 remove references to remote
* ab759d8 Add --stop option to dev command to clean up services
* 6e8b33e Fix config error
* 388569e Template deploy user and service port default to 8080
* 6c4f87a Change dev run command to use docker-compose run and launch a new container
* d4c85cd Always Be Building (--build/--no-build flags)
* 7149d1b Add .dockerignore to setup command
* bcbfce8 allow local config file as an alternative to an s3 bucket/key


## v0.4.0

[Documentation](https://github.com/artsy/hokusai/blob/v0.4.0/README.md)

### Notable changes since v0.3.5

* c2790e7 verbose logging in shout_concurrent
* 92b4196 drop local / remote top-level command groups - create staging, production and pieline groups
* 2a654c3 bugfix in ./hokusai/commands/env.py
* 29299af add --internal flag to setup
* d578d5f add deployment subcommand - change deploy to deployment update, include history refresh and promote
* 5269c6b create hokusai registry command group
* 7cec07b replace stack with (remote) environment
* 409539a move setup command to top level
* 5dab4d3 nest dev commands inside local
* 907f20f refactor local / remote logs --tail and --follow options
* aed338a change dev_shell to dev_run
* afcb035 refactor click commands into groups - local, remote, env - drop dev and stack hacks
* 809175a refactor top-level commands into nested groups
* da166b0 bugfix in hokusai/services/deployment.py and wait for refreshes to finish
* 37f1eae fix broken import
* f928864 Change deploy hooks nomenclature: before to pre and after to post
* cecc967 Refactor return codes to use exception handling to abort execution
* 6e08148 Add gitlog, rename diff to gitdiff
* dcea815 Consolidate running concurrent subprocesses
* 1575b37 Error handling syntax fixes
* b891fbe update dependencies in setup.py
* cce8ee6 update concurrency in logs command
* b38c8df update check command
* 7d15b21 wait for deployments to finish when updating deployments
* 36255dd be more lenient on default AWS env vars
* 0d08068 hack terminal width
* 5d46b78 apply pod constraints for commands via node selector labels if provided
* 6eaadd6 PEP8 styling
* ab6b2fd implement deploy hooks
* e511b3e update command inline documentation
* e43f51f alias --tail for --follow option where available
* dfcec9e Add instructions to output for dev and test commands
* feb590f change dev command follow to detach - swap --skip-build with --build option for dev and test -also catch signals in dev to guard against orphaned running containers
* f67fe58 remove unreferenced service wrapper
* 8091034 bump click dependency
* a856592 formatting output around deploys and promotions

## v0.3.5

[Documentation](https://github.com/artsy/hokusai/blob/v0.3.5/README.md)

### Notable changes since v0.3.4

* 9553910 hotfix hokusai push
* b68c74b distribute script fixes

## v0.3.4

[Documentation](https://github.com/artsy/hokusai/blob/v0.3.4/README.md)

### Notable changes since v0.3.3


* f4d2cb8 distribute Hokusai as a Docker image
* 326469f formatting fixes
* 694f7dc bring back build command - consolidate docker compose stack names and clean up containers on test

## v0.3.3

[Documentation](https://github.com/artsy/hokusai/blob/v0.3.3/README.md)

### Notable changes since v0.3.2

* 719a71b fix hokusai dev to always cause docker-compose up which is needed to create the default network
* 66b0e8e generalize env setup in GettingStarted.md
* c7ef75a add installation note to try --ignore-installed flag if pip install fails
* 6f5b16c add dev build subcommand
* 7f682d7 update error handling and output


## v0.3.2

[Documentation](https://github.com/artsy/hokusai/blob/v0.3.2/README.md)

### Notable changes since v0.3.1

* b7d24c3 hokusai diff finds git sha1 tag from production and staging tags
* 6f75d0b force aws account id to string, even if user has changed it to int in hokusai config yaml
* b1fc5d1 remove -e flag from TestECR.test_get_login
* 1eae772 add hokusai diff command
* f27db8b fixes in project environment scaffolding in setup command
* b8541d0 add --overwrite option to push command to separate behavior overwriting repo image from --force
* 6f105e0 update check command
* a700906 remove service dependencies from setup command
* ebc0b1e push command accepts only one tag - checks working directory is clean and tag does not already exist
* 9c02a65 Remove -e from docker login command

## v0.3.1

[Documentation](https://github.com/artsy/hokusai/blob/v0.3.1/README.md)

### Notable changes since v0.3

* 8276c18 bugfix in bin/hokusai
* a6e7782 fetch tags before creating a new one
* 2507748 bail out of distribute.sh if version tag exists


## v0.3

[Documentation](https://github.com/artsy/hokusai/blob/v0.3/README.md)

### Notable changes since v0.2

* 957babe add two replicas for production web deployment and update tests
* de5e74b refactor run to CommandRunner, add --migration flag to deploy and promote commands
* 6786351 fix env vars passed to run command

## v0.2

[Documentation](https://github.com/artsy/hokusai/blob/v0.2/README.md)

### Notable changes since v0.1

* 150a4b9 make hokusai run containers more grep-able as they do not seem to support labels
* 49e7d5f update distribute.sh to tag versions
* bc5e1a0 add deployment history
* 785b69a template project volume synced to /app in setup command
* d1d0203 catch ImageAlreadyExistsException when retagging images on deploy
* cde590d Revert "add --skip-tags option for deploy"
* fb8ce9b expand dev command to include start,stop,status,logs,shell,clean subcommands
* a75c5de add --skip-tags option for deploy
* eaee99c ensure zero-downtime deployment with rollingUpdate / maxUnavailable: 0
* ff4ef6a update README
* 59cad28 simplify stack status command using label selector
* 42c287e use ECR api to retag images directly
* ba292cf bugfix in hokusai/commands/env.py
* 59eb48c bugfix in promote click command
* 5f695db add distribute.sh
* 01991da compose service and deployment names with project name and component
* a356105 fixes for v1.0b1 - label selectors, stack creation kubectl command and rabbitmq alpine image
* 0e6c260 fix support for multiple deployments using the 'project' label - add refresh command
* 174738e store environment in configmaps rather than secrets
* bdc2a90 (tag: v1.0-b1) update version to 1.0-b1 - add version command
* 551aff5 update README and cli help text for configure and env commands
* d82cb74 rename command secrets to environment - store env vars in secret object '{project_name}-environment
* 34dea7e rename dependencies command to configure
* deb58d7 update hokusai run to use envFrom
* 48782f5 add envFrom supported in kubernetes 1.6+
* dd9d670 print docker output in hokusai push command

## v0.1

[Documentation](https://github.com/artsy/hokusai/blob/v0.1/README.md)
