from hokusai.lib.k8s_spec import add_env
from test import HokusaiUnitTestCase

class TestAddEnv(HokusaiUnitTestCase):
  def setUp(self):
    self.newvar = {'name': 'foo', 'value': 'bar'}
  def test_no_env(self):
    spec = {}
    self.assertEqual(add_env(spec, self.newvar), [self.newvar])
  def test_empty_env(self):
    spec = {'env': []}
    self.assertEqual(add_env(spec, self.newvar), [self.newvar])
  def test_none_env(self):
    spec = {'env': None}
    self.assertEqual(add_env(spec, self.newvar), [self.newvar])
  def test_has_var_already(self):
    spec = {'env': [self.newvar]}
    self.assertEqual(add_env(spec, self.newvar), [self.newvar])
  def test_has_var_twice(self):
    spec = {'env': [self.newvar, self.newvar]}
    self.assertEqual(add_env(spec, self.newvar), [self.newvar])
  def test_has_different_var(self):
    other_var = {'name': 'bar', 'value': 'foo'}
    spec = {'env': [other_var]}
    self.assertEqual(add_env(spec, self.newvar), [other_var, self.newvar])
  def test_has_var_with_same_name_but_different_value(self):
    other_var = {'name': 'foo', 'value': 'baz'}
    spec = {'env': [other_var]}
    self.assertEqual(add_env(spec, self.newvar), [self.newvar])
  def test_has_var_and_a_different_var(self):
    other_var = {'name': 'bar', 'value': 'foo'}
    spec = {'env': [self.newvar, other_var]}
    self.assertEqual(add_env(spec, self.newvar), [other_var, self.newvar])
  def test_has_a_different_var_and_var(self):
    other_var = {'name': 'bar', 'value': 'foo'}
    spec = {'env': [other_var, self.newvar]}
    self.assertEqual(add_env(spec, self.newvar), [other_var, self.newvar])
