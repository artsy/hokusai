import os

from collections import OrderedDict

import yaml

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.lib.common import print_red, print_green, shout
from hokusai.services.ecr import ECR
from hokusai.services.kubectl import Kubectl

@command
def stack_create(context):
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  ecr = ECR()
  if not ecr.project_repository_exists():
    print_red("ECR repository %s does not exist... did you run `hokusai setup` for this project?" % config.project_name)
    return -1

  if not ecr.tag_exists('latest'):
    print_red("Image tag 'latest' does not exist... did you run `hokusai push`?")
    return -1

  if not ecr.tag_exists(context):
    ecr.retag('latest', context)
    print_green("Updated tag 'latest' -> %s" % context)

  kctl = Kubectl(context)
  shout(kctl.command("create --save-config -f %s" % kubernetes_yml), print_output=True)
  print_green("Created stack %s" % context)

@command
def stack_update(context):
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  kctl = Kubectl(context)
  shout(kctl.command("apply -f %s" % kubernetes_yml), print_output=True)
  print_green("Updated stack %s" % context)

@command
def stack_delete(context):
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  kctl = Kubectl(context)
  shout(kctl.command("delete -f %s" % kubernetes_yml), print_output=True)
  print_green("Deleted stack %s" % context)

@command
def stack_status(context):
  kctl = Kubectl(context)
  print('')
  print_green("Deployments")
  print_green('-----------------------------------------------------------')
  shout(kctl.command("get deployments --selector app=%s -o wide" % config.project_name), print_output=True)
  print('')
  print_green("Services")
  print_green('-----------------------------------------------------------')
  shout(kctl.command("get services --selector app=%s -o wide" % config.project_name), print_output=True)
  print('')
  print_green("Pods")
  print_green('-----------------------------------------------------------')
  shout(kctl.command("get pods --selector app=%s -o wide" % config.project_name), print_output=True)
