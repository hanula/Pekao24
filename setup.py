from setuptools import setup, find_packages
import sys, os

version = '0.0'

requires = [
    "BeautifulSoup",
    "mechanize",
]



setup(name='pekao24',
      version=version,
      description="Pekao Bank's API",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='bank api pekao',
      author='Sebastian Hanula',
      author_email='sebastian.hanula@gmail.com',
      url='',
      license='',
      scripts=['scripts/pekao24'],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""
      # -*- Entry points: -*-
      """,
)
