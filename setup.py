from setuptools import find_packages, setup

setup(name='pjtools',
      version='0.0.2',
      author='Xinyu Wang',
      author_email='wangxinyu2017@gmail.com',
      packages=find_packages(),
      install_requires=[
          'numpy',
          'pyyaml',
      ])
