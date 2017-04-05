import boto3
from botocore.exceptions import BotoCoreError

from hokusai.config import config

class ECR(object):
  def __init__(self):
    self.client = boto3.client('ecr', region_name=config.aws_ecr_region)

  def registry(self):
    repos = []
    res = self.client.describe_repositories(registryId=config.aws_account_id)
    repos += res['repositories']
    while 'nextToken' in res:
      res = self.client.describe_repositories(registryId=self.registry_id,
                                                nextToken=res['nextToken'])
      repos += res['repositories']
    return repos

  def project_repository_exists(self):
    repo_names = [r['repositoryName'] for r in self.registry()]
    return config.project_name in repo_names

  def create_project_repository(self):
    try:
      self.client.create_repository(repositoryName=config.project_name)
    except BotoCoreError:
      return False
    return True

ecr = ECR()
