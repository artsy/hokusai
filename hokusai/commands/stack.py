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
  deployment_data = []
  for item in deployment.cache:
    deployment_data.append({
      'name': item['metadata']['name'],
      'replicas': item['spec']['replicas'],
      'tag': deployment.current_tag
    })

  service = Service(context)
  service_data = []
  for item in service.cache:
    service_data.append({
      'target': item['spec']['selector']['app'],
      'clusterIP': item['spec']['clusterIP'],
      'ports': item['spec']['ports'],
      'status': item['status']
    })

  print_green("Deployments")
  print_green('-----------------------------------------------------------')
  print(yaml.safe_dump(deployment_data, default_flow_style=False))

  print_green("Services")
  print_green('-----------------------------------------------------------')
  print(yaml.safe_dump(service_data, default_flow_style=False))
