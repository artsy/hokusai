from operator import itemgetter

from hokusai.lib.command import command
from hokusai.services.ecr import ECR
from hokusai.lib.config import config
from hokusai.lib.common import print_green, print_yellow, print_red, print_smart, shout, pick_yes, pick_no

@command()
def images(tag_exists, reverse_sort, limit, filter_tags, digests):
  ecr = ECR()
  if tag_exists:
    if ecr.get_image_by_tag(tag_exists):
      print_green(pick_yes())
      return
    else:
      print_red(pick_no())
      return 1

  images = ecr.images
  sorted_images = sorted(images, key=itemgetter('imagePushedAt'), reverse=not reverse_sort)
  filtered_images = list(filter(lambda image: 'imageTags' in image.keys(), sorted_images))
  if filter_tags:
    filtered_images = list(filter(lambda image: filter_tags in ', '.join(image['imageTags']), filtered_images))

  if digests:
    print_green('Image Pushed At           | Image Digest                                                            | Image Tags', newline_before=True)
    print_green('--------------------------------------------------------------------------------------------------------------------------------------')
  else:
    print_green('Image Pushed At           | Image Tags', newline_before=True)
    print_green('----------------------------------------------------------')

  for image in filtered_images[:limit]:
    image_tags = ', '.join(image['imageTags'])
    if digests:
      line = "%s | %s | %s" % (image['imagePushedAt'], image['imageDigest'], image_tags)
    else:
      line = "%s | %s" % (image['imagePushedAt'], image_tags)
    if 'production' in image['imageTags']:
      print_green(line)
    elif 'staging' in image['imageTags']:
      print_yellow(line)
    else:
      print_smart(line)

  print_yellow("%d more images available" % (len(filtered_images) - len(filtered_images[:limit])),
                newline_before=True, newline_after=True)

