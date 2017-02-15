import os

from subprocess import call, check_output, STDOUT

from hokusai.config import HokusaiConfig
from hokusai.common import print_red, print_green

def console(context, shell, tag, env):
  config = HokusaiConfig().check()

  switch_context_result = check_output("kubectl config use-context %s" % context, stderr=STDOUT, shell=True)
  print_green("Switched context to %s" % context)
  if 'no context exists' in switch_context_result:
    print_red("Context %s does not exist.  Check ~/.kube/config" % context)
    return -1

  environment = ' '.join(map(lambda x: '--env="%s"' % x, env))
  if tag is not None:
    image_tag = tag
  else:
    image_tag = context
  call("kubectl run %s-shell-%s -t -i --image=%s:%s --restart=OnFailure --rm %s -- %s" % (config.project_name, os.environ.get('USER'), config.aws_ecr_registry, image_tag, environment, shell), shell=True)
