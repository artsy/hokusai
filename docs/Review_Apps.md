## Working with review apps

Hokusai provides a command for managing review apps. Review apps are useful for testing feature branches that are not yet ready to be deployed to staging but need to be tested in a staging-like environment.

In order to start a review app you will need to follow these steps:

1) Create a new review app
    ```shell
    hokusai review_app setup <name> # we recommend using branch name or pr number as name
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

4) Make sure your review app deployment will use the image you just pushed. This can be done by modifying the new `<name>.yml` file.

    There will be a `containers` subsection of the configuration that specifies the `image` that should be pulled from AWS Elastic Container Registry when booting up your review app. Update the value of that `image` so that it points to your newly tagged image, rather than the default staging image for that project.

    Example:
    ```yml
    image: 585031190124.dkr.ecr.us-east-1.amazonaws.com/volt:staging

    # …must be changed to…

    image: 585031190124.dkr.ecr.us-east-1.amazonaws.com/volt:<name>
    ```
    …where `<name>` is the review app name you've been using in previous steps, especially step 3.


5) Create new deployment on k8s based on your new local YAML config:

    ```shell
    hokusai review_app create <name>
    ```

6) Copy the staging `configMap` to the new namespace:

    ```shell
    hokusai review_app env copy <name>
    ```

7) Find and visit your staging app:

    - In the Kubernetes UI, find the "Namespace" dropdown in the main nav and select your chosen `<name>` from that menu
    - Go to Replica Sets > _replica set name_ (there is probably only one)
    - Browse to the "Services" section
    - Look in the "External endpoints" column
    - These endpoints are your publicly accessible URLs
    - You may need to tweak the URL to use `https` instead of `http`
    - You may need to accept a browser warning about a missing or bad certificate

8) If you need to update environment variables:

    ```shell
    hokusai review_app env set <name> FOO=BAR
    ```

9) If you need to refresh your app, (e.g. after updating environment variables)

    ```shell
    hokusai review_app refresh <name>
    ```

10) Update review app:

    If you have made changes to your review app's yaml file, you need to update deployment for that do:
    ```shell
    hokusai review_app update <name>
    ```

11) Delete review app:

    ```shell
    hokusai review_app delete <name>
    ```

