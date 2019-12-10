## Working with review apps

Hokusai provides a command for managing review apps. Review apps are useful for testing feature branches that are not yet ready to be deployed to staging but need to be tested in a staging-like environment.

In order to start a review app you will need to follow these steps:

1) Create a new review app
    ```shell
    hokusai review_app setup <name> # we recommend using branch name or PR number as name
    ```
    This command will create a new `<name>.yml` under `hokusai/` folder.

2) Check the newly created `<name>.yml` file and make sure everything looks good. Note that we use Kubernetes [`namespace`](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) for review apps. Basically each review app will end up being in its own namespace to not collide with staging.

3) Push an image with this review app tag:

    ```shell
    hokusai registry push --tag <name>
    ```

    If you have git-ignored files in your working directory (likely) you will have to force push with:
    ```shell
    hokusai registry push --force --tag <name>
    ```

    It may be a good idea to skip updating the `latest` tag in the registry, which you can do with:
    ```shell
    hokusai registry push --skip-latest --tag <name>
    ```

4) Make sure your review app deployment will use the image you just pushed. This can be done by modifying the new `<name>.yml` file.

    There will be a `containers` subsection of the configuration that specifies the `image` that should be pulled from AWS Elastic Container Registry when booting up your review app. Update the value of that `image` so that it points to your newly tagged image, rather than the default staging image for that project.

    Example:
    ```yml
    image: 585031190124.dkr.ecr.us-east-1.amazonaws.com/volt:staging

    # must be changed to...

    image: 585031190124.dkr.ecr.us-east-1.amazonaws.com/volt:<name>
    ```
    ... where `<name>` is the review app name you've been using in previous steps, especially step 3.


5) Create new deployment on k8s based on your new local YAML config:

    ```shell
    hokusai review_app create <name>
    ```

6) Copy the staging environment's `ConfigMap` to the new namespace:

    ```shell
    hokusai review_app env copy <name>
    ```

7) If necessary, copy other `ConfigMaps` to the new namespace, for example:

    ```shell
    hokusai review_app env copy <name> --configmap nginx-config
    ```

8) Find and visit your staging app:

    - In the Kubernetes UI, find the "Namespace" dropdown in the main nav and select your chosen `<name>` from that menu
    - Browse to the "Services" section
    - In "Details", look for "External endpoints". These are your publicly accessible URLs.
    - You may need to tweak the URL to use `https` instead of `http`
    - You may need to accept a browser warning about a missing or bad certificate

    You can also view a summarized status of your review app with:

    ```shell
    hokusai review_app status <name>
    ```

9) If you need to view or update environment variables:

    ```shell
    hokusai review_app env get <name> FOO
    hokusai review_app env set <name> FOO=BAR
    ```

10) If you need to refresh your app, (e.g. after updating environment variables)

    ```shell
    hokusai review_app refresh <name>
    ```

11) If you need to view logs for your app, (e.g. after a refresh or deploy)

    ```shell
    hokusai review_app logs <name>
    ```

12) If you need to get a shell in your app, (e.g. to launch a Rails console)

    ```shell
    hokusai review_app run <name> <command> --tty
    ```

13) If you want to push subsequent changes to the review app,

    you can push a new build to the same tag with the `--overwrite` flag:
    ```shell
    hokusai registry push --overwrite --skip-latest --force --tag <name>
    ```

    and you need to redeploy your app:
    ```shell
    hokusai review_app deploy <name> <name>
    ```

14) If you have made changes to your review app's yaml file, you need to update the deployment:

    ```shell
    hokusai review_app deploy <name> <name> --update-config
    ```

    or

    ```shell
    hokusai review_app update <name>
    ```

15) Delete review app:

    ```shell
    hokusai review_app delete <name>
    ```
