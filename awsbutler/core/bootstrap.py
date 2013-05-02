from cement.core import handler
from awsbutler.controllers.ec2 import EC2Controller
from awsbutler.controllers.file import FileController

def load():
	handler.register(EC2Controller)
	handler.register(FileController)
	return