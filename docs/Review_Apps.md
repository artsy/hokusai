# Working with review apps

Hokusai provides commands for managing review apps. Review apps are useful for testing features that are not yet ready to be deployed to staging but need to be tested in a staging-like environment.

Perform the following steps in order to create a review app. `app-name` refers to name of the review app.

## Prepare app

```
hokusai review_app setup <app-name> # we recommend using branch name or PR number as name
```

It creates a `<app-name>.yml` file under `hokusai/` folder. This is the review app Yaml.

Check the file and make sure everything looks good. Note that we use Kubernetes [`namespace`](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) for review apps, that is, each review app is created in a dedicated namespace.

## Push Docker image

Tag the image with review app's name.

```
hokusai registry push --tag <app-name>
```

If the working directory has any changed, untracked, or git-ignored files, Hokusai aborts the push in order to not copy any potentially sensitive files into the image. If you know the files are not sensitive or they are already covered by `.dockerignore` file, force the push by:

```
hokusai registry push --force --tag <app-name>
```

`push` by default updates the `latest` tag in AWS ECR registry, which can be skipped by:

```
hokusai registry push --skip-latest --tag <app-name>
```

Then, edit review app Yaml. Find the `containers` subsection of the configuration that specifies the `image` that should be pulled from AWS ECR when booting up your review app. Update the value of that `image` so that it points to your newly tagged image, rather than the default staging image for that project.

For example, change:

```
image: <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/volt:staging
```

to:

```
image: <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/volt:<app-name>
```

## Create Kubernetes resources

This step actually creates Kubernetes resources for the review app.

```
hokusai review_app create <app-name>
```

## Find and visit the app:

- Go to https://kubernetes.stg.artsy.systems (VPN required).
- Find the "Namespace" dropdown in the main nav and select `<app-name>`.
- Browse to the "Services" section.
- In "Details", look for "External endpoints". These are your publicly accessible URLs.
- You may need to tweak the URL to use `https` instead of `http`.
- You may need to accept a browser warning about a missing or bad certificate.

You can also view a summarized status of your review app with:

```
hokusai review_app status <app-name>
```

## Update environment variables (optional)

```
hokusai review_app env get <app-name> FOO
hokusai review_app env set <app-name> FOO=BAR
```

## Refresh the app (optional)

Must be done if environment variables are updated.

```
hokusai review_app refresh <app-name>
```

## View pods' logs (optional)

```
hokusai review_app logs <app-name>
```

## Start a shell session (optional)

This launches a review app pod and opens a shell session (e.g. Rails console).

```
hokusai review_app run <app-name> <command> --tty
```

## Push code changes (optional)

When review app code is changed, update Docker image by:

```
hokusai registry push --overwrite --skip-latest --force --tag <app-name>
```

The re-deploy:

```
hokusai review_app deploy <app-name> <image-tag>
```

## Push Yaml changes (optional)

If review app Yaml is changed, do:

```
hokusai review_app deploy <app-name> <image-tag> --update-config
```

or

```
hokusai review_app update <app-name>
```

## Delete the app (optional)

```
hokusai review_app delete <app-name>
```
