import datetime

from hokusai.lib.config import config
from hokusai.lib.s3 import append_or_create_object

def log_configmap_changes(context, namespace, action, varlist):
  var_names = []
  for s in varlist:
    # if the vars are being set, varlist is a list of key=value pairs.
    # if the vars are being unset, varlist is a list of keys.
    # in either case, split returns the key.
    # what if user mistakenly pass value=key? we log the value which can be a secret. yikes!
    split = s.split('=', 1)
    var_names.append(split[0])

  # ugly, but upstream passes None for default namespace.
  if (namespace is None):
    ns = 'default'
  else:
    ns = namespace

  timestamp = datetime.datetime.utcnow()
  log = "time: %s, namespace: %s, action: %s, var: %s\n" % (timestamp, ns, action, ' '.join(var_names))

  # TODO: pass bucket/key in as a var.
  s3_bucket = 'artsy-hokusai'
  s3_key = 'configmap-changes/' + \
            config.project_name + \
            '/' + context + '/' + \
            datetime.datetime.utcnow().strftime('%Y-%m-%d')

  try:
    # log to s3 object.
    append_or_create_object(log, s3_bucket, s3_key)
  except:
    # catch and ignore all exceptions, failure to log configmap changes shall not be fatal.
    pass
