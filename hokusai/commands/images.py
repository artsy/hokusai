from operator import itemgetter

from hokusai.lib.command import command
from hokusai.services.ecr import ECR
from hokusai.lib.config import config
from hokusai.lib.common import print_green, print_yellow, shout

@command()
def images(reverse_sort, limit, filter_tags):
  images = ECR().get_images()
  sorted_images = sorted(images, key=itemgetter('imagePushedAt'), reverse=not reverse_sort)
  filtered_images = filter(lambda image: 'imageTags' in image.keys(), sorted_images)
  if filter_tags:
    filtered_images = filter(lambda image: filter_tags in ', '.join(image['imageTags']), filtered_images)

  print('')
  print_green('Image Pushed At           | Image Tags')
  print_green('----------------------------------------------------------')

  for image in filtered_images[:limit]:
    image_tags = ', '.join(image['imageTags'])
    line = "%s | %s" % (image['imagePushedAt'], image_tags)
    if 'production' in image['imageTags']:
      print_green(line)
    elif 'staging' in image['imageTags']:
      print_yellow(line)
    else:
      print(line)

  print('')
  print_yellow("%d more images available" % (len(filtered_images) - len(filtered_images[:limit])))

