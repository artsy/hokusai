import pytest

from tempfile import NamedTemporaryFile

import hokusai.services.yaml_spec

from hokusai.lib.exceptions import HokusaiError
from hokusai.services.yaml_spec import YamlSpec

from test.unit.test_services.fixtures.ecr import mock_ecr_class
from test.unit.test_services.fixtures.yaml_spec import (
  mock_hokusai_yaml,
  mock_hokusai_yaml_deployment,
  mock_hokusai_yaml_deployment_one,
  mock_hokusai_yaml_deployment_one_bad,
  test_k8s_spec_as_string
)


def describe_yaml_spec():
  def describe_init():
    def it_instantiates(mocker):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      spy = mocker.spy(hokusai.services.yaml_spec.atexit, 'register')
      obj = YamlSpec('foo.yml')
      assert obj.template_file == 'foo.yml'
      assert obj.render_template == True
      assert obj.ecr == 'foo'
      spy.assert_has_calls([
        mocker.call(obj.cleanup)
      ])

  def describe_extract_pod_spec():
    def describe_when_deployment_spec_is_found():
      def it_returns_pod_spec(mocker, mock_hokusai_yaml_deployment_one):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resource_spec', return_value=mock_hokusai_yaml_deployment_one)
        assert obj.extract_pod_spec('foo-deployment') == {
          'containers': ['foo-deployment1-container']
        }
      def it_raises_on_bad_pod_spec(mocker, mock_hokusai_yaml_deployment_one_bad):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resource_spec', return_value=mock_hokusai_yaml_deployment_one_bad)
        with pytest.raises(HokusaiError):
          obj.extract_pod_spec('foo-deployment')

    def describe_when_deployment_spec_is_not_found():
      def it_raises_key_error(mocker, mock_hokusai_yaml_deployment_one):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resource_spec', return_value={})
        with pytest.raises(KeyError):
          obj.extract_pod_spec('foo-deployment')

  def describe_get_resource_spec():
    def describe_when_name_specified():
      def it_returns_spec_when_name_found(mocker, mock_hokusai_yaml_deployment):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resources_by_kind', return_value=mock_hokusai_yaml_deployment)
        found_spec = obj.get_resource_spec('Deployment', name='foo-deployment2')
        assert found_spec == {
          'apiVersion': 'apps/v1',
          'kind': 'Deployment',
          'metadata': {
            'name': 'foo-deployment2'
          },
          'spec': {
            'template': {
              'spec': {
                'containers': ['foo-deployment2-container']
              }
            }
          }
        }
      def it_raises_when_name_not_found(mocker, mock_hokusai_yaml_deployment):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resources_by_kind', return_value=mock_hokusai_yaml_deployment)
        with pytest.raises(HokusaiError):
          obj.get_resource_spec('Deployment', name='foo-deployment3')

    def describe_when_name_not_specified():
      def it_returns_first_matching_kind(mocker, mock_hokusai_yaml_deployment):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resources_by_kind', return_value=mock_hokusai_yaml_deployment)
        found_spec = obj.get_resource_spec('Deployment')
        assert found_spec == {
          'apiVersion': 'apps/v1',
          'kind': 'Deployment',
          'metadata': {
            'name': 'foo-deployment1'
          },
          'spec': {
            'template': {
              'spec': {
                'containers': ['foo-deployment1-container']
              }
            }
          }
        }
      def it_raises_when_there_is_no_matching_kind(mocker, mock_hokusai_yaml_deployment):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resources_by_kind', return_value=[])
        with pytest.raises(HokusaiError):
          obj.get_resource_spec('Deployment')

  def describe_get_resources_by_kind():
    def it_returns_resources_when_kind_matches(mocker, mock_hokusai_yaml, mock_hokusai_yaml_deployment):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      mocker.patch.object(obj, 'to_list', return_value=mock_hokusai_yaml)
      assert obj.get_resources_by_kind('Deployment') == mock_hokusai_yaml_deployment
    def it_returns_empty_list_when_no_kind_matches(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      mocker.patch.object(obj, 'to_list', return_value=mock_hokusai_yaml)
      expected_return_value = []
      assert obj.get_resources_by_kind('fake-kind') == expected_return_value

  def describe_to_file():
    def it_returns_file_name(mocker, tmp_path):
      mocker.patch('hokusai.services.yaml_spec.ECR')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      mocker.patch('hokusai.services.yaml_spec.ConfigLoader')
      mocker.patch('hokusai.services.yaml_spec.TemplateRenderer')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      mocker.patch.object(obj, 'to_string', return_value='foo')
      f = NamedTemporaryFile(delete=False, dir=tmp_path, mode='w')
      mocker.patch('hokusai.services.yaml_spec.NamedTemporaryFile', return_value=f)
      file_name = obj.to_file()
      assert file_name == f.name
      content = ''
      with open(file_name, 'r') as f:
        content = f.read().strip()
      assert content == 'foo'

  def describe_to_list():
    def it_returns_list(mocker):
      mocker.patch('hokusai.services.yaml_spec.ECR')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      mocker.patch('hokusai.services.yaml_spec.ConfigLoader')
      mocker.patch('hokusai.services.yaml_spec.TemplateRenderer')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      template_yaml = '''
        'foo': 'bar'
        'bar': 'foo'
      '''
      mocker.patch.object(obj, 'to_string', return_value=template_yaml)
      template_list = obj.to_list()
      assert template_list == [{'bar': 'foo', 'foo': 'bar'}]

  def describe_to_string():
    def describe_render_template_true():
      def it_calls_template_renderer(mocker, mock_ecr_class):
        mock_ecr_obj = mock_ecr_class()
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value=mock_ecr_obj)
        mocker.patch('hokusai.services.yaml_spec.atexit')
        mocker.patch('hokusai.services.yaml_spec.ConfigLoader')
        mock_template_renderer_obj = mocker.patch('hokusai.services.yaml_spec.TemplateRenderer')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        template_string = obj.to_string()
        mock_template_renderer_obj.assert_has_calls([
          mocker.call(
            'test/fixtures/kubernetes-config.yml',
            {
              'project_name': 'hello',
              'project_repo': 'foo'
            }
          ),
          mocker.call().render()
        ])
        assert template_string._extract_mock_name() == 'TemplateRenderer().render()'
    def describe_render_template_false():
      def it_does_not_call_template_renderer(mocker, test_k8s_spec_as_string):
        mocker.patch('hokusai.services.yaml_spec.ECR')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        mocker.patch('hokusai.services.yaml_spec.ConfigLoader')
        mock_template_renderer_obj = mocker.patch('hokusai.services.yaml_spec.TemplateRenderer')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml', render_template=False)
        template_string = obj.to_string()
        assert not mock_template_renderer_obj.called
        assert template_string == test_k8s_spec_as_string
