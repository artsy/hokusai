from hokusai.lib.command import command
from hokusai.services.command_runner import CommandRunner

@command
def run(context, cmd, tty, tag, env):
  if tag is not None:
    image_tag = tag
  else:
    image_tag = context

  return CommandRunner(context).run(image_tag, cmd, tty=tty, env=env)
