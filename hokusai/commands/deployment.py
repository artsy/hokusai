from hokusai.lib.command import command
from hokusai.lib.common import print_green
from hokusai.services.deployment import Deployment
from hokusai.services.command_runner import CommandRunner
from hokusai.services.ecr import ECR
from hokusai.lib.exceptions import HokusaiError

@command()
def update(context, tag, migration, constraint, git_remote, timeout,
            namespace=None, update_config=False, filename=None):
  if migration is not None:
    print_green("Running migration '%s' on %s..." % (migration, context), newline_after=True)
    return_code = CommandRunner(context, namespace=namespace).run(tag, migration, constraint=constraint, tty=False)
    if return_code:
      raise HokusaiError("Migration failed with return code %s" % return_code, return_code=return_code)
  Deployment(context, namespace=namespace).update(tag, constraint, git_remote, timeout,
                                                  update_config=update_config, filename=filename)
  print_green("Deployment(s) updated to %s" % tag)


@command()
def refresh(context, deployment_name, namespace=None):
  deployment = Deployment(context, deployment_name=deployment_name, namespace=namespace)
  deployment.refresh()


@command()
def promote(migration, constraint, git_remote, timeout, update_config=False, filename=None):
  if migration is not None:
    print_green("Running migration '%s' on production..." % migration, newline_after=True)
    return_code = CommandRunner('production').run('staging', migration, constraint=constraint, tty=False)
    if return_code:
      raise HokusaiError("Migration failed with return code %s" % return_code, return_code=return_code)

  Deployment('production').update('staging', constraint, git_remote, timeout, update_config=update_config, filename=filename)
  print_green("Promoted staging to production")
