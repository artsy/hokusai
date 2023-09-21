import boto3

from hokusai.lib.common import get_region_name, print_red, verbose_print_green


class S3Interface:
  ''' interface with AWS S3 '''
  def __init__(self):
    self.client = boto3.client('s3', region_name=get_region_name())

  def download(self, uri, target_file):
    ''' download s3://bucket/foo/bar to target_file '''
    parsed_uri = urlparse(uri)
    bucket_name = parsed_uri.netloc
    key_name = parsed_uri.path.lstrip('/')
    verbose_print_green(f'Downloading {uri} to {target_file} ...', newline_after=True)
    try:
      self.client.download_file(bucket_name, key_name, target_file)
    except:
      print_red(f'Error: Failed to download {uri} to {target_file}')
      raise

s3_interface = S3Interface()
