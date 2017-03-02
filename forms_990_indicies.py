from tempfile import NamedTemporaryFile
import os
import errno
from shutil import copyfile
import json

CACHE_DIR = 'cached-data'

BUCKET_NAME = 'irs-form-990'

def get_only_json_filenames(indicies):
    return map(lambda f: f.get('Key'), filter(lambda e: e.get('Key').endswith('.json'), indicies.get('Contents')))

class Forms990Indicies:

    """Provide a boto3 s3 resource that you create with boto3.resource('s3')"""
    def __init__(self, boto3_s3_resource):
        self.indicies = {}
        self.saved_jsons = {}
        self.CACHE_DIR = CACHE_DIR
        self.BUCKET_NAME = BUCKET_NAME
        self.s3_resource = boto3_s3_resource

    """
    Retrieves the names of yearly index data files from the IRS Form 990 dataset,

    The index file object names are stored in the class property indicies
    """
    def get_indicies(self):
        all_indicies = self.s3_resource.meta.client.list_objects(Bucket=BUCKET_NAME, Prefix='index')
        self.indicies = get_only_json_filenames(all_indicies)

    def make_cache_dir(self):
        try:
            os.makedirs(self.CACHE_DIR)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def save_s3_object(self, name):
        self.make_cache_dir()
        cached_file = os.path.join(self.CACHE_DIR, name)

        if not os.path.isfile(cached_file):
            fd = NamedTemporaryFile(delete=False)
            bucket = self.s3_resource.Bucket(self.BUCKET_NAME)
            bucket.download_file(name, fd.name)
            fd.close()
            copyfile(fd.name, cached_file)

        cached_fd = open(cached_file, 'r')
        self.saved_jsons[name] = cached_fd

    """
    Retrieves all yearly index data from the IRS Form 990 dataset.

    Locally caches the files in the directory cached-data.
    After calling this method, you can access the indicies property to discover
    each year's file name, and then use the get_json_for_index method to load
    that index data into memory.
    """
    def save_all_indicies(self):
        self.get_indicies()
        for name in self.indicies:
          self.save_s3_object(name)

    """Load a certain index file's data"""
    def get_json_for_index(self, name):
        data = json.load(self.saved_jsons[name]).popitem()[1]
        self.saved_jsons[name].seek(0)
        return data

    """
    Remove cached files.

    This will only remove files that have been loaded since the class was instantiated;
    it will not remove files from a previous run.
    """
    def cleanup(self):
        if self.saved_jsons:
            os.unlink(self.saved_jsons.popitem()[1].name)
            self.cleanup()

