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
def k8s_create(context, tag='latest', namespace=None, yaml_file_name=None):
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

  kctl = Kubectl(context, namespace=namespace)
  shout(kctl.command("create --save-config -f %s" % kubernetes_yml), print_output=True)
  print_green("Created Kubernetes environment %s" % kubernetes_yml)


@command
def k8s_update(context, namespace=None, yaml_file_name=None):
  if yaml_file_name is None: yaml_file_name = context
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % yaml_file_name)
  if not os.path.isfile(kubernetes_yml):
    raise HokusaiError("Yaml file %s does not exist." % kubernetes_yml)

  kctl = Kubectl(context, namespace=namespace)
  shout(kctl.command("apply -f %s" % kubernetes_yml), print_output=True)
  print_green("Updated Kubernetes environment %s" % kubernetes_yml)


@command
def k8s_delete(context, namespace=None, yaml_file_name=None):
  if yaml_file_name is None: yaml_file_name = context
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % yaml_file_name)
  if not os.path.isfile(kubernetes_yml):
    raise HokusaiError("Yaml file %s does not exist." % kubernetes_yml)

  kctl = Kubectl(context, namespace=namespace)
  shout(kctl.command("delete -f %s" % kubernetes_yml), print_output=True)
  print_green("Deleted Kubernetes environment %s" % kubernetes_yml)


@command
def k8s_status(context, resources, pods, describe, top, namespace=None, yaml_file_name=None):
  if yaml_file_name is None: yaml_file_name = context
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % yaml_file_name)
  if not os.path.isfile(kubernetes_yml):
    raise HokusaiError("Yaml file %s does not exist." % kubernetes_yml)

  kctl = Kubectl(context, namespace=namespace)
  if describe:
    kctl_cmd = "describe"
    output = ""
  else:
    kctl_cmd = "get"
    output = " -o wide"
  if resources:
    print('')
    print_green("Resources")
    print_green("===========")
    shout(kctl.command("%s -f %s%s" % (kctl_cmd, kubernetes_yml, output)), print_output=True)
  if pods:
    print('')
    print_green("Pods")
    print_green("===========")
    shout(kctl.command("%s pods --selector app=%s,layer=application%s" % (kctl_cmd, config.project_name, output)), print_output=True)
  if top:
    print('')
    print_green("Top Pods")
    print_green("===========")
    shout(kctl.command("top pods --selector app=%s,layer=application" % config.project_name), print_output=True)


@command
def k8s_copy_config(context, destination_namespace):
  source_configmap = ConfigMap(context)
  destination_configmap = ConfigMap(context, namespace=destination_namespace)
  source_configmap.load()
  destination_configmap.struct['data'] = source_configmap.struct['data']
  destination_configmap.save()
