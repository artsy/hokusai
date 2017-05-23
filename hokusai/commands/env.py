from hokusai.lib.config import config
from hokusai.lib.command import command
from hokusai.services.configmap import ConfigMap
from hokusai.lib.common import print_red, print_green

@command
def create_env(context):
  configmap = ConfigMap(context)
  configmap.create()
  print_green("Created configmap %s-environment" % config.project_name)

@command
def delete_env(context):
  configmap = ConfigMap(context)
  configmap.destroy()
  print_green("Deleted configmap %s-environment" % config.project_name)

@command
def get_env(context, environment):
  configmap = ConfigMap(context)
  configmap.load()
  if len(environment) == 0:
    for k, v in configmap.all():
      print("%s=%s" % (k, v))
  else:
    for k, v in configmap.all():
      if k in environment:
        print("%s=%s" % (k, v))

@command
def set_env(context, environment):
  configmap = ConfigMap(context)
  configmap.load()
  for s in environment:
    if '=' not in s:
      print_red("Error: environment variables must be of the form 'KEY=VALUE'")
      return -1
    split = s.split('=', 1)
    configmap.update(split[0], split[1])
  configmap.save()

@command
def unset_env(context, environment):
  configmap = ConfigMap(context)
  configmap.load()
  for s in environment:
    configmap.delete(s)
  configmap.save()
