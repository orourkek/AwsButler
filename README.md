Awsinfo
=======

## Author

Kevin O'Rourke
orourke.kevin@gmail.com

## License

Copyright (C) 2013 Kevin O'Rourke

This software is released under the GNU GPL v3 license.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

## Introduction

Awsinfo is a command line tool for gathering basic information about an Amazon AWS account. I have developed this application with the following goals in mind:

1. Practice Python
2. Make my work life easier

I've not had much practice in Python-land, so forgive any poor code choices you might come accross, as this has largely been a learning experience so far.
My job necessitates a certain awareness of the happenings within a small cluster of AWS instances. As such, I was keen to develop a command line tool for getting a quick look at our AWS infrastructure, and for being able to quickly connect to instances.

***Note: this is very much a work in progress.***

## Requirements

+ Python 2.7.2+
+ Mac OSX (come features are currently written exclusively for OSX)

## Installation

First, grab a copy off the code:

	git clone https://github.com/orourkek/Awsinfo.git

Now you'll want to copy `config.json.example` into `config.json`, and modify it with the following information (as per the layout in the example file):

+ **alias** - an alias/shorthand for the account, used when running commands on it
+ **default [optional]** - assign this a value of '1' for the account to be loaded as the default, when no account is specified
+ **ssh_key** - the absolute path to the .pem ssh key file for connecting to instances
+ **aws_keys**
  - **key** - a public key string provided by amazon for your AWS account
  - **secret** - a secret key string provided by amazon for your AWS account

Once your config file is complete, you can begin querying AWS for information about your account.

To run the application, you can either call `run.py` with python

	python run.py <command>

...or, assuming `run.py` has the executable mode (`chmod +x run.py`):

	./run.py <command>

## Usage

A few basic comands are currently supported:

	./run.py instances [-v]
	./run.py connect
	./run.py elb

To see a full list of available commands, along with help text and available flags/options, run:

	./run.py --help


The most useful command is `instances`, which will output a table with information about your instances, like this:

	+--------+------------+-------------+----------+------------------------------------------+--------------+-------------+
	| UID	 | IID		  | Name		| Type	   | Public DNS								  | Ami			 | State	   |
	+--------+------------+-------------+----------+------------------------------------------+--------------+-------------+
	| 0		 | i-abcdefgh |				| m1.small | ec2-00-00-00-00.compute-1.amazonaws.com  | ami-12345678 | running(16) |
	+--------+------------+-------------+----------+------------------------------------------+--------------+-------------+

