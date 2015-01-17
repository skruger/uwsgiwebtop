
from setuptools import setup
from pip.req import parse_requirements



install_reqs = parse_requirements("REQUIREMENTS.txt")

entry_points = {'console_scripts': ['uwsgi-webtop=uwsgiwebtop.cli:main']}

setup(name='uwsgiwebtop',
      version='0',
      url='https://github.com/skruger/uwsgiwebtop',
      description='Web application to aggregate stats from multiple uWSGI instances',
      author="Shaun Kruger",
      author_email="shaun.kruger@gmail.com",
      include_package_data=True,
      packages=['uwsgiwebtop'],
      entry_points = entry_points,
      install_requires=[str(ir.req) for ir in install_reqs],
      )
