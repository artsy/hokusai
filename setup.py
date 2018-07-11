import os
from setuptools import setup
from hokusai.version import VERSION

setup(name='hokusai',
      version=VERSION,
      description='Artsy Docker development toolkit',
      url='http://github.com/artsy/hokusai',
      author='Isac Petruzzi',
      author_email='isac@artsymail.com',
      license='MIT',
      packages=['hokusai'],
      package_data={'hokusai': ['cli/*', 'commands/*', 'lib/*', 'services/*', 'templates/*']},
      install_requires=[
          'click==6.7',
          'click-repl==0.1.3',
          'prompt-toolkit==1.0.15',
          'MarkupSafe==1.0',
          'Jinja2==2.9.6',
          'PyYAML==3.12',
          'termcolor==1.1.0',
          'boto3==1.4.4',
          'botocore==1.5.41'
      ],
      zip_safe=False,
      include_package_data = True,
      scripts = ['bin/hokusai'])
