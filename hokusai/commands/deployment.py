from hokusai.lib.command import command
from hokusai.lib.common import print_green
from hokusai.services.deployment import Deployment
from hokusai.services.command_runner import CommandRunner
from hokusai.services.ecr import ECR
from hokusai.lib.exceptions import HokusaiError

@command()
def update(context, tag, migration, constraint, git_remote, timeout,
            namespace=None, resolve_tag_sha1=True, update_config=False, filename=None):
  if migration is not None:
    print_green("Running migration '%s' on %s..." % (migration, context), newline_after=True)
    return_code = CommandRunner(context, namespace=namespace).run(tag, migration, constraint=constraint, tty=False)
    if return_code:
      raise HokusaiError("Migration failed with return code %s" % return_code, return_code=return_code)
  Deployment(context, namespace=namespace).update(tag, constraint, git_remote, timeout,
                                                  resolve_tag_sha1=resolve_tag_sha1, update_config=update_config, filename=filename)
  print_green("Deployment updated to %s" % tag)


@command()
def refresh(context, deployment_name, namespace=None):
  deployment = Deployment(context, deployment_name=deployment_name, namespace=namespace)
  deployment.refresh()


@command()
def promote(migration, constraint, git_remote, timeout):
  ecr = ECR()

  deploy_from = Deployment('staging')
  tag = deploy_from.current_tag
  if tag is None:
    raise HokusaiError("Could not find a tag for staging.  Aborting.")
  tag = ecr.find_git_sha1_image_tag(tag)
  if tag is None:
    print_red("Could not find a git SHA1 for tag %s.  Aborting." % tag)
    return 1

  if migration is not None:
    print_green("Running migration '%s' on production..." % migration, newline_after=True)
    return_code = CommandRunner('production').run(tag, migration, constraint=constraint, tty=False)
    if return_code:
      raise HokusaiError("Migration failed with return code %s" % return_code, return_code=return_code)

  deploy_to = Deployment('production').update(tag, constraint, git_remote, timeout)
  print_green("Promoted staging to production at %s" % tag)
