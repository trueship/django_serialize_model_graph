from setuptools import setup

from django_serialize_model_graph import __version__


setup(name='django_serialize_model_graph',
      version=__version__,
      description='Django Serialize Model Graph -- utility for serializing graph of models for django.',
      author='Konstantine Rybnikov',
      author_email='k-bx@k-bx.com',
      url='https://bitbucket.org/k_bx/django_serialize_model_graph/',
      license='BSD',
      packages=['django_serialize_model_graph'],
      test_suite='nose.collector')
