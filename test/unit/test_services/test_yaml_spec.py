import json
import pytest

import hokusai.services.yaml_spec

from hokusai.lib.exceptions import HokusaiError
from hokusai.services.yaml_spec import YamlSpec

from test.unit.test_services.fixtures.ecr import mock_ecr_class
from test.unit.test_services.fixtures.yaml_spec import (
  mock_hokusai_yaml,
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

  def describe_all_deployments_configmap_refs():
    def it_returns_configmap_refs(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      spy = mocker.spy(hokusai.services.yaml_spec.atexit, 'register')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      mocker.patch.object(obj, 'get_resources_by_kind', return_value=mock_hokusai_yaml[slice(5)])
      assert obj.all_deployments_configmap_refs() == [
        'foo-common-configmap',
        'foo-deployment1-configmap1',
        'foo-deployment1-configmap2',
        'foo-deployment1-container2-configmap',
        'foo-deployment1-init-container-configmap',
        'foo-deployment2-configmap'
      ]

  def describe_all_deployments_sa_refs():
    def it_returns_sa_ref(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      spy = mocker.spy(hokusai.services.yaml_spec.atexit, 'register')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      mocker.patch.object(obj, 'get_resources_by_kind', return_value=mock_hokusai_yaml[slice(5)])
      assert obj.all_deployments_sa_refs() == [
        'foo-deployment1-sa',
        'foo-deployment2-sa'
      ]

  def describe_container_configmap_refs():
    def it_returns_configmap_refs_and_those_only(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      spy = mocker.spy(hokusai.services.yaml_spec.atexit, 'register')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      assert obj.container_configmap_refs(
        mock_hokusai_yaml[0]['spec']['template']['spec']['containers'][0]
      ) == [
        'foo-common-configmap',
        'foo-deployment1-configmap1',
        'foo-deployment1-configmap2',
      ]
    def it_returns_empty_list_when_envfrom_empty(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      spy = mocker.spy(hokusai.services.yaml_spec.atexit, 'register')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      assert obj.container_configmap_refs(
        mock_hokusai_yaml[2]['spec']['template']['spec']['containers'][0]
      ) == []
    def it_returns_empty_list_when_no_envfrom(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      spy = mocker.spy(hokusai.services.yaml_spec.atexit, 'register')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      assert obj.container_configmap_refs(
        mock_hokusai_yaml[3]['spec']['template']['spec']['containers'][0]
      ) == []

  def describe_containers_configmap_refs():
    def it_returns_configmap_refs(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      spy = mocker.spy(hokusai.services.yaml_spec.atexit, 'register')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      assert obj.containers_configmap_refs(
        mock_hokusai_yaml[0]['spec']['template']['spec']['containers']
      ) == [
        'foo-common-configmap',
        'foo-deployment1-configmap1',
        'foo-deployment1-configmap2',
        'foo-deployment1-container2-configmap'
      ]

  def describe_deployment_configmap_refs():
    def it_returns_configmap_refs(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      spy = mocker.spy(hokusai.services.yaml_spec.atexit, 'register')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      assert obj.deployment_configmap_refs(
        mock_hokusai_yaml[0]
      ) == [
        'foo-common-configmap',
        'foo-deployment1-configmap1',
        'foo-deployment1-configmap2',
        'foo-deployment1-container2-configmap',
        'foo-deployment1-init-container-configmap'
      ]

  def describe_deployment_sa_ref():
    def it_returns_sa_ref(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      spy = mocker.spy(hokusai.services.yaml_spec.atexit, 'register')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      assert obj.deployment_sa_ref(
        mock_hokusai_yaml[0]
      ) == 'foo-deployment1-sa'
    def it_returns_none_when_no_sa_ref(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      spy = mocker.spy(hokusai.services.yaml_spec.atexit, 'register')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      assert obj.deployment_sa_ref(
        mock_hokusai_yaml[2]
      ) == None

  def describe_extract_pod_spec():
    def describe_when_deployment_spec_is_found():
      def it_returns_pod_spec(mocker, mock_hokusai_yaml):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resource_spec', return_value=mock_hokusai_yaml[0])
        assert obj.extract_pod_spec('foo-deployment1') == mock_hokusai_yaml[0]['spec']['template']['spec']
      def it_raises_on_bad_pod_spec(mocker, mock_hokusai_yaml):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resource_spec', return_value=mock_hokusai_yaml[4])
        with pytest.raises(HokusaiError):
          obj.extract_pod_spec('foo-deployment')

    def describe_when_deployment_spec_is_not_found():
      def it_raises_key_error(mocker):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resource_spec', return_value={})
        with pytest.raises(KeyError):
          obj.extract_pod_spec('foo-deployment1')

  def describe_get_resource_spec():
    def describe_when_name_specified():
      def it_returns_spec_when_name_found(mocker, mock_hokusai_yaml):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resources_by_kind', return_value=mock_hokusai_yaml[slice(5)])
        found_spec = obj.get_resource_spec('Deployment', name='foo-deployment2')
        assert found_spec == mock_hokusai_yaml[1]

      def it_raises_when_name_not_found(mocker, mock_hokusai_yaml):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resources_by_kind', return_value=mock_hokusai_yaml[slice(5)])
        with pytest.raises(HokusaiError):
          obj.get_resource_spec('Deployment', name='foo-deployment100')

    def describe_when_name_not_specified():
      def it_returns_first_matching_kind(mocker, mock_hokusai_yaml):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resources_by_kind', return_value=mock_hokusai_yaml[slice(5)])
        found_spec = obj.get_resource_spec('Deployment')
        assert found_spec == mock_hokusai_yaml[0]

      def it_raises_when_there_is_no_matching_kind(mocker):
        mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
        mocker.patch('hokusai.services.yaml_spec.atexit')
        obj = YamlSpec('test/fixtures/kubernetes-config.yml')
        mocker.patch.object(obj, 'get_resources_by_kind', return_value=[])
        with pytest.raises(HokusaiError):
          obj.get_resource_spec('Deployment')

  def describe_get_resources_by_kind():
    def it_returns_resources_when_kind_matches(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      mocker.patch.object(obj, 'to_list', return_value=mock_hokusai_yaml)
      assert obj.get_resources_by_kind('Deployment') == mock_hokusai_yaml[slice(5)]
    def it_returns_empty_list_when_no_kind_matches(mocker, mock_hokusai_yaml):
      mocker.patch('hokusai.services.yaml_spec.ECR', return_value='foo')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      mocker.patch.object(obj, 'to_list', return_value=mock_hokusai_yaml)
      expected_return_value = []
      assert obj.get_resources_by_kind('fake-kind') == expected_return_value

  def describe_to_file():
    def it_returns_file_name(mocker, monkeypatch):
      mocker.patch('hokusai.services.yaml_spec.ECR')
      mocker.patch('hokusai.services.yaml_spec.atexit')
      mocker.patch('hokusai.services.yaml_spec.ConfigLoader')
      mocker.patch('hokusai.services.yaml_spec.TemplateRenderer')
      mocker.patch('hokusai.services.yaml_spec.write_temp_file', return_value='foofile')
      write_temp_file_spy = mocker.spy(hokusai.services.yaml_spec, 'write_temp_file')
      mock_hokusai_tmp_dir = 'hokusaitmpdir'
      monkeypatch.setattr(hokusai.services.yaml_spec, "HOKUSAI_TMP_DIR", mock_hokusai_tmp_dir)
      obj = YamlSpec('test/fixtures/kubernetes-config.yml')
      mocker.patch.object(obj, 'to_string', return_value='foo')
      file_name = obj.to_file()
      write_temp_file_spy.assert_called_once_with(
        'foo',
        mock_hokusai_tmp_dir
      )
      assert file_name == 'foofile'

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
