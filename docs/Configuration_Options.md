# Configuration Options

## Global configuration

The environment variables `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY` are referenced by Hokusai when running `setup` as well as `registry` commands.

When running `hokusai configure` the following files are created:

* `kubectl` installed on your $PATH
* Your organization-specific `~/.kube/config` kubectl configuration file

## Project configuration

When running `hokusai setup` the following files are created:

* `./hokusai/config.yml` contains project-specific configuration options.  It accepts the following keys:

    - `project-name`: <string> (required) - The project name
    - `pre-deploy`: <string> (optional) - A pre-deploy hook - useful to enforce migrations
    - `post-deploy`: <string> (optional) - A post-deploy hook

* `./hokusai/common.yml` is the base docker-compose Yaml file referenced when running `hokusai local` commands. It should contain a single service for the project, `build` referencing the root project directory, and any build args (i.e.) host environment variables to inject into the Dockerfile. 

* `./hokusai/development.yml` is the docker-compose Yaml file referenced when running `hokusai local dev` commands. It should contain a definition for your project service (extending `./hokusai/common.yml`) as well as development environment variables and any dependent services.

* `./hokusai/test.yml` is the docker-compose Yaml file referenced when running `hokusai local test`. It should contain a definition for your project service (extending `./hokusai/common.yml`) as well as test environment variables and any dependent services.

* `./hokusai/staging.yml` is the Kubernetes Yaml file referenced with running `hokusai staging` subcommands. It should contain a `Deployment` and a `Service` definition for the project as well as any dependent deployments and/or services.

* `./hokusai/production.yml` is the Kubernetes Yaml file referenced with running `hokusai production` subcommands. It should contain a `Deployment` and a `Service` definition for the project as well as any dependent deployments and/or services.

These files are meant to be modified on a per-project basis.  You can (and should) use them as a starting point and modify them to suit the needs of your application.  Hokusai remains agnostic about the content of these files, only passes them to `docker-compose` and `kubectl` as part of its workflow.  To see how exactly these files are being used by Hokusai, run commands with the `-v / --verbose` flag.

### Environment Injection

In order to inject an application's environment into running containers, Hokusai templates each `Deployment` in `./hokusai/staging.yml` and `./hokusai/production.yml` with the following definition:

```
spec:
    spec:
        containers:
            envFrom:
                - configMapRef:
                    name: {{ project_name }}
```

This instructs Kubernetes to use the `ConfigMap` object named `{project-name}-environment` as a key-value mapping of environment variables to set in the container runtime environment.  `hokusai [staging|production] env` commands are designed to manage this environment.

Note: When changing the project environment (i.e. after running `hokusai [staging|production] env set FOO=bar`) you need to run `hokusai [staging|production] deployment refresh` to re-create the project deployment's containers as Kubernetes will not propogate the new environment variables automatically.

### Kubernetes labels and selectors

Hokusai prescribes a deployment strategy and label structure for the `Deployment` and `Service` definitions it creates in `./hokusai/staging.yml` and `./hokusai/production.yml`.

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

For example, to add a worker `Deployment` to `./hokusai/staging.yml` or `./hokusai/production.yml` you would create it with the following labels:

```
spec:
  template:
    metadata:
      labels:
        app: {{ project_name }}
        layer: worker
        component: application
```

With this structure, Hokusai will update *both* the web and worker deployments simultaneuosly, which is probably what you want.

If you do not want this, and for example want to include a Redis `Deployment` in `./hokusai/staging.yml` or `./hokusai/production.yml` you would create it with the following labels:

```
spec:
  template:
    metadata:
      labels:
        app: {{ project_name }}
        layer: redis
        component: cache
```

Hokusai would ignore this when `hokusai [staging|production]` commands, but it would be included as part of your application's Kubernetes environment.
