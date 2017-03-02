import unittest
import mock
import shutil
import os
import json

from boto3 import resource

from forms_990_indicies import get_only_json_filenames, Forms990Indicies

TESTING_CACHE_DIR = 'testing-cache-dir'

class MockBucket():
    def download_file(self, name, dest):
        somedata = {
          u'testdata': {
            u'whatwewant': name
          }
        }
        with open(dest, 'w') as fd:
            json.dump(somedata, fd)

class TestForms990Indicies(unittest.TestCase):

    def setUp(self):
        os.makedirs(TESTING_CACHE_DIR)

    def tearDown(self):
        shutil.rmtree(TESTING_CACHE_DIR)
        return

    def test_get_only_json_filenames(self):
        only_jsons = get_only_json_filenames({u'Contents': [
          {u'Key': u'index1999.json'},
          {u'Key': u'index1999.csv'},
        ]})
        self.assertEqual([
          u'index1999.json',
        ], only_jsons)

    def test_instantiation(self):
        mock_s3_resource = mock.create_autospec(resource('s3'))
        mock_s3_resource.Bucket.return_value = MockBucket()

        indicies = Forms990Indicies(mock_s3_resource)

        indicies.CACHE_DIR = TESTING_CACHE_DIR

        mock_s3_resource.meta.client.list_objects.return_value = {u'Contents': [
          {u'Key': u'index1999.json'},
          {u'Key': u'index1999.csv'},
          {u'Key': u'index2000.json'},
          {u'Key': u'index2000.csv'},
        ]}

        indicies.get_indicies()
        mock_s3_resource.meta.client.list_objects.assert_called_with(Bucket='irs-form-990', Prefix='index')

        self.assertEqual([
          u'index1999.json',
          u'index2000.json',
        ], indicies.indicies)

        indicies.save_all_indicies()

        self.assertEqual(indicies.get_json_for_index('index1999.json'), {'whatwewant': 'index1999.json'})
        self.assertEqual(indicies.get_json_for_index('index2000.json'), {'whatwewant': 'index2000.json'})
