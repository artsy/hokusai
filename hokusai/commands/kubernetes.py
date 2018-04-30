import os
from collections import OrderedDict

import yaml

from hokusai.lib.command import command
from hokusai.lib.config import config
from hokusai.lib.common import print_green, shout
from hokusai.services.ecr import ECR
from hokusai.services.kubectl import Kubectl
from hokusai.services.configmap import ConfigMap
from hokusai.lib.exceptions import HokusaiError

@command
def k8s_create(context, tag='latest', yaml_file_name=None):
  if yaml_file_name is None: yaml_file_name = context
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % yaml_file_name)
  if not os.path.isfile(kubernetes_yml):
    raise HokusaiError("Yaml file %s does not exist." % kubernetes_yml)

  ecr = ECR()
  if not ecr.project_repo_exists():
    raise HokusaiError("ECR repository %s does not exist... did you run `hokusai setup` for this project?" % config.project_name)

  if not ecr.tag_exists(tag):
    raise HokusaiError("Image tag %s does not exist... did you run `hokusai push`?" % tag)

  if tag is 'latest' and not ecr.tag_exists(context):
    ecr.retag(tag, context)
    print_green("Updated tag 'latest' -> %s" % context)

  kctl = Kubectl(context)
  shout(kctl.command("create --save-config -f %s" % kubernetes_yml), print_output=True)
  print_green("Created Kubernetes environment %s" % context)

@command
def k8s_update(context, yaml_file_name=None):
  if yaml_file_name is None: yaml_file_name = context
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    raise HokusaiError("Yaml file %s does not exist." % kubernetes_yml)

  kctl = Kubectl(context)
  shout(kctl.command("apply -f %s" % kubernetes_yml), print_output=True)
  print_green("Updated Kubernetes environment %s" % context)

@command
def k8s_delete(context, yaml_file_name=None):
  if yaml_file_name is None: yaml_file_name = context
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % yaml_file_name)
  if not os.path.isfile(kubernetes_yml):
    raise HokusaiError("Yaml file %s does not exist." % kubernetes_yml)

  kctl = Kubectl(context)
  shout(kctl.command("delete -f %s" % kubernetes_yml), print_output=True)
  print_green("Deleted Kubernetes environment %s" % context)

@command
def k8s_status(context):
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

@command
def k8s_copy_config(context, destination_namespace):
  kctl = Kubectl(context)
  configmap = ConfigMap(context)
  configmap.load()
  configmap.struct['metadata']['namespace'] = destination_namespace
  configmap.save()
