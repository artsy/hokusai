from hokusai.lib.command import command
from hokusai.services.command_runner import CommandRunner

@command()
def run(context, cmd, tty, tag, env, constraint, namespace=None):
  if tag is None:
    tag = context

  return CommandRunner(context, namespace=namespace).run(tag, cmd, tty=tty, env=env, constraint=constraint)
