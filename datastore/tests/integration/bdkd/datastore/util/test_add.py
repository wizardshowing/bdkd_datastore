# Copyright 2015 Nicta
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
import bdkd.datastore
from bdkd.datastore.util import ds_util
import glob, os, shutil

FIXTURES = os.path.join(os.path.dirname(__file__), 
    '..', '..', '..', '..', 'fixtures')

class DatastoreUtilsAddTest(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.repository = bdkd.datastore.repository("bdkd-datastore-test")
        self.assertTrue(self.repository)
        self.assertTrue(self.repository.get_bucket())


    def setUp(self):
        # Start with the test bucket empty
        for key in self.repository.get_bucket().list():
            key.delete()
        self._clear_local()
        self.filepath = os.path.join(FIXTURES, 'FeatureCollections', 'Coastlines', 
                    'Seton_etal_ESR2012_Coastlines_2012.1.gpmlz')
        self.metadatafile = os.path.join(FIXTURES, 'meta.yml')


    def test_create_resource(self):
        """
        Simulate creating a Resource from the command-line, with only a basic set
        of options (same as `datastore-util create`) and no metadata.
        """
        args_in = [ 'create', '--no-publish', 'bdkd-datastore-test', 'my_resource',
                self.filepath 
                ]
        ds_util.ds_util(args_in)
        self._check_bucket_count('', 2)


    def test_create_resource_with_metadata(self):
        """
        Simulate creating a Resource from the command-line, including all metadata
        options (same as `datastore-util create`).
        """
        args_in = [ 'create',
                '--description', 'Description of resource',
                '--author', 'fred', 
                '--author-email', 'fred@here',
                '--version', '1.0',
                '--maintainer', 'Joe',
                '--maintainer-email', 'joe@here',
                'bdkd-datastore-test', 'my_resource',
                self.filepath 
                ]
        ds_util.ds_util(args_in)
        self._check_bucket_count('', 2)

    def test_create_resource_with_no_files(self):
        """
        Simulate creating a Resource from the command-line, with no files
        provided
        """
        args_in = [ 'create',
                '--description', 'Description of resource',
                '--author', 'fred',
                '--author-email', 'fred@here',
                '--version', '1.0',
                '--maintainer', 'Joe',
                '--maintainer-email', 'joe@here',
                'bdkd-datastore-test', 'my_resource',
                ]
        ds_util.ds_util(args_in)
        self._check_bucket_count('', 1)
        # Ensure no files stored
        added = self.repository.get('my_resource')
        self.assertTrue(added)
        self.assertEquals(added.files, [])

    def test_create_unpublished_resource_with_metadata(self):
        """
        Simulate creating a Resource from the command-line, including all metadata
        options (same as `datastore-util create`), but with --no-publish.
        """
        args_in = [ 'create', '--no-publish',
                '--description', 'Description of resource',
                '--author', 'fred',
                '--author-email', 'fred@here',
                '--version', '1.0',
                '--maintainer', 'Joe',
                '--maintainer-email', 'joe@here',
                'bdkd-datastore-test', 'my_resource',
                self.filepath
                ]
        ds_util.ds_util(args_in)
        self._check_bucket_count('', 2)
        # Ensure metadata is stored
        added = self.repository.get('my_resource')
        self.assertTrue(added)
        self.assertEquals('Description of resource',
                          added.meta('description'))
        self.assertEquals('fred',
                          added.meta('author'))
        self.assertEquals('fred@here',
                          added.meta('author_email'))
        self.assertEquals('1.0',
                          added.meta('version'))
        self.assertEquals('Joe',
                          added.meta('maintainer'))
        self.assertEquals('joe@here',
                          added.meta('maintainer_email'))

    def test_create_published_resource_with_complex_metadata(self):
        """
        Supply metadata both via command line and via metadata file.
        """
        args_in = [ 'create',
                '--description', 'Description of resource',
                '--version', '1.0',
                '--maintainer', 'Joe',
                '--maintainer-email', 'joe@here',
                '--metadata-file', self.metadatafile,
                 'bdkd-datastore-test', 'my_resource',
                self.filepath
                ]
        ds_util.ds_util(args_in)
        # Ensure mixing metadata args and file metadata works as expected
        added = self.repository.get('my_resource')
        self.assertTrue(added)
        self.assertEquals('Description of resource',
                          added.meta('description'))
        self.assertEquals('Jane Researcher',
                          added.meta('author'))
        self.assertEquals('jane@sydney.edu.au',
                          added.meta('author_email'))
        self.assertEquals('1.0',
                          added.meta('version'))
        self.assertEquals('Joe',
                          added.meta('maintainer'))
        self.assertEquals('joe@here',
                          added.meta('maintainer_email'))

    def test_create_resource_without_metadata_fails(self):
        """
        Supply some metadata but not all mandatory fields in published mode.
        """
        args_in = [ 'create',
                '--description', 'Description of resource',
                '--version', '1.0',
                '--maintainer', 'Joe',
                '--maintainer-email', 'joe@here',
                 'bdkd-datastore-test', 'my_resource',
                self.filepath
                ]
        with self.assertRaises(ValueError):
            ds_util.ds_util(args_in)

    def test_create_duplicate_resource(self):
        """
        Adding a resource of the same name (duplicate) should fail with a 
        ValueError, unless the user provides the '--force' flag.
        """
        args_in = [ 'create', '--no-publish', 'bdkd-datastore-test', 'my_resource',
                self.filepath 
                ]
        ds_util.ds_util(args_in)
        self._check_bucket_count('', 2)
        # Again: error (already exists)
        with self.assertRaises(ValueError):
            ds_util.ds_util(args_in)
        # Do it properly
        args_in.append('--force')
        try:
            ds_util.ds_util(args_in)
        except ValueError:
            self.fail("Flag '--force' should allow overwrite of resource.")


    def _check_bucket_count(self, pseudopath, expected):
        # Check that S3 repository has two keys in it
        key_count = 0
        for key in self.repository.get_bucket().list(pseudopath):
            key_count += 1
        self.assertEqual(key_count, expected)

        
    def _clear_local(self):
        for tmp_path in [ self.repository.local_cache ]:
            if tmp_path and tmp_path.startswith('/var/tmp'):
                if os.path.exists(tmp_path):
                    shutil.rmtree(tmp_path)
