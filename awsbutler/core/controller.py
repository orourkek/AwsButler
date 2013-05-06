from cement.core import controller
from awsbutler.helpers.terminal import Color
from awsbutler.core import aws

class BaseController(controller.CementBaseController):

	class Meta:
		label = 'base'
		interface = controller.IController
		stacked_on = None
		description = 'AwsInfo is a tool for aiding in AWS instance management'
		arguments = []

	@controller.expose(hide=True)
	def default(self):
		print 'use the help flag [-h|--help] to view available commands and options'


class InstanceInteractionController(BaseController):

	def _instance_prompt(self):
		instance = self.app.pargs.instance
		client = aws.Client(self.app.AWS_ACCOUNT)
		instances = client.instances()

		if instance is not None and int(instance) in instances:
			return instances[int(instance)]

		print instances
		print Color.yellow('\nWhich instance do you want to interact with? (Enter a UID from above)', bold=True)

		while True:
			try:
				inp = raw_input(" > ")
				if inp in ('^C', 'exit', 'exit()', 'q', 'quit'):
					print '\n'
					exit()
			except Exception as e:
				if isinstance(e, exc.CaughtSignal):
					print '\n'
					exit()
			try:
				return instances[int(inp)]
			except KeyError:
				print Color.red('invalid input. please enter a UID from the above table')