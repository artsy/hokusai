import os
import base64

from subprocess import call, check_output, CalledProcessError, STDOUT

import yaml

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green, k8s_uuid

def console(context, shell, tag, with_config, with_secrets, env):
  config = HokusaiConfig().check()

  try:
    switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
    print_green("Switched context to %s" % context)
    if 'no context exists' in switch_context_result:
      print_red("Context %s does not exist.  Check ~/.kube/config" % context)
      return -1

    if tag is not None:
      image_tag = tag
    else:
      image_tag = context

    env = list(env)

    if with_config:
      try:
        existing_configmap = check_output("kubectl get configmap %s-config -o yaml"
                                            % config.project_name, stderr=STDOUT, shell=True)
        configmap_data = yaml.load(existing_configmap)['data']
      except CalledProcessError, e:
          if 'Error from server: configmaps "%s-config" not found' % config.project_name in e.output:
            configmap_data = {}
          else:
            raise

      for k, v in configmap_data.iteritems():
        env.append("%s=%s" % (k, v))

    if with_secrets:
      try:
        existing_secrets = check_output("kubectl get secret %s-secrets -o yaml"
                                        % config.project_name, stderr=STDOUT, shell=True)
        secret_data = yaml.load(existing_secrets)['data']
      except CalledProcessError, e:
        if 'Error from server: secrets "%s-secrets" not found' % config.project_name in e.output:
          secret_data = {}
        else:
          raise

      for k, v in secret_data.iteritems():
        try:
          env.append("%s=%s" % (k, base64.b64decode(v)))
        except TypeError:
          continue

    environment = ' '.join(map(lambda x: '--env="%s"' % x, env))

    if os.environ.get('USER') is not None:
      job_id = "%s-%s" % (os.environ.get('USER'), k8s_uuid())
    else:
      job_id = k8s_uuid()

    call("kubectl run %s-shell-%s -t -i --image=%s:%s --restart=OnFailure --rm %s -- %s" %
         (config.project_name, job_id, config.aws_ecr_registry, image_tag, environment, shell), shell=True)
  except CalledProcessError:
    print_red("Failed to launch console")
    return -1
