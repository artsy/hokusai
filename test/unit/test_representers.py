from collections import OrderedDict

import yaml

from test import HokusaiUnitTestCase

class TestRepresenters(HokusaiUnitTestCase):
  def test_represent_odict(self):
    obj = OrderedDict([
      ('foo', 'bar'),
      ('baz', ['hello']),
      ('spam', {'with': 'eggs'})
    ])
    payload = yaml.safe_dump(obj, default_flow_style=False)
    deserialized_obj = yaml.load(payload, Loader=yaml.FullLoader)
    self.assertEqual(deserialized_obj['foo'], 'bar')
    self.assertEqual(deserialized_obj['baz'], ['hello'])
    self.assertEqual(deserialized_obj['spam']['with'], 'eggs')
