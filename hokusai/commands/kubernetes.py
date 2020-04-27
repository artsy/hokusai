import os

from hokusai import CWD
from hokusai.lib.command import command
from hokusai.lib.config import HOKUSAI_CONFIG_DIR, config
from hokusai.lib.common import print_green, shout, returncode
from hokusai.lib.template_selector import TemplateSelector
from hokusai.services.ecr import ECR
from hokusai.services.kubectl import Kubectl
from hokusai.services.configmap import ConfigMap
from hokusai.services.yaml_spec import YamlSpec
from hokusai.lib.exceptions import HokusaiError

@command()
def k8s_create(context, tag='latest', namespace=None, filename=None, environment=()):
  if filename is None:
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, context))
  else:
    yaml_template = TemplateSelector().get(filename)

  ecr = ECR()
  if not ecr.project_repo_exists():
    raise HokusaiError("ECR repository %s does not exist... did you run `hokusai setup` for this project?" % config.project_name)

  if not ecr.tag_exists(tag):
    raise HokusaiError("Image tag %s does not exist... did you run `hokusai registry push`?" % tag)

  if tag is 'latest' and not ecr.tag_exists(context):
    ecr.retag(tag, context)
    print_green("Updated tag 'latest' -> %s" % context)

  if filename is None:
    configmap = ConfigMap(context, namespace=namespace)
    for s in environment:
      if '=' not in s:
        raise HokusaiError("Error: environment variables must be of the form 'KEY=VALUE'")
      split = s.split('=', 1)
      configmap.update(split[0], split[1])
    configmap.create()
    print_green("Created configmap %s-environment" % config.project_name)

  kctl = Kubectl(context, namespace=namespace)
  yaml_spec = YamlSpec(yaml_template).to_file()

  shout(kctl.command("create --save-config -f %s" % yaml_spec), print_output=True)
  print_green("Created Kubernetes environment %s" % yaml_template)


@command()
def k8s_update(context, namespace=None, filename=None, check_branch="master",
                check_remote=None, skip_checks=False, dry_run=False):
  if filename is None:
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, context))
  else:
    yaml_template = TemplateSelector().get(filename)

  if not skip_checks:
    current_branch = None
    for branchname in shout('git branch').splitlines():
      if '* ' in branchname:
        current_branch = branchname.replace('* ', '')
        break

    if 'detached' in current_branch:
      raise HokusaiError("Not on any branch!  Aborting.")
    if current_branch != check_branch:
      raise HokusaiError("Not on %s branch!  Aborting." % check_branch)

    remotes = [check_remote] if check_remote else shout('git remote').splitlines()
    for remote in remotes:
      shout("git fetch %s" % remote)
      if returncode("git diff --quiet %s/%s" % (remote, current_branch)):
        raise HokusaiError("Local branch %s is divergent from %s/%s.  Aborting." % (current_branch, remote, current_branch))

  kctl = Kubectl(context, namespace=namespace)
  yaml_spec = YamlSpec(yaml_template).to_file()

  if dry_run:
    shout(kctl.command("apply -f %s --dry-run" % yaml_spec), print_output=True)
    print_green("Updated Kubernetes environment %s (dry run)" % yaml_template)
  else:
    shout(kctl.command("apply -f %s" % yaml_spec), print_output=True)
    print_green("Updated Kubernetes environment %s" % yaml_template)


@command()
def k8s_delete(context, namespace=None, filename=None):
  if filename is None:
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, context))
  else:
    yaml_template = TemplateSelector().get(filename)

  if filename is None:
    configmap = ConfigMap(context, namespace=namespace)
    configmap.destroy()
    print_green("Deleted configmap %s-environment" % config.project_name)

  kctl = Kubectl(context, namespace=namespace)
  yaml_spec = YamlSpec(yaml_template).to_file()

  shout(kctl.command("delete -f %s" % yaml_spec), print_output=True)
  print_green("Deleted Kubernetes environment %s" % yaml_template)


@command()
def k8s_status(context, resources, pods, describe, top, namespace=None, filename=None):
  if filename is None:
    yaml_template = TemplateSelector().get(os.path.join(CWD, HOKUSAI_CONFIG_DIR, context))
  else:
    yaml_template = TemplateSelector().get(filename)

  kctl = Kubectl(context, namespace=namespace)
  yaml_spec = YamlSpec(yaml_template).to_file()

  if describe:
    kctl_cmd = "describe"
    output = ""
  else:
    kctl_cmd = "get"
    output = " -o wide"
  if resources:
    print_green("Resources", newline_before=True)
    print_green("===========")
    shout(kctl.command("%s -f %s%s" % (kctl_cmd, yaml_spec, output)), print_output=True)
  if pods:
    print_green("Pods", newline_before=True)
    print_green("===========")
    shout(kctl.command("%s pods --selector app=%s,layer=application%s" % (kctl_cmd, config.project_name, output)), print_output=True)
  if top:
    print_green("Top Pods", newline_before=True)
    print_green("===========")
    shout(kctl.command("top pods --selector app=%s,layer=application" % config.project_name), print_output=True)



@command()
def k8s_copy_config(context, destination_namespace, name=None):
  source_configmap = ConfigMap(context, name=name)
  destination_configmap = ConfigMap(context, name=name, namespace=destination_namespace)
  source_configmap.load()
  destination_configmap.struct['data'] = source_configmap.struct['data']
  destination_configmap.save()
