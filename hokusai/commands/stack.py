from subprocess import check_output, check_call, CalledProcessError, STDOUT

from hokusai.config import HokusaiConfig
from hokusai.common import *

def stack_up(context):
  config = HokusaiConfig().check()
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  try:
    switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      check_call("kubectl apply -f %s" % kubernetes_yml, shell=True)
  except CalledProcessError:
    print_red('Stack up failed')
    return -1

  print_green("Stack %s created" % kubernetes_yml)
  return 0

def stack_down(context):
  config = HokusaiConfig().check()
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  try:
    switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      check_call("kubectl delete -f %s" % kubernetes_yml, shell=True)
  except CalledProcessError:
    print_red('Stack down failed')
    return -1

  print_green("Stack %s deleted" % kubernetes_yml)
  return 0

def stack_status(context):
  config = HokusaiConfig().check()
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  try:
    switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1
    elif 'switched to context' in switch_context_result:
      check_call("kubectl describe -f %s" % kubernetes_yml, shell=True)
  except CalledProcessError:
    print_red('Stack status failed')
    return -1
  return 0

