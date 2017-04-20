from operator import itemgetter

from hokusai.lib.command import command
from hokusai.services.ecr import ECR
from hokusai.lib.config import config
from hokusai.lib.common import print_green, shout

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
