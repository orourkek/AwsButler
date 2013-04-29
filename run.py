#! /usr/bin/python

from cement.core import foundation, handler, backend, controller
from aws import AwsController
from app import AwsInfoApp, BaseController
from termcolor import cprint
import os



class AwsInfoApp(foundation.CementApp):

	VERSION = '0.1.1'

	@staticmethod
	def check_for_updates():
		from urllib2 import urlopen
		import re
		from terminal import Table

		try:
			origin_version = 'unknown'
			cregex = re.compile("VERSION = '([0-9]\.[0-9]\.[0-9])'")
			url = 'https://raw.github.com/orourkek/Awsinfo/master/run.py'

			for line in urlopen(url):
				result = cregex.search(line.strip())
				if result is not None:
					origin_version = result.group(1)

			print '\n  local version:  %s' % AwsInfoApp.VERSION
			print '  origin version: %s\n' % origin_version

			if origin_version is 'unknown':
				cprint("couldn't determine origin version from '%s'" % url, 'red', attrs=['bold'])
			elif (AwsInfoApp.VERSION < origin_version):
				cprint('your application appears to be out-of-date!', 'yellow', attrs=['bold'])
				cprint('update to the latest version with `git pull origin`', 'yellow', attrs=['bold'])
			else:
				cprint('your application is up to date!', 'green', attrs=['bold'])
		except Exception as e:
			#print 'ERROR: %s' % e
			raise e

class BaseController(controller.CementBaseController):

	class Meta:
		label = 'base'
		interface = controller.IController
		stacked_on = 'None'
		description = 'AwsInfo is a tool for aiding in AWS instance management'
		arguments = []

	@controller.expose(help='application (meta) status information', hide=False)
	def appstatus(self):
		AwsInfoApp.check_for_updates()


defaults = backend.defaults('myapp', 'awsinfo')
defaults['awsinfo']['config_file'] = '%s/config.json' % os.path.dirname(os.path.abspath(__file__))

app = AwsInfoApp('awsinfo', base_controller=BaseController, config_defaults=defaults, arguments_override_config=True)

handler.register(AwsController)

try:
	app.setup()

	app.args.add_argument('-c', '--config', action='store', dest='config_file', help='config file (JSON) location')

	app.run()


finally:
	app.close()
