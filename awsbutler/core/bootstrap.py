from cement.core import handler
from awsbutler.controllers.aws import AwsController
from awsbutler.controllers.fileops import FileOpsController
from awsbutler.controllers.vcs import SvnController

def load():
	handler.register(AwsController)
	handler.register(FileOpsController)
	handler.register(SvnController)
	return