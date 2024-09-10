import hokusai.commands.review_app

from hokusai.commands.review_app import (
  create_yaml,
  edit_namespace,
  list_review_apps
)

from test.unit.test_commands.fixtures.kubectl import mock_kubectl_obj


def describe_edit_namespace():
  def describe_good_spec():
    def it_edits():
      spec = {
        'apiVersion': 'v1',
        'metadata': {
          'namespace': 'oldns'
        }
      }
      edit_namespace(spec, 'newns')
      assert spec['metadata']['namespace'] == 'newns'
  def describe_no_apiversion():
    def it_skips():
      spec = {
        'metadata': {
          'namespace': 'oldns'
        }
      }
      edit_namespace(spec, 'newns')
      assert spec['metadata']['namespace'] == 'oldns'
  def describe_no_metadata():
    def it_adds():
      spec = {
        'apiVersion': 'v1'
      }
      edit_namespace(spec, 'newns')
      assert spec['metadata']['namespace'] == 'newns'
  def describe_no_namespace_field():
    def it_adds():
      spec = {
        'apiVersion': 'v1',
        'metadata': {}
      }
      edit_namespace(spec, 'newns')
      assert spec['metadata']['namespace'] == 'newns'

def describe_list_review_apps():
  def it_lists(mocker, mock_kubectl_obj, capfd):
    mocker.patch('hokusai.commands.review_app.Kubectl', return_value=mock_kubectl_obj)
    spy = mocker.spy(mock_kubectl_obj, 'get_objects')
    list_review_apps('staging', 'foo1=bar1')
    assert spy.call_count == 1
    spy.assert_has_calls([
      mocker.call('namespaces', 'foo1=bar1')
    ])
    out, err = capfd.readouterr()
    assert out == 'namespace1\nnamespace2\n'
