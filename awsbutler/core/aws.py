from awsbutler.helpers.terminal import Color, Table
from collections import OrderedDict
from boto.ec2.connection import EC2Connection
from boto.ec2.instance import Instance
from boto import connect_cloudwatch, connect_elb
import os
import datetime


class Account:

	DATA = {}

	def __init__(self, config_data):
		try:
			config_data['ssh_key']
			config_data['ssh_user']
			config_data['aws_keys']['secret']
			config_data['aws_keys']['key']
		except KeyError as e:
			print Color.red('incomplete account configuration. missing key %s' % e, bold=True)
			exit()
		self.DATA = config_data
		if not self.DATA['ssh_port']:
			self.DATA['ssh_port'] = "22"

	def key(self):
		return self.DATA['aws_keys']['key']

	def secret_key(self):
		return self.DATA['aws_keys']['secret']

	def ssh_pem(self):
		return self.DATA['ssh_key']

	def ssh_user(self):
		return self.DATA['ssh_user']

	def ssh_port(self):
		return self.DATA['ssh_port']

	def svn_dir(self):
		try:
			return self.DATA['svn_directory']
		except:
			return False



class Client:

	ACCOUNT = None
	INSTANCES = None
	ELBS = None

	def __init__(self, account):
		if not isinstance(account, Account):
			raise TypeError('aws.Client() requires an instance of aws.Account')
		self.ACCOUNT = account
		self.INSTANCES = InstanceCollection()
		self.ELBS = OrderedDict()

	def instances(self, verbose=False):
		if len(self.INSTANCES) > 0:
			#print 'using cached instance data'
			return self.INSTANCES
		if verbose:
			print Color.yellow('warning: verbose data collection will take a bit longer', bold=True)
		print 'fetching instance data...'
		conn = EC2Connection(aws_access_key_id=self.ACCOUNT.key(), aws_secret_access_key=self.ACCOUNT.secret_key())
		instance_list = [i for r in conn.get_all_instances() for i in r.instances]

		if verbose:
			if len(self.ELBS) <= 0:
				self.elbs()
			print 'fetching cloudwatch metrics...'
			cloudwatch_conn = connect_cloudwatch(aws_access_key_id=self.ACCOUNT.key(), aws_secret_access_key=self.ACCOUNT.secret_key())
			metric_end = datetime.datetime.now()
			metric_start = metric_end - datetime.timedelta(hours=1)

		for i in instance_list:
			if verbose:
				load_balancer = ''
				for lb in self.ELBS:
					if i.id in [inst.id for inst in lb.instances]:
						load_balancer = lb.name
				query_results = cloudwatch_conn.list_metrics(metric_name='CPUUtilization',dimensions={'InstanceId':i.id})
				try:
					metric = query_results[0]
					result = metric.query(metric_start, metric_end, ['Minimum','Average','Maximum'], 'Percent', 3600)
					cpu_utilization = '%d~%d~%d' % (round(result[0]['Minimum']),round(result[0]['Average']),round(result[0]['Maximum']))
				except Exception as e:
					cpu_utilization = '-error-'
				i.load_balancer = load_balancer
				i.cpu_utilization = cpu_utilization

			self.INSTANCES.add_instance(i)

		return self.INSTANCES

	def elbs(self):
		if len(self.ELBS) > 0:
			#print 'using cached ELB data'
			return self.ELBS
		print 'fetching load balancer data...'
		conn = connect_elb(aws_access_key_id=self.ACCOUNT.key(), aws_secret_access_key=self.ACCOUNT.secret_key())
		self.ELBS = conn.get_all_load_balancers()
		return self.ELBS

	def ssh_connect(self, instance, new_window=False):
		if instance not in self.INSTANCES:
			raise KeyError
		dns = self.INSTANCES[instance].public_dns_name
		print Color.green('connecting you to %s...' % dns, bold=True)
		if new_window:
			ssh_command = 'ssh -p %s -i %s %s@%s' % (self.ACCOUNT.ssh_port(), self.ACCOUNT.ssh_pem(), self.ACCOUNT.ssh_user(), dns)
			print Color.white(ssh_command)
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
			ssh_command = ['ssh', '-p', self.ACCOUNT.ssh_port(), '-t', '-i', self.ACCOUNT.ssh_pem(), '%s@%s' % (self.ACCOUNT.ssh_user(), dns)]
			print Color.white('ssh -p %s -i %s %s@%s' % (self.ACCOUNT.ssh_port(), self.ACCOUNT.ssh_pem(), self.ACCOUNT.ssh_user(), dns))
			#return subprocess.Popen(ssh_command)
			return os.system(' '.join(ssh_command))



class InstanceCollection():

	INSTANCES = None

	def __init__(self):
		self.INSTANCES = OrderedDict()

	def add_instance(self, ec2instance):
		if not isinstance(ec2instance, Instance):
			return False
		self.INSTANCES[len(self.INSTANCES)] = ec2instance
		return self

	def __str__(self):
		columns = ['UID','IID','Name','Type','Public DNS','AZ','AMI','State']

		#columns.append()
		#("UID", "IID", "Name", "Type", "ELB", "AZ", "Public DNS", "Ami", "State", "CPU")
		rows = []
		for c, i in self.INSTANCES.items():
			row_data = [c, i.id, i.tags.get("Name", ""), i.instance_type, i.dns_name, i.placement, i.image_id, i._state]
			if 'load_balancer' in i.__dict__:
				if 'ELB' not in columns:
					columns.append('ELB')
				row_data.append(i.load_balancer)
			if 'cpu_utilization' in self.INSTANCES[0].__dict__:
				if 'CPU' not in columns:
					columns.append('CPU')
				row_data.append(i.cpu_utilization)
			rows.append(tuple(row_data))

		table = Table(columns)
		for row in rows:
			table.add_row(row)
		return str(table)

	def __len__(self):
		return len(self.INSTANCES)

	def __iter__(self):
		return self.INSTANCES.__iter__()

	def __getitem__(self, index):
		return self.INSTANCES[index]

