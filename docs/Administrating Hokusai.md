## Administrating Hokusai

Operationally, Hokusai requires:
- One or more Kubernetes deployments
- An AWS IAM user and keypair
- IAM policy / policies granting access to ECR and S3

### Deploying Kubernetes

Deploying Kubernetes is outside the scope of Hokusai, but we recommend taking a look at [kops](https://github.com/kubernetes/kops) to bootstrap Kubernetes clusters on EC2.

Note: Ensure that your Kubelets have access to ECR and can pull images.

### Creating an IAM user

We recommend creating an IAM user per application developer, let's call her Anja. Navigate to the AWS IAM dashboard, and create a new user 'anja'.  Take note of the generated keypair.

### Configuring IAM credentials

In order to grant users access to the ECR repositories, create a new IAM policy, and attach this policy to `anja`.

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

### Configuring kubectl for your organization

Hokusai depends on the existence of two Kubernetes contexts - `staging` and `production`.  You should create a kubectl config file, with these two contexts targeting your staging and production Kubernetes deployment(s).  We manage seperate staging and production clusters, but you can just as easily use one cluster with different namespaces.

Upload the kubectl config file to S3, and ensure your development teams have access to it by creating another / updating your existing IAM policy and attaching this policy to `anja`.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::bucket-name/file-key"]
    }
  ]
}
```

Finally, instruct your development teams to run `hokusai configure --kubectl-version <kubectl version> --s3-bucket <bucket name> --s3-key <file key>` with the version of your Kubernetes deployment(s) as well as the S3 bucket and key of the kubectl config file you provided.
