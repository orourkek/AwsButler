#! /usr/bin/python

from cement.core import foundation, handler, backend
from aws import AwsController
import os

defaults = backend.defaults('myapp', 'awsinfo')
defaults['awsinfo']['config_file'] = '%s/config.json' % os.path.dirname(os.path.abspath(__file__))

app = foundation.CementApp('awsinfo', base_controller=AwsController, config_defaults=defaults, arguments_override_config=True)

try:
	app.setup()

	app.args.add_argument('-c', '--config', action='store', dest='config_file', help='config file (JSON) location')

	app.run()


finally:
	app.close()