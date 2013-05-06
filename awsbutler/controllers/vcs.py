from cement.core import controller
from awsbutler.core.controller import InstanceInteractionController
from awsbutler.helpers.terminal import Color
import os

class SvnController(InstanceInteractionController):
	class Meta:
		label = 'vcs'
		interface = controller.IController
		stacked_on = None
		arguments = [
			(['-i', '--instance'], dict(action='store', help='which instance to interact with from', dest='instance'))
		]

	@controller.expose(help="update an svn repository")
	def update(self):
		command = 'svn update %s' % self._get_svn_directory()

		target_instance = self._instance_prompt()

		print "running command '%s' on instance '%s'..." % (command, target_instance.id)
		ssh_command = 'ssh -t -i %s %s@%s "%s"' % (self.app.AWS_ACCOUNT.ssh_pem(), self.app.AWS_ACCOUNT.ssh_user(), target_instance.public_dns_name, command)
		print Color.green('output:', bold=True)
		return os.system(ssh_command)


	@controller.expose(help="fetch the status of an svn repository")
	def status(self):
		command = 'svn status %s' % self._get_svn_directory()

		target_instance = self._instance_prompt()

		print "running command '%s' on instance '%s'..." % (command, target_instance.id)
		ssh_command = 'ssh -t -i %s %s@%s "%s"' % (self.app.AWS_ACCOUNT.ssh_pem(), self.app.AWS_ACCOUNT.ssh_user(), target_instance.public_dns_name, command)
		print Color.green('output:', bold=True)
		return os.system(ssh_command)




	def _get_svn_directory(self):
		svn_dir = self.app.AWS_ACCOUNT.svn_dir()
		if not svn_dir:
			print Color.red('you must have the "svn_directoy" option set in awsbutler.cfg to use this command', bold=True)
			exit()
		return svn_dir