from hokusai.lib.config import config
from hokusai.lib.command import command
from hokusai.services.secret import Secret
from hokusai.lib.common import print_green

@command
def create_env(context):
  secret = Secret(context)
  secret.create()
  print_green("Created secret %s-environment" % config.project_name)

@command
def delete_env(context):
  secret = Secret(context)
  secret.destroy()
  print_green("Deleted secret %s-environment" % config.project_name)

@command
def get_env(context, environment):
  secret = Secret(context)
  secret.load()
  if len(environment) == 0:
    for k, v in secret.all():
      print("%s=%s" % (k, v))
  else:
    for k, v in secret.all():
      if k in environment:
        print("%s=%s" % (k, v))

@command
def set_env(context, environment):
  secret = Secret(context)
  secret.load()
  for s in environment:
    if '=' not in s:
      print_red("Error: environment vars must be of the form 'KEY=VALUE'")
      return -1
    split = s.split('=', 1)
    secret.update(split[0], split[1])
  secret.save()

@command
def unset_env(context, environment):
  secret = Secret(context)
  secret.load()
  for s in environment:
    secret.delete(s)
  secret.save()
