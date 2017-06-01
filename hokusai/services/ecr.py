import base64

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from hokusai.lib.config import config

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
      repository = self.client.create_repository(repositoryName=config.project_name)['repository']
    except BotoCoreError:
      return False
    except KeyError:
      return False
    try:
      assert 'createdAt' in repository
      assert repository['registryId'] == config.aws_account_id
      assert 'repositoryArn' in repository
      assert repository['repositoryName'] == config.project_name
      assert 'repositoryUri' in repository
    except AssertionError:
      return False
    return True

  def get_login(self):
    res = self.client.get_authorization_token(registryIds=[str(config.aws_account_id)])['authorizationData'][0]
    token = base64.b64decode(res['authorizationToken'])
    username = token.split(':')[0]
    password = token.split(':')[1]
    return "docker login -u %s -p %s -e none %s" % (username, password, res['proxyEndpoint'])

  def get_images(self):
    images = []
    res = self.client.describe_images(registryId=config.aws_account_id,
                                  repositoryName=config.project_name)
    images += res['imageDetails']
    while 'nextToken' in res:
      res = self.client.describe_images(registryId=config.aws_account_id,
                                    repositoryName=config.project_name,
                                    nextToken=res['nextToken'])
      images += res['imageDetails']
    return images

  def tag_exists(self, tag):
    for image in self.get_images():
      if 'imageTags' not in image.keys():
        continue
      if tag in image['imageTags']:
        return True
    return False

  def retag(self, tag, new_tag):
    res = self.client.batch_get_image(
      registryId=config.aws_account_id,
      repositoryName=config.project_name,
      imageIds=[{'imageTag': tag}]
    )

    if len(res['failures']) and not len(res['images']):
      raise ValueError("Failed to retrieve image manifest for tag %s" % tag)

    image = res['images'][0]

    try:
      self.client.put_image(
          registryId=config.aws_account_id,
          repositoryName=config.project_name,
          imageManifest=image['imageManifest'],
          imageTag=new_tag
      )
    except ClientError as e:
      if e.response['Error']['Code'] != 'ImageAlreadyExistsException':
        raise
