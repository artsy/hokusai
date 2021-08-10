from hokusai.lib.command import command
from hokusai.lib.common import print_green, print_red
from hokusai.lib.exceptions import HokusaiError
from hokusai.services.ecr import ECR, ClientError

@command()
def retag(tag_to_change, tag_to_match):
  ecr = ECR()

  if not ecr.project_repo_exists():
    raise HokusaiError("Project repo does not exist. Aborting.")

  try:
    ecr.retag(tag_to_match, tag_to_change)
    print_green("Updated ECR '%s' tag to point to the image that '%s' tag points to." % (tag_to_change, tag_to_match), newline_after=True)
  except (ValueError, ClientError) as e:
    raise HokusaiError("Updating ECR tag failed due to the error: '%s'" % str(e))
