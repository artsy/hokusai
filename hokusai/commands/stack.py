import os
import yaml

from hokusai.command import command
from hokusai.config import config
from hokusai.common import print_red, print_green, shout
from hokusai.deployment import Deployment
from hokusai.service import Service
from hokusai.kubectl import Kubectl

@command
def stack_create(context):
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  kctl = Kubectl(context)
  shout(kctl.command("create -f %s" % kubernetes_yml))
  print_green("Stack %s created" % context)

@command
def stack_update(context):
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  kctl = Kubectl(context)
  shout(kctl.command("apply -f %s" % kubernetes_yml))
  print_green("Stack %s updated" % context)

@command
def stack_destroy(context):

  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  kctl = Kubectl(context)
  shout(kctl.command("delete -f %s" % kubernetes_yml))
  print_green("Stack %s deleted" % kubernetes_yml)

@command
def stack_status(context):
  deployment = Deployment(context)
  deployment_state = deployment.state
  if deployment_state is None:
    return -1
  deployment_data = {
    'replicas': deployment_state['spec']['replicas'],
    'tag': deployment.current_tag
  }

  service = Service(context)
  service_state = service.state
  if service_state is None:
    return -1
  service_data = {
    'clusterIP': service_state['spec']['clusterIP'],
    'ports': service_state['spec']['ports'],
    'status': service_state['status']
    }

  print_green("Deployment %s" % config.project_name)
  print_green('-----------------------------------------------------------')
  print(yaml.safe_dump(deployment_data, default_flow_style=False))

  print_green("Service %s" % config.project_name)
  print_green('-----------------------------------------------------------')
  print(yaml.safe_dump(service_data, default_flow_style=False))
