from operator import itemgetter

import boto3

from hokusai.command import command
from hokusai.config import HokusaiConfig
from hokusai.common import print_green, shout

@command
def images():
  config = HokusaiConfig().check()
  client = boto3.client('ecr')

  images = []
  res = client.describe_images(registryId=config.aws_account_id,
                                repositoryName=config.project_name)
  images += res['imageDetails']

  while 'nextToken' in res:
    res = client.describe_images(registryId=config.aws_account_id,
                                  repositoryName=config.project_name,
                                  nextToken=res['nextToken'])
    images += res['imageDetails']

  print_green('Image Pushed At           | Image Tags')
  print_green('-----------------------------------------------------------')
  for image in sorted(images, key=itemgetter('imagePushedAt'), reverse=True):
    if 'imageTags' not in image.keys():
      continue
    print("%s | %s" % (image['imagePushedAt'], ', '.join(image['imageTags'])))
