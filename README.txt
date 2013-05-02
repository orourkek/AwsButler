AwsButler
=========

## Author

Kevin O'Rourke

orourke.kevin@gmail.com

## License

Copyright (C) 2013 Kevin O'Rourke

This software is released under the GNU GPL v3 license.

***see the LICENSE file for more information***

## Introduction

AwsButler is a command line tool for gathering information about, issuing commands on, and overseeing an Amazon AWS account. I have developed this application with the following goals in mind:

	1. Practice/learn Python
	2. Make my work life easier

I've not had much practice in Python-land, so forgive any poor code choices you might come accross, as this has largely been a learning experience so far.
My job necessitates a certain awareness of the happenings within a small cluster of AWS instances. As such, I was keen to develop a command line tool for getting a quick look at our AWS infrastructure, and for being able to quickly connect to instances.

***Note: this is an experimental application. I offer no guarantees and/or promises about functionality, performance, or reliability***

## Requirements

+ Python 2.7.2+
+ Boto (will be installed as a dependency)
+ Cement (will be installed as a dependency)
+ Mac OSX (come features are currently written exclusively for OSX)

## Installation

First, grab a copy off the code:

	git clone https://github.com/orourkek/Awsinfo.git

Run the setup script in **develop** mode:

	sudo python setup.py develop

I'm new to Python package development, and there's a rather frustrating bug that I can't fix if it's installed using 'install' in place of 'develop'.

At this point you should have a `awsbutler` file in `/usr/local/bin`, and the example configuration file will be copied to `$HOME/awsbutler.cfg`. You will need to edit this file to provide the following information for one or more accounts:

+ **alias** - an alias/shorthand for the account, used when running commands on it
+ **default [optional]** - assign this a value of '1' for the account to be loaded as the default, when no account is specified
+ **ssh_key** - the absolute path to the .pem ssh key file for connecting to instances
+ **aws_keys**
  - **key** - a public key string provided by amazon for your AWS account
  - **secret** - a secret key string provided by amazon for your AWS account

Once your config file is complete, you can begin querying AWS for information about your account.

To run the application, you can either call `awsbutler` from `/usr/local/bin` directly:

	awsbutler <command>

...or alias it however you want (personally I have an alias for each AWS account in my cfg file


## Usage

A few basic comands are currently supported:

	awsbutler instances [-v]
	awsbutler connect
	awsbutler elb
	awsbutler file
	awsbutler file tail
	awsbutler file download

To see a full list of available commands, along with help text and available flags/options, run:

	awsbutler --help


The most useful command so far is `instances`, which will output a table with information about your instances, like this:

	+--------+------------+-------------+----------+------------------------------------------+--------------+-------------+
	| UID	 | IID		  | Name		| Type	   | Public DNS								  | Ami			 | State	   |
	+--------+------------+-------------+----------+------------------------------------------+--------------+-------------+
	| 0		 | i-abcdefgh |				| m1.small | ec2-00-00-00-00.compute-1.amazonaws.com  | ami-12345678 | running(16) |
	+--------+------------+-------------+----------+------------------------------------------+--------------+-------------+


*more to come in the readme as the project develops*
