from cement.core import controller, exc
from boto.ec2.connection import EC2Connection
import boto.ec2.cloudwatch
import boto
from termcolor import cprint, colored
from terminal import Table
import collections
import os
import datetime
import json
import ConfigParser
import subprocess


class AwsController(controller.CementBaseController):

	_acct_info = {}
	_config_loaded = False
	_instances_cache = None 	#not fully implemented yet

	class Meta:
		label = 'aws'
		interface = controller.IController
		stacked_on = 'base'
		description = "Various AWS operations/commands"
		arguments = [
			(['-a', '--account'], dict(action='store', help='which account to run commands on (see config.json)', dest='account')),
			(['-v', '--verbose'], dict(action='store_true', help='more verbose data output (not applicable to all commands)', dest='verbose')),
		]

	def _parse_args(self):
		super(AwsController, self)._parse_args()
		self._load_config()

	def _load_config(self):
		if self._config_loaded:
			return
		self._config_loaded = True
		config_file = self.app.config.get('awsinfo', 'config_file')
		default_acct = None
		try:
			config_json = open(config_file)
			config_data = json.load(config_json)
			acct = self.app.pargs.account
			for account in config_data['accounts']:
				if (('default' in account) and (account['default']) and (acct is None)) or (acct == account['alias']):
					#verify the rest of the data is there
					account['ssh_key']
					account['aws_keys']['secret']
					account['aws_keys']['key']
					self._acct_info = account
					return
		except IOError as e:
			exit("failed to load config file: %s" % e)
		except KeyError as e:
			exit('invalid config file format. missing key %s' % e)
		except IndexError as e:
			exit('no accounts could be found in config file')
		except Exception as e:
			exit('unexpected error: %s' % e)

		exit("error: failed to find account information for alias '%s'" % acct)

	@controller.expose(help="default command for aws", hide=True)
	def default(self):
		print 'Use the help flag [-h|--help] to view available commands and flags\n'


	@controller.expose(help="shows active AWS instances and other useful status information")
	def instances(self):
		if self.app.pargs.verbose:
			self.instances_verbose()
			exit()
		instances = self._fetch_instances()
		table = Table(("UID", "IID", "Name", "Type", "Public DNS", "Ami", "State"))
		for c, i in instances.items():
			table.add_row((c, i.id, i.tags.get("Name", ""), i.instance_type, i.dns_name, i.image_id, i._state))
		print table
		return

	def instances_verbose(self):
		cprint('This could take a few moments, be patient...', 'yellow', attrs=['bold'])
		instances = self._fetch_instances()
		elbs = self._fetch_load_balancers()
		print 'fetching cloudwatch metrics...'
		creds = self._acct_info['aws_keys']
		cloudwatch_conn = boto.connect_cloudwatch(aws_access_key_id=creds["key"], aws_secret_access_key=creds["secret"])
		metric_end = datetime.datetime.now()
		metric_start = metric_end - datetime.timedelta(hours=1)

		table = Table(("UID", "IID", "Name", "Type", "ELB", "AZ", "Public DNS", "Ami", "State", "CPU"))
		for c, i in instances.items():
			load_balancer = ''
			for lb in elbs:
				if i.id in [inst.id for inst in lb.instances]:
					load_balancer = lb.name
			query_results = cloudwatch_conn.list_metrics(metric_name='CPUUtilization',dimensions={'InstanceId':i.id})
			try:
				metric = query_results[0]
				result = metric.query(metric_start, metric_end, ['Minimum','Average','Maximum'], 'Percent', 3600)
				cpu_utilization = '%d~%d~%d' % (round(result[0]['Minimum']),round(result[0]['Average']),round(result[0]['Maximum']))
			except Exception as e:
				cpu_utilization = '-error-'
			#cpu_utilization =
			#print cpu_utilization = .query(metric_start, metric_end, 'Average', 'Percent')
			table.add_row((c, i.id, i.tags.get("Name", ""), i.instance_type, load_balancer, i.placement, i.dns_name, i.image_id, i._state, cpu_utilization))
		print table
		return


	@controller.expose(help="connect to an AWS instance")
	def connect(self):
		self.instances()
		cprint('\nWhich instance do you want to connect to? (Enter a UID from above)', 'yellow', attrs=['bold'])

		valid_input = False
		while not valid_input:
			try:
				inp = raw_input(" > ")
				if inp in ('^C', 'exit', 'exit()', 'q', 'quit'):
					return
				target_instance = self._instances_cache[int(inp)]
				valid_input = True
			except Exception as e:
				if isinstance(e, exc.CaughtSignal):
					print '\n'
					exit()
				cprint('invalid input. please enter a UID from the above table', 'red')
		self._run_ssh_connect(target_instance.public_dns_name)
		return

	@controller.expose(help="information about load balancer(s)")
	def elb(self):
		elbs = self._fetch_load_balancers()
		c = 0
		for lb in elbs:
			c += 1
			print '\n',
			print '%15s %-100.100s' % ('', 'ELB #%d' % c)
			print '%15s %-100.100s' % ('', '~~~~~')
			print '%15s %-100.100s' % ('Name: ', lb.name)
			print '%15s %-100.100s' % ('Created: ', lb.created_time)
			print '%15s %-100.100s' % ('DNS: ', lb.dns_name)
			print '%15s %-100.100s' % ('AZs: ', ', '.join(lb.availability_zones))
			first = True
			for inst in lb.instances:
				state = 'running'
				label = ''
				if inst.state is not None:
					state = inst.state
				if first is True:
					first = False
					label = 'Instances: '
				print '%15s %-100.100s' % (label, '%s (%s)' % (inst.id, state))
			print ''
		return

	def _run_ssh_connect(self, dns, new_window=False):
		self._load_config()
		ssh_key = self._acct_info['ssh_key']
		if new_window:
			ssh_command = 'ssh -i %s root@%s' % (ssh_key, dns)
			if os.path.exists('/Applications/iTerm.app'):
				terminal_osa_script = """tell application "iTerm"
							make new terminal
							tell the current terminal
								activate current session
								launch session "Default Session"
								tell the last session
									write text "%s"
								end tell
							end tell
						end tell"""  % ssh_command
			else:
				terminal_osa_script = 'tell application "Terminal" to do script "%s"' % ssh_command;
			return os.system("osascript -e '%s'" % terminal_osa_script)
		else:
			ssh_command = ['ssh', '-t', '-i', ssh_key, 'root@%s' % dns]
			#return subprocess.Popen(ssh_command)
			return os.system(' '.join(ssh_command))

	def _fetch_load_balancers(self):
		self._load_config()
		creds = self._acct_info['aws_keys']
		print 'fetching load balancer data...'
		conn = boto.connect_elb(aws_access_key_id=creds["key"], aws_secret_access_key=creds["secret"])
		return conn.get_all_load_balancers()


	def _fetch_instances(self):
		self._load_config()
		print 'fetching instance data...'
		creds = self._acct_info['aws_keys']
		conn = EC2Connection(aws_access_key_id=creds["key"], aws_secret_access_key=creds["secret"])
		instance_list = [i for r in conn.get_all_instances() for i in r.instances]
		instances = collections.OrderedDict()

		c = 0
		for i in instance_list:
			instances[c] = i
			c += 1
		self._instances_cache = instances
		return instances

