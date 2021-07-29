import os
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='hokusai',
      version=open(os.path.join(os.path.dirname(__file__), "hokusai", "VERSION")).read().strip(),
      description='Artsy Docker development toolkit',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/artsy/hokusai',
      author='Isac Petruzzi',
      author_email='isac@artsymail.com',
      license='MIT',
      packages=['hokusai'],
      package_data={
                      'hokusai': [
                                    'cli/*',
                                    'commands/*',
                                    'lib/*',
                                    'services/*',
                                    'templates/*',
                                    'templates/hokusai/*',
                                    'VERSION'
                                  ]
      },
      install_requires=[
          'click~=6.7',
          'click-repl~=0.1',
          'prompt-toolkit~=1.0.16',
          'MarkupSafe~=1.0',
          'Jinja2~=2.10',
          'packaging',
          'PyYAML~=3.12',
          'termcolor~=1.1',
          'boto3~=1.4',
          'botocore~=1.12'
      ],
      zip_safe=False,
      include_package_data = True,
      scripts = ['bin/hokusai'])
