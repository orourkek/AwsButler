from cement.core import handler
from awsbutler.controllers.aws import AwsController
from awsbutler.controllers.file import FileController

def load():
	handler.register(AwsController)
	handler.register(FileController)
	return