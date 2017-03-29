import os

from hokusai.command import command
from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, shout, select_context
from hokusai.deployment import Deployment

@command
def stack_up(context):
  HokusaiConfig().check()
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  select_context(context)
  shout("kubectl apply -f %s" % kubernetes_yml)
  print_green("Stack %s updated" % context)

@command
def stack_down(context):
  HokusaiConfig().check()

  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  select_context(context)
  shout("kubectl delete -f %s" % kubernetes_yml)
  print_green("Stack %s deleted" % kubernetes_yml)

@command
def stack_status(context):
  deployment = Deployment(context)
  tag = deployment.get_current_tag()
  if tag is None:
    return -1
  print_green("Current tag: %s" % tag)
