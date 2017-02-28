import unittest

from forms_990_indicies import get_only_json_filenames

class TestForms990Indicies(unittest.TestCase):
    def test_get_only_json_filenames(self):
        only_jsons = get_only_json_filenames({u'Contents': [
          {u'Key': u'index1999.json'},
          {u'Key': u'index1999.csv'},
        ]})
        self.assertEqual([
          u'index1999.json',
        ], only_jsons)
