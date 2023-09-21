import boto3

from urllib.parse import urlparse

import hokusai.lib.common as common

from hokusai.services.aws import get_region_name


class S3Interface:
  ''' interface with AWS S3 '''
  def __init__(self):
    self.client = boto3.client('s3', region_name=get_region_name())

  def download(self, uri, target_file):
    ''' download s3://bucket/foo/bar to target_file '''
    parsed_uri = urlparse(uri)
    bucket_name = parsed_uri.netloc
    key_name = parsed_uri.path.lstrip('/')
    common.verbose_print_green(f'Downloading {uri} to {target_file} ...', newline_after=True)
    try:
      self.client.download_file(bucket_name, key_name, target_file)
    except:
      common.print_red(f'Error: Failed to download {uri} to {target_file}')
      raise

s3_interface = S3Interface()
