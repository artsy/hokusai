import os

from botocore import session as botosession


def get_region_name():
  # boto3 autodiscovery
  _region = botosession.get_session().get_config_variable('region')
  if _region:
    return _region
  # boto2 compatibility
  if os.environ.get('AWS_REGION'):
    return os.environ.get('AWS_REGION')
  return AWS_DEFAULT_REGION
