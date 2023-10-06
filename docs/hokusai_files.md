# Hokusai Files

The following Hokusai files must exist on a user's local environment:

Global file:

- `~/.hokusai.yml` - user's global Hokusai configuration

Per-project files:

- `(project)/hokusai/config.yml` - customizes Hokusai commands' behavior for the project
- `(project)/hokusai/build.yml` - the base docker-compose spec for building the project's Docker image
- `(project)/hokusai/development.yml` - the docker-compose spec on launching a local development stack
- `(project)/hokusai/test.yml` - the docker-compose spec on launching a test stack
- `(project)/hokusai/staging.yml` - the Kubernetes spec for launching the project's Staging resources
- `(project)/hokusai/production.yml` - the Kubernetes spec for launching the project's Production resources

There are samples of project files in [templates directory](../hokusai/templates/hokusai), which you can customize to suit your project. Project-specific files can be [bootstrapped by `hokusai setup` command](./Command_Reference.md#setting-up-a-project).


## The files

This section describes the files in more detail.

### ~/.hokusai.yml

Read by `hokusai configure` and any Hokusai command that makes use of the configuration variables stored in this file. The following configuration variables are supported:

- `kubeconfig_source_uri` - the URI to fetch kubeconfig from, influences `hokusai configure` command
- `kubectl_version` - the version of kubectl to download (must match version of Kubernetes deployment), influences `hokusai cofigure` command
- `kubeconfig_dir` - the directory to install kubeconfig into, influences `hokusai configure` command
- `kubectl_dir` - the directory to install kubectl into, influences any Hokusai command that invokes kubectl

Here's a sample global configuration file:

```
---
kubeconfig-dir: /Users/anja/.kube
kubeconfig-source-uri: s3://acme/k8s/config
kubectl-dir: /Users/anja/.local/bin
kubectl-version: 1.28.0
```

A user would not have this file at the beginning. An admin is expected to [prepare an org-wide version](./Administering_Hokusai.md#create-an-org-wide-hokusai-global-config-file) in advance, which can be obtained by users by running [hokusai configure](docs/Command_Reference.md#configuring-hokusai-for-your-organization) command.


### (project)/hokusai/config.yml

The variables defined in this file are used to customize Hokusai commands' behavior for a particular project. The following variables are supported:

- `hokusai-required-version`: <string> (optional) - A [PEP-440 version specifier string](https://www.python.org/dev/peps/pep-0440/#version-specifiers).  Hokusai will raise an error when running commands if its current version does not satisfy these version specifications.  For example: `~=0.5`, `==0.5.1`, `>=0.4.0,<0.4.6`, `!=0.1.*` are all valid version specifier strings
- `project-name`: <string> (required) - The project name
- `git-remote`: <string> (optional) - Push deployment tags to git remote when invoking the `hokusai [staging|production] deploy` or the `hokusai pipeline promote` commands.  Can either be a local alias like 'origin' or a URI like `git@github.com:artsy/hokusai.git`.  Bound to the `--git-remote` option for these commands.
- `template-config-files`: <list> (optional) - Load template config files from the desired URIs, either `s3://` or a local file path.  See [Kubernetes Yaml Template Processing](#kubernetes-yaml-template-processing) for further details.
- `pre-build`: <string> (optional) - A pre-build hook - useful to inject dynamic environment variables into the build, for example: `export COMMIT_HASH=$(git rev-parse HEAD)`
- `post-build`: <string> (optional) - A post-build hook - useful for image post-processing
- `pre-deploy`: <string> (optional) - A pre-deploy hook - useful to enforce migrations
- `post-deploy`: <string> (optional) - A post-deploy hook - useful for deploy notifications
- `run-tty`: <boolean> (optional) - Attach the terminal to your shell session when invoking `hokusai [staging|production|review_app] run`.  Bound to the `--tty` option for this command, and falls back to by the `HOKUSAI_RUN_TTY` env var.
    - `follow-logs`: <boolean> (optional) - Follow log output when invoking `hokusai [staging|production|review_app] logs`.  Bound to the `--follow` option for this command, and falls back to the `HOKUSAI_FOLLOW_LOGS` env var.
    - `tail-logs`: <integer> (optional) - Tail N lines of log output when invoking `hokusai [staging|production|review_app] logs`.  Bound to the `--tail` option for this command, and falls back to the `HOKUSAI_TAIL_LOGS` env var.
- `run-constraints`: <list of kubernetes label selector strings> - Constrain run containers to Kubernetes nodes matching the label selectors in the form `key=value` by setting the `nodeSelector` field on the container's spec. Bound to the `--constrint` option for `hokusai [staging|production|review_app] run` as well as containers run via the `--migration` flag as well as `pre-deploy` / `post-deploy` hooks triggered by `hokusai [staging|production|review_app] deploy` or `hokusai pipeline promote`.  Falls back to the `HOKUSAI_RUN_CONSTRAINTS` env var, in which case a list is parsed from a comma-delimited string.
- `always-verbose`: <boolean> (optional) - Always pront verbose output.  Bound to the `--verbose` option for various commands, and falls back to the `HOKUSAI_ALWAYS_VERBOSE` env var.

Some of these configuration variables have corresponding environment variables and/or Hokusai command line options. When user specifies a config in multiple ways, the order of precedence is as follows:

- If the configuration variable is bound to a command-line option, the option supplied on the command line always takes precedence.
- If the configuration variable is provided in `(project)/hokusai/config.yml` it is used as the option if not supplied on the command line.
- If an environment variable is set it is used as a fallback.
- The default value from the command-line option is used.

Here's a sample `(project)/hokusai/config.yml` file:

```
---
project-name: test-project
git-remote: git@github.com:acme/test-project.git
hokusai-required-version: ">=1.0.0"
pre-deploy: echo hi
post-deploy: echo bye
template-config-files:
  - s3://bucket/hokusai-vars.yml
```


### (project)/hokusai/build.yml

Used by `hokusai build` command. This file should contain a single Docker Compose Service with `build` spec referencing the root project directory, and any build args (i.e. host environment variables to inject into the Dockerfile).


### (project)/hokusai/development.yml

Referenced by `hokusai dev` commands. It should contain a definition for your project service (extending `(project)/hokusai/build.yml`) as well as development environment variables and any dependent services.


### (project)/hokusai/test.yml

Referenced by `hokusai test`. It should contain a definition for your project service (extending `(project)/hokusai/build.yml`) as well as test environment variables and any dependent services.


### (project)/hokusai/staging.yml

Referenced by `hokusai staging` subcommands. It should contain a `Deployment` and a `Service` definition for the project as well as any dependent deployments and/or services.


### (project)/hokusai/production.yml

Referenced by `hokusai production` subcommands. It should contain at least a `Deployment` and a `Service` definition for the project as well as any dependent Kubernetes resources.


## Kubernetes Yaml Template Processing

In order to support flexible configuration across multiple projects and keep Kubernetes Yaml specs DRY, Hokusai treats files in `(project)/hokusai` as [Jinja](https://jinja.palletsprojects.com/en/2.11.x/) templates. The files are rendered before being passed to Docker Compose and Kubernetes.

The default [template context dictionary](https://jinja.palletsprojects.com/en/2.11.x/templates/#variables) includes the variables `project_name` and `project_repo` and the context can be extended by providing the location of multiple Yaml files to the `template-config-files` project config parameter.  These files must contain a dictionary as a single document.  The dictionaries are merged into the template context dictionary in the order specified.  Any variables defined in the template and not included in the context dictionary will result in Hokusai raising an error, as will invalid operations on a variable, i.e. attempting to access a missing property of a variable of the wrong type.

For advanced template design see Jinja's [template designer documentation](https://jinja.palletsprojects.com/en/2.11.x/templates/).


### Tips on template design

- If you get errors when sending Kubernetes Yaml to the Kubernetes API server, set the `DEBUG` environment variable to print out the rendered Yaml.
- Pay attention to whitespace and indentation in rendered Yaml files.  Use the [whitespace control](https://jinja.palletsprojects.com/en/2.11.x/templates/#whitespace-control) features to strip leading and trailing whitespace and the [indent filter](https://jinja.palletsprojects.com/en/2.11.x/templates/#indent) to control indentation.
- Make use of [template inheritance](https://jinja.palletsprojects.com/en/2.11.x/templates/#template-inheritance) to share config snippets between Yaml templates.  You can extend or include any other template file in the `(project)/hokusai` directory.


## Environment Injection

In order to inject an application's environment into running containers, Hokusai templates each `Deployment` in `(project)/hokusai/staging.yml` and `(project)/hokusai/production.yml` with the following definition:

```
spec:
  spec:
    containers:
      envFrom:
        - configMapRef:
          name: {{ project_name }}-environment
```

This instructs Kubernetes to use the `ConfigMap` object named `{project-name}-environment` as a key-value mapping of environment variables to set in the container runtime environment.  `hokusai [staging|production] env` commands are designed to manage this environment.


## Kubernetes labels and selectors

Hokusai prescribes a deployment strategy and label structure for the `Deployment` and `Service` definitions it creates in `(project)/hokusai/staging.yml` and `(project)/hokusai/production.yml`.

It templates a `Deployment` with the following structure:

```
spec:
  template:
    metadata:
      labels:
        app: {{ project_name }}
        layer: web
        component: application
```

And a `Service` with the following structure:

```
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: {{ project_name }}
    layer: application
    component: web
  type: ClusterIP
```

Custom templates as well as additional Deployments and Services should preserve the label structure `app` / `layer` / `component` label structure.  Hokusai will only target deployments with the `app={project_name},layer=application` label selector when running `hokusai [staging|production]` subcommands.

For example, to add a worker `Deployment` to `(project)/hokusai/staging.yml` or `(project)/hokusai/production.yml` you would create it with the following labels:

```
spec:
  template:
    metadata:
      labels:
        app: {{ project_name }}
        layer: application
        component: worker
```

With this structure, Hokusai will update *both* the web and worker deployments simultaneuosly, which is probably what you want.

If you do not want this, and for example want to include a Redis `Deployment` in `(project)/hokusai/staging.yml` or `(project)/hokusai/production.yml` you would create it with the following labels:

```
spec:
  template:
    metadata:
      labels:
        app: {{ project_name }}
        layer: cache
        component: redis
```

Hokusai would ignore this when `hokusai [staging|production]` commands, but it would be included as part of your application's Kubernetes environment.
