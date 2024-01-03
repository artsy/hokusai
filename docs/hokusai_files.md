# Hokusai Files

The following Hokusai files must exist on a user's local environment:

Global files:

- `~/.hokusai.yml` - Default global Hokusai configuration file, with configs that meet the org's specifications.

Per-project files:

These files are stored in a `hokusai` directory that is in the project's root directory (i.e. `/path/to/project/hokusai`)

- `config.yml` - Hokusai configuration file for the project
- `build.yml` - docker-compose spec for building the project's Docker image
- `development.yml` - docker-compose spec for launching a local development stack
- `test.yml` - docker-compose spec for launching a test stack
- `staging.yml` - Kubernetes spec for defining the project's Staging resources
- `production.yml` - Kubernetes spec for defining the project's Production resources

When you create a new Hokusai-managed project, run [`hokusai setup`](./Command_Reference.md#setting-up-a-project) and it will populate the per-project files (using [templates](../hokusai/templates/hokusai)). Feel free to customize them for your project.

The following sections describe each file in detail.


## Global files


### ~/.hokusai.yml

Global configuration file. Currently supports:

- `kubeconfig_source_uri` - URI to fetch kubeconfig from, influences `hokusai configure` command
- `kubectl_version` - version of kubectl to download (must match Kubernetes cluster's version), influences `hokusai cofigure` command
- `kubeconfig_dir` - directory to install kubeconfig into, influences `hokusai configure` command
- `kubectl_dir` - directory to install kubectl into, influences any Hokusai command that causes kubectl to be invoked

Any Hokusai command including `hokusai configure` can look up configs in this file.

Here's a sample of the file:

```
---
kubeconfig-dir: /Users/anja/.kube
kubeconfig-source-uri: s3://acme/k8s/kubeconfig
kubectl-dir: /Users/anja/.local/bin
kubectl-version: 1.28.0
```

Please see [hokusai configure command](./Command_Reference.md#configuring-hokusai-for-your-organization) on how to generate this file based on the org's specifications.


## Per-project files


### config.yml

Per-project config file. The following configs are supported:

- `hokusai-required-version`: <string> (optional) - A [PEP-440 version specifier string](https://www.python.org/dev/peps/pep-0440/#version-specifiers).  Hokusai will raise an error when running commands if its current version does not satisfy these version specifications.  For example: `~=0.5`, `==0.5.1`, `>=0.4.0,<0.4.6`, `!=0.1.*` are all valid version specifier strings
- `project-name`: <string> (required) - The project name
- `git-remote`: <string> (optional) - Push deployment tags to git remote when invoking the `hokusai [staging|production] deploy` or the `hokusai pipeline promote` commands.  Can either be a local alias like 'origin' or a URI like `git@github.com:artsy/hokusai.git`.  Bound to the `--git-remote` option for these commands.
- `template-config-files`: <list> (optional) - Load template config files from the desired URIs, either `s3://` or a local file path.  See [Kubernetes YAML Template Processing](#kubernetes-yaml-template-processing) for further details.
- `pre-build`: <string> (optional) - A pre-build hook - useful to inject dynamic environment variables into the build, for example: `export COMMIT_HASH=$(git rev-parse HEAD)`
- `post-build`: <string> (optional) - A post-build hook - useful for image post-processing
- `pre-deploy`: <string> (optional) - A pre-deploy hook - useful to enforce migrations
- `post-deploy`: <string> (optional) - A post-deploy hook - useful for deploy notifications
- `run-tty`: <boolean> (optional) - Attach the terminal to your shell session when invoking `hokusai [staging|production|review_app] run`.  Bound to the `--tty` option for this command, and falls back to by the `HOKUSAI_RUN_TTY` env var.
    - `follow-logs`: <boolean> (optional) - Follow log output when invoking `hokusai [staging|production|review_app] logs`.  Bound to the `--follow` option for this command, and falls back to the `HOKUSAI_FOLLOW_LOGS` env var.
    - `tail-logs`: <integer> (optional) - Tail N lines of log output when invoking `hokusai [staging|production|review_app] logs`.  Bound to the `--tail` option for this command, and falls back to the `HOKUSAI_TAIL_LOGS` env var.
- `run-constraints`: <list of kubernetes label selector strings> - Constrain run containers to Kubernetes nodes matching the label selectors in the form `key=value` by setting the `nodeSelector` field on the container's spec. Bound to the `--constrint` option for `hokusai [staging|production|review_app] run` as well as containers run via the `--migration` flag as well as `pre-deploy` / `post-deploy` hooks triggered by `hokusai [staging|production|review_app] deploy` or `hokusai pipeline promote`.  Falls back to the `HOKUSAI_RUN_CONSTRAINTS` env var, in which case a list is parsed from a comma-delimited string.
- `always-verbose`: <boolean> (optional) - Always print verbose output.  Bound to the `--verbose` option for various commands, and falls back to the `HOKUSAI_ALWAYS_VERBOSE` env var.

Some of these configs have corresponding environment variables and/or Hokusai command line options. When a config is specified in multiple ways, the following order of precedence applies:

- User-specified value in command line option
- Value in `(project)/hokusai/config.yml` (this config file)
- Value in environment variable
- Default value of command line option

Here's a sample of the config file:

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


### build.yml

Referenced by `hokusai build` command. Should contain:

- a single Docker Compose Service
- a `build` spec referencing the root project directory
- any build args (i.e. host environment variables to inject into the Dockerfile)


### development.yml

Referenced by `hokusai dev` commands. Should contain:

- Docker Compose services required for project's dev stack
- development environment variables

It should extend `build.yml`.


### test.yml

Referenced by `hokusai test` commands. Should contain:

- Docker Compose services required for project's test stack
- test environment variables

It should extend `build.yml`.


### staging.yml

Referenced by `hokusai staging` commands. Should contain:

- at least one `Deployment` resource
- at least one `Service` resource
- any other necessary Kubernetes resources for project's staging stack


### production.yml

Referenced by `hokusai production` commands. Should contain:

- at least one `Deployment` resource
- at least one `Service` resource
- any other necessary Kubernetes resources for project's production stack


## Kubernetes YAML Template Processing

Since certain information (e.g. project name) is repeated in each of those YAML files, Hokusai tries to avoid manual duplication by treating the YAML files as [Jinja](https://jinja.palletsprojects.com/en/2.11.x/) templates. The files are Jinja-rendered (e.g. project name is filled in) before being passed to Docker Compose and Kubernetes.

The default [template context dictionary](https://jinja.palletsprojects.com/en/2.11.x/templates/#variables)(TCD) includes the variables `project_name` and `project_repo` and the context can be extended by providing the location of multiple YAML files to `template-config-files` config (see `config.yml` above). These files must contain a dictionary as a single document. The dictionaries are merged into the TCD in the order specified.  Any variables defined in the template and not included in the TCD will result in an Hokusai error, as will invalid operations on a variable (i.e. attempting to access a missing property of a variable of the wrong type).

For advanced template design please see Jinja's [template designer documentation](https://jinja.palletsprojects.com/en/2.11.x/templates/).


### Tips on template design

- If you get errors when sending Kubernetes YAML to the Kubernetes API, set `DEBUG` environment variable to print out the rendered YAML.
- Pay attention to whitespace and indentation in rendered YAML files.  Use the [whitespace control](https://jinja.palletsprojects.com/en/2.11.x/templates/#whitespace-control) features to strip leading and trailing whitespace and the [indent filter](https://jinja.palletsprojects.com/en/2.11.x/templates/#indent) to control indentation.
- Use [template inheritance](https://jinja.palletsprojects.com/en/2.11.x/templates/#template-inheritance) to share config snippets between YAML templates.  You can extend or include any other template file in the `(project)/hokusai` directory.


## Environment Injection

In order to inject configs into an application's environment, Hokusai's Kubernetes `Deployment` template includes a ConfigMap reference:

```
spec:
  spec:
    containers:
      envFrom:
        - configMapRef:
          name: {{ project_name }}-environment
```

The ConfigMap's name is assumed to be (project)-environment (e.g. `my-awesome-project-envirornment`). The ConfigMap Ref causes Kubernetes to map key/value pairs in the ConfigMap to variables in the application containers' environment. `hokusai [staging|production] env` commands interact with this ConfigMap.


## Kubernetes labels and selectors

Hokusai prescribes a label structure for a project's Kubernetes resources (e.g. `Deployment`, `Service`). In Kubernetes YAMLs, you will find the following:

```
# in a Deployment resource
spec:
  template:
    metadata:
      labels:
        app: {{ project_name }}
        layer: web
        component: application

# in a Service resource
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

This labeling allows `hokusai [staging|production]` commands to find the project's resources by `app={project_name},layer=application` labels.
