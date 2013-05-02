from cement.core import controller
from awsbutler.core.controller import BaseController
from awsbutler.core import aws
from awsbutler.helpers.terminal import Table



class InstanceController(BaseController):
	class Meta:
		label = 'instance'
		interface = controller.IController
		stacked_on = None
		arguments = [
			(['-v', '--verbose'], dict(action='store_true', help='more verbose data output (not applicable to all commands)', dest='verbose')),
		]

"""
	@controller.expose(help="shows detailed information about an AWS instance")
	def detail(self):
		client = aws.Client(self.app.AWS_ACCOUNT)
		if self.app.pargs.verbose:
			instances = client.instances(verbose=True)
			table = Table(("UID", "IID", "Name", "Type", "ELB", "AZ", "Public DNS", "Ami", "State", "CPU"))
			for c, i in instances.items():
				table.add_row((c, i.id, i.tags.get("Name", ""), i.instance_type, i.load_balancer, i.placement, i.dns_name, i.image_id, i._state, i.cpu_utilization))
		else:
			instances = client.instances()
			table = Table(("UID", "IID", "Name", "Type", "Public DNS", "Ami", "State"))
			for c, i in instances.items():
				table.add_row((c, i.id, i.tags.get("Name", ""), i.instance_type, i.dns_name, i.image_id, i._state))
		print table
		return
"""