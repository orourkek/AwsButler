from setuptools import setup, find_packages
from shutil import copyfile
from os.path import expanduser, isfile

home_dir = expanduser("~")

if not isfile('%s/awsbutler.cfg' % home_dir):
	if isfile('awsbutler.cfg'):
		copyfile('awsbutler.cfg', '%s/awsbutler.cfg' % home_dir)
	else:
		copyfile('awsbutler.cfg.example', '%s/awsbutler.cfg' % home_dir)

setup(
    name='AwsButler',
    version='0.1.1',
    author="Kevin O'Rourke",
    author_email='kevin@korourke.net',
    packages=find_packages(),
    scripts=['bin/awsbutler'],
    license='LICENSE',
    description='Command line tools for AWS cloud management & status information',
    long_description=open('README.md').read(),
    install_requires=[
        "cement == 2.0.2",
        "boto == 2.9.2",
    ],
    #data_files = [(home_dir, ['awsbutler.cfg'])],
)
