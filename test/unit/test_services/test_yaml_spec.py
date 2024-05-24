from tempfile import NamedTemporaryFile

import hokusai.services.yaml_spec

from hokusai.services.yaml_spec import YamlSpec

from test.unit.test_services.fixtures.ecr import mock_ecr_class
from test.unit.test_services.fixtures.yaml_spec import test_k8s_spec_as_string


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
