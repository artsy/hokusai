import re
import base64

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from hokusai.lib.config import config
from hokusai.lib.common import get_region_name

SHA1_REGEX = re.compile(r"\b[0-9a-f]{40}\b")

class ECR(object):
  def __init__(self):
    self.client = boto3.client('ecr', region_name=get_region_name())
    self.__aws_account_id = None
    self.__registry = None
    self.__project_repo = None

  @property
  def aws_account_id(self):
    if self.__aws_account_id is None:
      self.__aws_account_id = boto3.client('sts', region_name=get_region_name()).get_caller_identity().get('Account')
    return self.__aws_account_id

  @property
  def registry(self):
    if self.__registry is None:
      repos = []
      res = self.client.describe_repositories(registryId=self.aws_account_id)
      try:
        repos += res['repositories']
      except KeyError, err:
        print(res)
        raise
      while 'nextToken' in res:
        res = self.client.describe_repositories(registryId=self.aws_account_id,
                                                  nextToken=res['nextToken'])
        repos += res['repositories']
      self.__registry = repos
    return self.__registry

  @property
  def project_repo(self):
    if self.__project_repo is None:
      for repo in self.registry:
        if repo['repositoryName'] == config.project_name:
          self.__project_repo = repo['repositoryUri']
    return self.__project_repo

  def project_repo_exists(self):
    return self.project_repo is not None

  def create_project_repo(self):
    if self.project_repo_exists():
      return False
    self.client.create_repository(repositoryName=config.project_name)
    return True

  def get_login(self):
    res = self.client.get_authorization_token(registryIds=[str(self.aws_account_id)])['authorizationData'][0]
    token = base64.b64decode(res['authorizationToken'])
    username = token.split(':')[0]
    password = token.split(':')[1]
    return "docker login -u %s -p %s %s" % (username, password, res['proxyEndpoint'])

  def get_image_by_tag(self, tag):
    res = self.client.describe_images(registryId=self.aws_account_id,
                                      repositoryName=config.project_name,
                                      imageIds=[{'imageTag': tag}])
    return res['imageDetails'][0]

  def get_images(self):
    images = []
    res = self.client.describe_images(registryId=self.aws_account_id,
                                  repositoryName=config.project_name)
    images += res['imageDetails']
    while 'nextToken' in res:
      res = self.client.describe_images(registryId=self.aws_account_id,
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

  def find_git_sha1_image_tag(self, tag):
    image = self.get_image_by_tag(tag)
    for t in image['imageTags']:
      if SHA1_REGEX.match(t) is not None:
        return t
    return None

  def retag(self, tag, new_tag):
    res = self.client.batch_get_image(
      registryId=self.aws_account_id,
      repositoryName=config.project_name,
      imageIds=[{'imageTag': tag}]
    )

    if res['failures'] and not res['images']:
      raise ValueError("Failed to retrieve image manifest for tag %s" % tag)

    image = res['images'][0]

    try:
      self.client.put_image(
          registryId=self.aws_account_id,
          repositoryName=config.project_name,
          imageManifest=image['imageManifest'],
          imageTag=new_tag
      )
    except ClientError as e:
      if e.response['Error']['Code'] != 'ImageAlreadyExistsException':
        raise
