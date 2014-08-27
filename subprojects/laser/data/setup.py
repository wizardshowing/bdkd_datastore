#!/usr/bin/env python

from setuptools import setup

setup(                         
        name='bdkd-laser-data',
        version='0.0.1',
        description='Access dataset data',
        author='Sirca Ltd',
        author_email='david.nelson@sirca.org.au',
        url='http://github.com/sirca/bdkd',
        package_dir={'': 'lib'},        
        packages=['bdkd.laser'],
        scripts=[
                'bin/pack_dataset.py',            
                ],
        entry_points = {
            'console_scripts': [
                'datastore-add-laser = bdkd.laser.util.add:add_laser_util',
                ],
            },
        install_requires=['boto', 'PyYAML', 'bdkd-datastore', 'h5py']
        )
