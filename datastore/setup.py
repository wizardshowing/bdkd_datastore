#!/usr/bin/env python

from setuptools import setup
import glob
≡jedi=0, ≡     (**attrs) ≡jedi≡
setup(
        name='bdkd-datastore',
        version='0.0.1',
        description='Store and retrieve sets of files from an object store',
        author='Sirca Ltd',
        author_email='david.nelson@sirca.org.au',
        url='http://github.com/sirca/bdkd',
        package_dir={'': 'lib'},
        packages=['bdkd'],
        scripts=[
                'bin/datastore-add',
                'bin/datastore-delete',
                'bin/datastore-files',
                'bin/datastore-get',
                'bin/datastore-list',
                'bin/datastore-repositories',
                ],
        entry_points = {
            'console_scripts': [
                'datastore-add-bdkd = bdkd.datastore_util.add:add_bdkd_util',
                'datastore-getkey = bdkd.datastore_util.info:getkey_util',
                'datastore-lastmod = bdkd.datastore_util.info:lastmod_util',
            ],
        },
        install_requires=['boto', 'PyYAML']
        )
