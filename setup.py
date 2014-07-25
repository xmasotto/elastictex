#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(name="elastictex",
      version="0.1",
      description="Search with Latex",
      author="Xander Masotto",
      author_email="xmasotto@gmail.com",
      packages=["elastictex",
                "mongo_connector",
                "mongo_connector.doc_managers"],
      package_data={
          'elastictex': ['templates/*']
      },
      install_requires=["elasticsearch", "flask"],
      entry_points={
          'console_scripts': [
              'elastictex = elastictex.server:main'
          ]
      })
