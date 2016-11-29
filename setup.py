from setuptools import setup

setup(name='hokusai',
      version='0.1',
      description='Artsy Docker development toolkit',
      url='http://github.com/artsy/hokusai',
      author='Isac Petruzzi',
      author_email='isac@artsymail.com',
      license='MIT',
      packages=['hokusai'],
      package_data={'hokusai': 'templates'},
      install_requires=[
          'click==6.6',
          'Jinja2==2.8',
          'PyYAML==3.12'
      ],
      zip_safe=False,
      include_package_data = True,
      scripts = ['bin/hokusai'])
