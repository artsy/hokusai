# Administering Hokusai

This doc talks about some admin-level setup that must be performed before you can can start using Hokusai.

- Deploy a Kubernetes cluster
- Create a kubectl config file
- Create an AWS IAM User for the person using Hokusai
- Grant IAM User access to ECR
- Create an org-wide Hokusai global config file
- Grant IAM User access to S3


## Deploy a Kubernetes cluster

There is a bunch of tools available for doing this. [Kops](https://github.com/kubernetes/kops) is one, and it can deploy a cluster on AWS EC2.

The cluster must be able to pull Docker images from AWS ECR.


## Create a kubectl config file

Create a kubectl config file (also known as kubeconfig file) that has two contexts: `staging` and `production`. Hokusai recognizes only those two contexts. Map these contexts to your staging and production environments which can be two Kubernetes clusters, or two namespaces of the same cluster.

Upload the file to an S3 location readable by users.


## Create an AWS IAM User for the person using Hokusai

Suppose the person's name is Anja, create an IAM User named 'anja'. Generate a keypair and deliver to Anja.


## Grant IAM User access to ECR

For example, attach the following IAM policy to `anja` IAM User.

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ecr:CreateRepository",
      "ecr:GetAuthorizationToken",
      "ecr:ListImages",
      "ecr:DescribeImages",
      "ecr:BatchGetImage"
    ],
    "Resource": "*"
  }]
}
```


## Create an org-wide Hokusai global config file

See [Global Configuration](./Configuration_Options.md) for list of config variables supported.

Upload the file to an S3 location readable by users.


## Grant IAM User access to S3

For example, attach the following IAM policy to `anja` IAM User.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": [
        "arn:aws:s3:::bucket-name/path/to/kubeconfig-file",
        "arn:aws:s3:::bucket-name/path/to/org-wide-global-config-file"
      ]
    }
  ]
}
```
