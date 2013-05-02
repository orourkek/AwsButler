from cement.core import controller


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
