from cement.core import controller
from awsbutler.core.controller import BaseController
from awsbutler.core import aws
from awsbutler.helpers.terminal import Table, Color
from collections import Iterable



class EC2Controller(BaseController):
	class Meta:
		label = 'status'
		interface = controller.IController
		stacked_on = 'base'
		arguments = [
			(['-v', '--verbose'], dict(action='store_true', help='more verbose data output (not applicable to all commands)', dest='verbose')),
			#(['-xv', '--extra-verbose'], dict(action='store_true', help='boatloads of information (not applicable to all commands)', dest='extra_verbose')),
		]

	@controller.expose(help="shows active AWS instances and other useful status information")
	def instances(self):
		client = aws.Client(self.app.AWS_ACCOUNT)
		if self.app.pargs.verbose:
			instances = client.instances(verbose=True)
			print instances
		else:
			instances = client.instances()
			print instances
			"""
			if self.app.pargs.extra_verbose:
				for c, i in instances.items():
					print 'Instance %s:' % (c,),
					table = Table(('Field', 'Value'))
					for item in i.__dict__:
						value = getattr(i, item)
						if(not isinstance(value, str) and not isinstance(value, unicode) and isinstance(value, Iterable)):
							value = ', '.join(map(str, value))
						table.add_row((item, str(value).strip()))
					print table
					table = None
			"""
		return

	@controller.expose(help="information about load balancer(s)")
	def elb(self):
		client = aws.Client(self.app.AWS_ACCOUNT)
		elbs = client.elbs()
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

	@controller.expose(help="connect to an AWS instance")
	def connect(self):
		client = aws.Client(self.app.AWS_ACCOUNT)
		instances = client.instances()
		print instances
		print Color.yellow('\nWhich instance do you want to connect to? (Enter a UID from above)', bold=True)

		valid_input = False
		while not valid_input:
			try:
				inp = raw_input(" > ")
				if inp in ('^C', 'exit', 'exit()', 'q', 'quit'):
					return
			except Exception as e:
				if isinstance(e, exc.CaughtSignal):
					print '\n'
					exit()
			try:
				client.ssh_connect(int(inp), new_window=False)
				valid_input = True
			except KeyError:
				print Color.red('invalid input. please enter a UID from the above table')

		return


