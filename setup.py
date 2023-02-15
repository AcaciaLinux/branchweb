from setuptools import setup

setup(
    name='branchweb',
    version='1.0',
    package_dir={'': 'src'},
    packages=['webserver'],
    py_modules=["branchweb"],
    include_package_data=True,
    install_requires=[],
    author='zimsneexh',
    author_email='z@zsxh.eu',
    description='A simple webserver for python3!'
)

