## v1.0.0

[Documentation](https://github.com/artsy/hokusai/blob/v1.0.0/README.md)

### Notable changes since v0.5.18

* ed3d1ae feat: track deployed project version in a Kubernetes deployment label
* 3b8a7e6 feat: drop support for Python 2.x, allow installation for Python 3.7+ only

## v0.5.18

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.18/README.md)

### Notable changes since v0.5.17

* b804c4d feat: add digest support to CommandRunner:run() (#276)

## v0.5.17

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.17/README.md)

### Notable changes since v0.5.16

* 126b373 feat: discontinue ecr repository exists test before run a kubectl command #272

## v0.5.16

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.16/README.md)

### Notable changes since v0.5.15

* 3c58b49 feat: Introduce 'hokusai registry retag' command. (#262)

## v0.5.15

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.15/README.md)

### Notable changes since v0.5.14
* 7930029 fix: python 3 fixes
* b7cd7d7 documentation updates
* 19a13b1 fix: replacing invalid character with '-' for the pod name
* 80fed3b fix: reverted promt-toolkit version due to mismatch with python 3.5

## v0.5.14

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.14/README.md)

### Notable changes since v0.5.13

* 9d43922 fix: skip project config check when configuring hokusai (#249)
* 9c0f660 fix: filter returns iterable and not a list in py3 so cast to list
* 3c69774 fix: urlretrieve import
* e16f9b6 feature: Hokusai Lite

## v0.5.13

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.13/README.md)

### Notable changes since v0.5.12

* adfbdfb fix: check command uses TemplateSelector
* 53e9020 Install JQ in hokusai image as it's required for the new version of slack orb
* 75b1be4 fix: treat HokusaiError separately from CalledProccessError on exit
* e2edea5 fix: mask CalledProcessError msg and output attributes
* 7bc6cc1 hotfix: upgrade pip and wheel dependencies in order to fix pip errors

## v0.5.12

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.12/README.md)

### Notable changes since v0.5.11

* a547787 fix: use write mode for named tempfiles explicitly
* 2327502 fix: don't remove teh entire hokusai temp directory - another invocation of hokusai may be using it
* 75c851f chore: add a 1-liner to install Hokusai in README.md
* 53d6b65 fix: use a NamedTemporaryFile for rendering Yaml specs
* 65f1759 fix: don't try to print an exception with None as message or output
* 346a610 prefer .j2 ;)
* 4f6fa62 bump docker-compose to 1.25.5
* ad5ad81 fix pip installs - include VERSION in MANIFEST.in
* 900f2bb --enable-framework when running pyenv install in release_version_macos job


## v0.5.11

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.11/README.md)

### Notable changes since v0.5.10

* dc8292c Move release homebrew from a sh file in the main repo to a circleci command
* 9c9ecad refactor circleci workflow so beta releases depend on their test versions
* ac6ba0d cleanup .hokusai-tmp directory on exit unless DEBUG is set
* e1ee684 use the test or development yaml template when building in test or dev environments
* 667d9bb Add get-hokusai.sh
* 1027b21 Fix pyinstaller hidden imports for Python 2 and 3 compatibility
* a6955a9 Fix  traceback and exception  handling
* b0383e6 downcase user when creating a pod name
* b974c75 Merge pull request #212 from izakp/python-3
* 212483f replace pipenv with poetry
* 9bf7f56 fix ssl linking in pyinstaller builds
* 74f85f6 downgrade virtualenv to 15.1.0
* 6f15580 for post deployment git tagging, force git to replace local tags.
* a649dd8 move head builds to beta

## v0.5.10

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.10/README.md)

### Notable changes since v0.5.9

* 7809787 follow extends in rendered docker compose Yaml files to other templates
* fd5e3a7 git fetch tags, has been failing intermittently. Print the actual Git error. Retry up to 3 times. Don't fail the build.

## v0.5.9

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.9/README.md)

### Notable changes since v0.5.8

* 2d2ab3f strip .j2 file extensions when rendering templates
* 59d4eb1 raise HokusaiError if no Yaml file or template found
* 9562696 leave templates in temp dir if DEBUG rather than printing to stderr
* b17976d NamedTemporaryFiles use the local hokusai temp directory as well
* b243069 create a .hokusai-tmp directory for rendered Yaml templates
* 4071e35 rename KubernetesSpec to YamlSpec
* f747e2e use TemplateSelector to find Yaml files and j2 templates for all docker-compose and kubernetes files
* 63eb8b9 Remove legacy docker compose Yaml file hokusai/common.yml
* 104cffe Add TemplateSelector
* f8eae5d render KubernetesSpec as template on review app setup
* 3bd7c85 Update publish-pip make target to run within pipenv
* e4c5af3 (upstream/pvinis-patch-1) Fix markdown

## v0.5.8

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.8/README.md)

### Notable changes since v0.5.7

* 721bf51 Merge pull request #190 from izakp/fea-dynamic-interpolation
* dece53b add ipython / ipnb and jupyter dev dependencies
* c0a83b5 install pyinstaller outside pipenv
* 63846ed Use Pyenv and Pipenv to manage hokusai's py version and dependencies
* fec9f68 serialize / deserialize ConfigMaps as JSON
* f5ba644 missing imports in gitcompare / gitlog commands

## v0.5.7

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.7/README.md)

### Notable changes since v0.5.6

* 52d7612 refactor deployment update behavior to account for canary and review apps
* 90deb7e update head releases on master to require all test suites
* 3be6be0 release Docker image tag head on master
* 8949ff4 fix --environment flag in creaste command to accept multiple occurances
* 2f2499a bugfix in hokusai/commands/deployment.py
* f8b56d4 update review app docs
* d28a724 update ECR tests
* a2605e5 trim the ecr.get_images method as it now is the images property
a87c15f Refactor deployments to patch image digests and pipeline to resolve Git SHAs - always use the registry rather than k8s as source of * truth for current deployment tag
* 5b74e0e Add back image digest display to registry images with the --digests option
* eb2f3fa refactor ECR to cache images
* 19caa96 refactor ECR module to provide tags, deployment_tags, current_deployment_tag methods
0393a11 add --configmap option to review_app env copy command to copy other configmaps other than the app's environment and refactor * configmap.py to support this
* 266d542 Add --environment option to staging/production create to bootstrap stack with environment variables
* d641fd0 Add short option -u to --update-config option
* de9afff Add --update-config and --filename options to pipeline promote
* 4d9dd48 Update env get to sort results
* c13c985 Install bash in hokusai image
* 142310f Update README with updated installation instructions

## v0.5.6

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.6/README.md)

### Notable changes since v0.5.5
* c6f8338 Add a short option -f for --filename ( -fi in dev logs command )
* 07bea52 Add --update-config and --filename options to staging/production deploy
* 1896d71 Fix ECR integration tests for boto update
* f2fa240 Update yaml-file-name to filename and refactor commands / fix kubernetes integration tests
* 1d93ee6 Add a --service-name option to test command to get the return value from a different docker-compose service
* 017f03c Add a global config file `~/.hokusai/config.yml` to run hokusai configure with no arguments but keep backwards compatibility
* 1b33220 Add a --dry-run flag to staging/production update and pass through to kubectl apply
* fdb2e6b Install the aws cli and iam authenticator in the docker image
* bb74eda Loosen dependencies
* 88220af Create and delete env configmap with stack
* 05c4bcf Add the option to override Yaml filename when building, test, dev, staging production and pushing images
* b6f7725 Add registry pull command


## v0.5.5

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.5/README.md)

### Notable changes since v0.5.4
* d31a771 create tar archive upon release
* fdec578 fetch from remotes before running gitdiff and gitlog commands
* 1c7a4a8 add checks to staging and production updates command so they are run on up-to-date checkouts of master
* 5867d6b get test kube context before scrubbing the environment
* 9879cd2 strip all HOKUSAI_ env vars from environment before running the test suite
* e44e7a5 Add mask argument to shout_concurrent function
* 8b65615 mask verbose output - add a mask when shelling out to docker login


## v0.5.4

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.4/README.md)

### Notable changes since v0.5.3
* 987a77d add --label option to logs to filter by additional label selectors
* a10105f print newline only after verbose log line
* 1cdb7b9 add the --previous option to logs commands
* 395d57d use a unique tmp dir to download and configure kubectl
* 36316e7 refactor printing always via smart_str and add some spacing
* 538f5d5 add --timeout flag to deploy and promote and patch deployments with progressDeadlineSeconds when rolling out
* 8cf1ce4 add flags --reverse-sort, --limit and --filter-tags to hokusai registry images
* 93dd0e1 update docs/Command_Reference.md with a note on deployment rollout behavior
* 4730592 refactor post-deploy steps to attempt post-deploy hook, pushing Git and ECR tags and print warnings if any fail before exiting 1 - fix CommandRunner.run so config value run-tty is not respected when running migrations, pre-deploy or post-deploy hooks
* 3061785 change order of precedence for configuration - project-specific config takes precedence over environment variable fallbacks
* 97fedd9 fetch from git-remote before creating or pushing tags
* a835e28 update docs for git-remote config option as it does not apply to review apps as well as run-constraints set via an env var
* 2d91f25 fix parsing run-constratins from an env var - accept a comma-delimited string and parse as a list
* 6ea6190 add hokusai.lib.constants and always-verbose to config
* d2b1da4 explicity tag git deployment tags at the tag to be deployed rather than HEAD
* 2b78d57 add the congif options follow-logs, tail-logs and run-constraints
* 76f4ccb call Docker.build() in commands/development.py and commands/test.py rather than passing the --build option to docker-compose so pre- and post-build hooks are executed

## v0.5.3

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.3/README.md)

### Notable changes since v0.5.2
* d23aafc DRY up references to development, test, build and common yml files
* 867da74 update return value of hokusai/commands/logs.py
* 3295d9f remove the kubectl timeout flag and rely on deployment config to specify progressDeadlineSeconds to orchestrate deployment rollouts (note - this also fixes issues with pipeline commands referencing sidecar containers running alongside application containers)
* 708ffdd create and push git tags individually with --no-verify

## v0.5.2

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.2/README.md)

### Notable changes since v0.5.1
* 2f68593 refactor and DRY-up calls to docker-compose build and add pre-build and post-build hooks
* ca89edf refactor gitcompare - add org-name as first, required option
* 76587b1 patch deployment targets only if the project repo matches
* 39ad325 properly quote json for bash

## v0.5.1

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.1/README.md)

### Notable changes since v0.5.0
* cd7b48a More helpful error messages in hokusai/lib/config.py
* c027a4c update hokusai-required-version check to use PEP-440 version specifiers - add the packaging lib
* c785e39 change config key required-version to more explicit hokusai-required-version, refactor config check and add tests and docs
* 3a5234d refactor command decorator check config and allow commands like version and setup to opt-out and check required-version against current version if project specifies it
* 82d5129 add openssh client to Docker build
* 3deea30 lock docker-compose version to 1.22.0 in Dockerfile
* e352309 one-liner for downloading Pyinstaller binaries for your os
* f8a3564 remove distribute.sh

## v0.5.0

[Documentation](https://github.com/artsy/hokusai/blob/v0.5.0/README.md)

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
