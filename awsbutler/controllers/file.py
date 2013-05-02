from cement.core import controller
from awsbutler.core import aws
from awsbutler.core.controller import BaseController
from awsbutler.helpers.terminal import Color
import os
from os.path import expanduser, isdir, basename


class FileController(BaseController):
	class Meta:
		label = 'file'
		interface = controller.IController
		stacked_on = None
		description = "Remote file operations"
		arguments = [
			(['-f', '--file'], dict(action='store', help='which file to interact with', dest='filename', default='/var/log/httpd/php_error.log')),
			(['-l', '--lines'], dict(action='store', help='how many log lines to process', dest='lines', default=100)),
			(['-i', '--instance'], dict(action='store', help='which instance to fetch log data from', dest='instance')),
			(['-tf', '--target-file'], dict(action='store', help='when downloading to local machine, where to save the file', dest='local_target')),
			#(['-p', '--path'], dict(action='store', help='the directory to look in for the file', dest='path', default='/var/log/httpd')),
		]


	@controller.expose(help="view `tail` output from a remote file")
	def tail(self):
		instance = self.app.pargs.instance
		filename = self.app.pargs.filename
		lines = self.app.pargs.lines
		#path = self.app.pargs.path

		file_path = filename #'%s/%s' % (path, filename)

		client = aws.Client(self.app.AWS_ACCOUNT)
		instances = client.instances()

		if instance is not None and int(instance) in instances:
			target_instance = instances[int(instance)]
		else:
			target_instance = self._instance_prompt(instances)

		dns = target_instance.public_dns_name
		print "fetching the last %s lines of '%s' from %s..." % (lines, file_path, dns)
		ssh_command = 'ssh -t -i %s %s@%s "tail -n %s %s"' % (self.app.AWS_ACCOUNT.ssh_pem(), self.app.AWS_ACCOUNT.ssh_user(), dns, lines, file_path)
		print Color.green('output:', bold=True)
		return os.system(ssh_command)

	@controller.expose(help="download a remote file with gzip compression")
	def download(self):
		instance = self.app.pargs.instance
		file_path = self.app.pargs.filename
		local_target = self.app.pargs.local_target

		if local_target is None:
			home_dir = expanduser("~")
			local_target = '%s/Downloads' % home_dir
			if not isdir(local_target):
				local_target = '/tmp'
			local_target = '%s/%s' % (local_target, basename(file_path))


		client = aws.Client(self.app.AWS_ACCOUNT)
		instances = client.instances()

		if instance is not None and int(instance) in instances:
			target_instance = instances[int(instance)]
		else:
			target_instance = self._instance_prompt(instances)

		dns = target_instance.public_dns_name
		print "downloading file '%s' from %s to %s..." % (file_path, dns, local_target)
		download_command = """ssh -t -i %s %s@%s "cat %s | gzip -f -c1 " | gunzip -c""" % (self.app.AWS_ACCOUNT.ssh_pem(), self.app.AWS_ACCOUNT.ssh_user(), dns, file_path)
		#scp_command = """scp -i %s %s@%s:%s %s """ % (self.app.AWS_ACCOUNT.ssh_pem(), self.app.AWS_ACCOUNT.ssh_user(), dns, file_path, local_file)
		#print Color.green('output:', bold=True)
		return os.system('%s > %s' % (download_command, local_target))


	def _instance_prompt(self, instances):
		print instances
		print Color.yellow('\nWhich instance do you want to interact with? (Enter a UID from above)', bold=True)

		while true:
			try:
				inp = raw_input(" > ")
				if inp in ('^C', 'exit', 'exit()', 'q', 'quit'):
					return
			except Exception as e:
				if isinstance(e, exc.CaughtSignal):
					print '\n'
					exit()
			try:
				return instances[int(inp)]
			except KeyError:
				print Color.red('invalid input. please enter a UID from the above table')


