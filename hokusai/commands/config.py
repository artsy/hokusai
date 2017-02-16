import os

from collections import OrderedDict
from subprocess import check_output, CalledProcessError, STDOUT
import yaml

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green

def pull_config(context):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s"
                                         % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      try:
        existing_configmap = check_output("kubectl get configmap %s-config -o yaml"
                                        % config.project_name, stderr=STDOUT, shell=True)
        configmap_data = yaml.load(existing_configmap)['data']
      except CalledProcessError, e:
        if 'Error from server: configmaps "%s-config" not found' % config.project_name in e.output:
          configmap_data = {}
        else:
          return -1

      configmap_yaml = OrderedDict([
        ('apiVersion', 'v1'),
        ('kind', 'ConfigMap'),
        ('metadata', {
          'labels': {'app': config.project_name},
          'name': "%s-config" % config.project_name
        }),
        ('data', configmap_data)
      ])

      with open(os.path.join(os.getcwd(), 'hokusai', "%s-config.yml" % context), 'w') as f:
        f.write(yaml.safe_dump(configmap_yaml, default_flow_style=False))

  except CalledProcessError:
    print_red("Failed to pull configmap hokusai/%s-config.yml" % context)
    return -1

  print_green("Pulled configmap hokusai/%s-config.yml" % context)
  return 0

def push_config(context):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s"
                                         % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      check_output("kubectl apply -f %s" % os.path.join(os.getcwd(), 'hokusai', "%s-config.yml" % context), stderr=STDOUT, shell=True)

  except CalledProcessError:
    print_red("Failed to push configmap hokusai/%s-config.yml" % context)
    return -1

  print_green("Pushed configmap hokusai/%s-config.yml" % context)
  return 0
