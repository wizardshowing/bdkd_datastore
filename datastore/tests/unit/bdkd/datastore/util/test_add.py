# -*- coding: utf-8 -*-
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
from mock import patch, ANY
import argparse

import os
# Load a custom configuration for unit testing
os.environ['BDKD_DATASTORE_CONFIG'] = os.path.join(
        os.path.dirname(__file__), '..', '..', '..', 'conf', 'test.conf')
from bdkd.datastore.util import ds_util

FIXTURES = os.path.join(os.path.dirname(__file__), 
    '..', '..', '..', '..', 'fixtures')


class CreateTest(unittest.TestCase):

    def setUp(self):
        self.filepath = os.path.join(FIXTURES, 'FeatureCollections', 'Coastlines', 
                    'Seton_etal_ESR2012_Coastlines_2012.1.gpmlz')
        self.parser = argparse.ArgumentParser()
        subparser = self.parser.add_subparsers(dest='subcmd')
        ds_util._create_subparsers(subparser)


    def test_create_minimal_arguments(self):
        args_in = [ 'create', '--no-publish', 'test-repository', 'my_resource',
                self.filepath ]
        args = self.parser.parse_args(args_in)
        self.assertTrue(args)
        self.assertEquals(args.repository.name, 'test-repository')
        self.assertEquals(args.resource_name, 'my_resource')
        self.assertEquals(args.publish, False)
        self.assertEquals(args.force, False)  # See corresponding below
        self.assertEquals(args.filenames[0], self.filepath)


    def test_create_bad_path(self):
        args_in = [ 'create', '--no-publish', 'test-repository', 'my_resource',
                'some/nonexistent/file' ]
        self.assertRaises(ValueError, self.parser.parse_args, args_in)

    def test_create_no_files(self):
        args_in = [ 'create', '--no-publish', 'test-repository', 'my_resource' ]
        args = self.parser.parse_args(args_in)
        self.assertTrue(args)
        self.assertEquals(args.repository.name, 'test-repository')
        self.assertEquals(args.resource_name, 'my_resource')
        self.assertEquals(args.publish, False)
        self.assertEquals(args.force, False)  # See corresponding below

    def test_create_published_default(self):
        args_in = [ 'create', 'test-repository', 'my_resource' ]
        args = self.parser.parse_args(args_in)
        self.assertTrue(args)
        self.assertEquals(args.repository.name, 'test-repository')
        self.assertEquals(args.resource_name, 'my_resource')
        self.assertEquals(args.publish, True)

    def test_create_incorrect_publish(self):
        # specifying both --publish and --no-publish
        args_in = [ 'create', '--no-publish', '--publish' 'test-repository', 'my_resource',
                'some/nonexistent/file' ]
        self.assertRaises(ValueError, self.parser.parse_args, args_in)

    def test_create_all_arguments(self):
        args_in = [ 'create', '--force', '--bundle', '--no-publish',
                    'test-repository', 'my_resource',
                    self.filepath ]
        args = self.parser.parse_args(args_in)
        self.assertTrue(args)
        self.assertEquals(args.force, True)
        self.assertEquals(args.bundle, True)


    def test_create_mandatory_metadata(self):
        args_in = [ 'create', '--description', 'Description of resource',
                '--author', u'Dietmar Müller', 
                '--author-email', 'fred@here',
                'test-repository', 'my_resource',
                self.filepath ]
        args = self.parser.parse_args(args_in)
        self.assertTrue(args)
        self.assertEquals(args.description, 'Description of resource')
        self.assertEquals(args.author, u'Dietmar Müller')
        self.assertEquals(args.author_email, 'fred@here')


    def test_create_all_metadata(self):
        args_in = [ 'create',
                '--description', 'Description of resource',
                '--author', 'fred', 
                '--author-email', 'fred@here',
                '--version', '1.0',
                '--maintainer', 'Joe',
                '--maintainer-email', 'joe@here',
                'test-repository', 'my_resource',
                self.filepath 
                ]
        args = self.parser.parse_args(args_in)
        self.assertEquals(args.version, '1.0')
        self.assertEquals(args.maintainer_email, 'joe@here')


    def test_create_parsed_resource(self):
        args_in = [ 'create',
                '--description', 'Description of resource',
                '--author', 'fred', 
                '--author-email', 'fred@here', 
                '--data-type', 'feature collection',
                '--version', '1.0',
                '--maintainer', 'Joe',
                '--maintainer-email', 'joe@here',
                'test-repository', 'my_resource',
                self.filepath
                ]
        expected_metadata = dict(
                description='Description of resource',
                author='fred',
                author_email='fred@here',
                data_type='feature collection',
                version='1.0',
                maintainer='Joe',
                maintainer_email='joe@here',
                )
        resource_args = self.parser.parse_args(args_in)
        resource = ds_util.create_new_resource(resource_args)
        self.assertEquals(resource.metadata, expected_metadata)
        self.assertEquals(resource.files[0].path, self.filepath)

        
    @patch('os.path.exists')
    @patch('os.path.isdir')
    def test_create_new_resource_just_files(self,
            mock_os_path_isdir,
            mock_os_path_exists):
        resource_args = argparse.Namespace()
        setattr(resource_args, 'bundle', False)
        setattr(resource_args, 'metadata_file', {})
        setattr(resource_args, 'publish', False)
        setattr(resource_args, 'filenames', ['file1','file2'])
        setattr(resource_args, 'resource_name', 'dummy-resource')

        mock_os_path_exists.return_value = True
        mock_os_path_isdir.return_value = False
        with patch('bdkd.datastore.Resource.new') as mock_Resource_new:
            resource = ds_util.create_new_resource(resource_args)
        mock_Resource_new.assert_called_once_with('dummy-resource', 
                files_data=['file1','file2'],
                do_bundle=False,
                metadata={},
                publish=False)


    @patch('os.path.exists')
    @patch('os.path.isdir')
    def test_create_new_resource_files_and_remote(self,
            mock_os_path_isdir,
            mock_os_path_exists):
        resource_args = argparse.Namespace()
        setattr(resource_args, 'bundle', False)
        setattr(resource_args, 'metadata_file', {})
        setattr(resource_args, 'publish', False)
        setattr(resource_args, 'filenames', ['file1','http://test.dummy/file2','file3'])
        setattr(resource_args, 'resource_name', 'dummy-resource')


        mock_os_path_exists.side_effect = lambda f: f[0:4] == 'file'
        mock_os_path_isdir.return_value = False
        with patch('bdkd.datastore.Resource.new') as mock_Resource_new:
            resource = ds_util.create_new_resource(resource_args)
        mock_Resource_new.assert_called_once_with(
            'dummy-resource',
            files_data=['file1','http://test.dummy/file2', 'file3'],
            metadata={},
            do_bundle=False,
            publish=False)


    @patch('bdkd.datastore.Resource.new')
    @patch('os.path.exists')
    @patch('os.path.isdir')
    @patch('os.walk')
    def test_create_new_resource_files_and_dirs(self,
            mock_walk,
            mock_os_path_isdir,
            mock_os_path_exists,
            mock_Resource_new):
        resource_args = argparse.Namespace()
        setattr(resource_args, 'bundle', False)
        setattr(resource_args, 'metadata_file', {})
        setattr(resource_args, 'publish', False)
        setattr(resource_args, 'filenames', ['file1','dir1'])
        setattr(resource_args, 'resource_name', 'dummy-resource')

        mock_os_path_exists.return_value = True
        mock_os_path_isdir.side_effect = lambda f: 'file' not in f
        mock_walk.return_value = [
            ('dir1', ['emptydir','subdir1','subdir2' ], []),
            ('dir1/emptydir', [], []),
            ('dir1/subdir1', [], ['file1']),
            ('dir1/subdir2', [], ['file2'])
            ]
        # Simulates the following file structure:
        # ./file1
        # ./dir1/
        # ./dir1/emptydir/
        # ./dir1/subdir1/
        # ./dir1/subdir1/file1
        # ./dir1/subdir2/
        # ./dir1/subdir2/file2
        # When adding with the parameter 'file1 dir1', it will create a resource
        # containing the file 'file1' and all files inside directory 'dir1'

        resource = ds_util.create_new_resource(resource_args)
        mock_Resource_new.assert_called_once_with(
            'dummy-resource', 
            do_bundle=False,
            files_data=['file1','dir1/subdir1/file1','dir1/subdir2/file2'],
            metadata={},
            publish=False)
