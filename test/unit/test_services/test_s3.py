import hokusai.services.s3

from hokusai.services.s3 import S3Interface
from test.unit.test_services.fixtures.s3 import mock_s3_client


def describe_s3_interface():

  def describe_init():
    def it_instantiates(mocker, mock_s3_client):
      mocker.patch('hokusai.services.s3.boto3.client', return_value=mock_s3_client)
      mocker.patch('hokusai.services.s3.get_region_name', return_value='fooregion')
      spy = mocker.spy(hokusai.services.s3.boto3, 'client')
      obj = S3Interface()
      assert obj._client is mock_s3_client
      spy.assert_has_calls([
        mocker.call('s3', region_name='fooregion')
      ])

  def describe_download():
    def it_calls_s3_client_download_file(mocker, mock_s3_client):
      mocker.patch('hokusai.services.s3.boto3.client', return_value=mock_s3_client)
      obj = S3Interface()
      spy = mocker.spy(mock_s3_client, 'download_file')
      obj.download('s3://foobucket/path/to/file', 'footargetfile')
      spy.assert_has_calls([
        mocker.call('foobucket', 'path/to/file', 'footargetfile')]
      )
