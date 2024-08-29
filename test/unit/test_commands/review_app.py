import hokusai.commands.review_app

from hokusai.commands.review_app import list_namespaces

from test.unit.test_commands.fixtures.kubectl import mock_kubectl_obj


def describe_list_namespaces():
  def it_lists(mocker, mock_kubectl_obj, capfd):
    mocker.patch('hokusai.commands.review_app.Kubectl', return_value=mock_kubectl_obj)
    spy = mocker.spy(mock_kubectl_obj, 'get_objects')
    list_namespaces('staging', 'foo1=bar1')
    assert spy.call_count == 1
    spy.assert_has_calls([
      mocker.call('namespaces', 'foo1=bar1')
    ])
    out, err = capfd.readouterr()
    assert out == 'namespace1\nnamespace2\n'
