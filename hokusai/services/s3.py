import boto3

from urllib.parse import urlparse

# blanket import to avoid circular import error
import hokusai.lib.common as common


class S3Interface:
  ''' interface with AWS S3 '''
  def __init__(self):
    self._client = boto3.client(
      's3', region_name=common.get_region_name()
    )

  def download(self, uri, target_file):
    ''' download s3://bucket/foo/bar to target_file '''
    parsed_uri = urlparse(uri)
    bucket_name = parsed_uri.netloc
    key_name = parsed_uri.path.lstrip('/')
    if common.get_verbosity():
      common.print_green(
        f'Downloading {uri} to {target_file} ...',
        newline_after=True
      )
    try:
      self._client.download_file(
        bucket_name, key_name, target_file
      )
    except:
      common.print_red(
        f'Error: Failed to download {uri} to {target_file}'
      )
      raise
