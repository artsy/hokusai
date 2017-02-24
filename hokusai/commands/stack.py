import os

from subprocess import check_output, check_call, CalledProcessError, STDOUT

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, verbose, select_context, HokusaiCommandError

def stack_up(context):
  HokusaiConfig().check()
  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  try:
    select_context(context)
  except HokusaiCommandError, e:
    print_red(repr(e))
    return -1

  try:
    check_call(verbose("kubectl apply -f %s" % kubernetes_yml), shell=True)
  except CalledProcessError, e:
    print_red("Stack up failed with error: %s" % e.output)
    return -1

  print_green("Stack %s created" % kubernetes_yml)
  return 0

def stack_down(context):
  HokusaiConfig().check()

  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  try:
    select_context(context)
  except HokusaiCommandError, e:
    print_red(repr(e))
    return -1

  try:
    check_call(verbose("kubectl delete -f %s" % kubernetes_yml), shell=True)
  except CalledProcessError, e:
    print_red("Stack down failed with error: %s" % e.output)
    return -1

  print_green("Stack %s deleted" % kubernetes_yml)
  return 0

def stack_status(context):
  HokusaiConfig().check()

  kubernetes_yml = os.path.join(os.getcwd(), "hokusai/%s.yml" % context)
  if not os.path.isfile(kubernetes_yml):
    print_red("Yaml file %s does not exist for given context." % kubernetes_yml)
    return -1

  try:
    select_context(context)
  except HokusaiCommandError, e:
    print_red(repr(e))
    return -1

  try:
    check_call(verbose("kubectl describe -f %s" % kubernetes_yml), shell=True)
  except CalledProcessError, e:
    print_red("Stack status failed with error: %s" % e.output)
    return -1
  return 0
