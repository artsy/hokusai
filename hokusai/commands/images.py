from operator import itemgetter

from hokusai.command import command
from hokusai.ecr import ECR
from hokusai.config import config
from hokusai.common import print_green, shout

@command
def images():
  images = ECR().get_images()
  print('')
  print_green('Image Pushed At           | Image Digest                                                     | Image Tags')
  print_green('-------------------------------------------------------------------------------------------------------------------------------')
  for image in sorted(images, key=itemgetter('imagePushedAt'), reverse=True):
    if 'imageTags' not in image.keys():
      continue
    print("%s | %s | %s" % (image['imagePushedAt'], image['imageDigest'][7:], ', '.join(image['imageTags'])))
