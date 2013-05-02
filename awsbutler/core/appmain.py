from cement.core import foundation
from awsbutler.core.controller import BaseController
from awsbutler.core import aws
import json
from os.path import dirname, abspath, expanduser
from awsbutler.helpers.terminal import Color


class AwsButler(foundation.CementApp):

	class Meta:
		label = 'awsbutler'
		bootstrap = 'awsbutler.core.bootstrap'
		arguments_override_config = True
		base_controller = BaseController

	def setup(self):
		super(AwsButler, self).setup()
		self.args.add_argument('-a', '--account', action='store', dest='account', help='which account (alias) to run commands on')
		self.args.add_argument('-c', '--config', action='store', dest='config', help='configuration file location')

	def validate_config(self):
		self._process_app_config()

	def __getattr__(self, name):
		if 'AWS_ACCOUNT' == name:
			accounts = self.config.get('awsbutler', 'accounts')
			alias = self.pargs.account

			if (alias is None):
				for acct in accounts:
					try:
						acct['default']
						self.AWS_ACCOUNT = aws.Account(acct)
						return self.AWS_ACCOUNT
					except KeyError:
						pass
				raise KeyError('no account specified, and no default set (see config.json.example)')
			else:
				for acct in accounts:
					if (alias == acct['alias']):
						self.AWS_ACCOUNT = aws.Account(acct)
						return self.AWS_ACCOUNT
				raise KeyError('unknown account specified: "%s"' % alias)
		raise AttributeError

	def _process_app_config(self):
		home_dir = expanduser("~")
		config_file = '%s/awsbutler.cfg' % home_dir
		try:
			config_json = open(config_file)
			config_data = json.load(config_json)
			self._validate_config_data(config_data)
		except IOError as e:
			exit("failed to load configuration file: %s" % e)
		except Exception as e:
			exit('unexpected error loading configuration file: %s' % e)

		self.config.set('awsbutler', 'accounts', config_data['accounts'])

	def _validate_config_data(self, data):
		try:
			data['accounts']
			for acct in data['accounts']:
				acct['alias']
				acct['ssh_key']
				acct['aws_keys']
				acct['aws_keys']['key']
				acct['aws_keys']['secret']
		except KeyError as e:
			print Color.red('invalid configuration, missing key "%s"' % str(e), bold=True)
			exit()
