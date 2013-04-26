from termcolor import cprint, colored
from collections import OrderedDict
import decimal
import sys


class ProgressBar:

	total = 0
	bar_length = 50
	completed_msg = 'done.'

	def __init__(self, total, bar_length=50, start_msg='', completed_msg='done.'):
		self.total = total
		self.bar_length = bar_length
		self.completed_msg = completed_msg
		print start_msg

	def _compute_current_position(self, current):
		current = decimal.Decimal(current)
		total = decimal.Decimal(self.total)
		return int(decimal.Decimal(current/total) * self.bar_length)

	def step(self, current):
		current = decimal.Decimal(current)
		total = decimal.Decimal(self.total)
		progress = decimal.Decimal(current/total)
		current_position = int(progress * self.bar_length)
		#print '%d %d %d' % (progress, (self.bar_length - progress), (progress/self.bar_length))
		sys.stdout.write('\r[ {0}{1} ] {2}%'.format('#'*current_position, ' '*(self.bar_length - current_position), int(progress * 100)))
		sys.stdout.flush()
		if current == self.total:
			cprint('\n%s' % self.completed_msg, 'green', attrs=['bold'])


class EventIndicatorMatrix:

	total_events = 0
	line_limit = 20
	event_count = 0
	errors = []


	def __init__(self, total_events, line_limit=20, start_msg=''):
		self.total_events = total_events
		self.line_limit = line_limit
		print start_msg
		sys.stdout.write("\n  ")

	def step(self, result):
		self.event_count += 1
		if result:
			msg = colored('.', 'green')
		else:
			msg = colored('X', 'red')

		if self.event_count % self.line_limit == 0:
			msg += '  [ %d/%d ]\n  ' % (self.event_count, self.total_events)

		sys.stdout.write(msg)
		sys.stdout.flush()

		if self.event_count == self.total_events:
			sys.stdout.write('%s  [ %d/%d ]\n\n' % (' '*(self.line_limit - (self.event_count % self.line_limit)), self.event_count, self.total_events))
			sys.stdout.flush()
			self._wrap_up()

	def register_error(self, error):
		self.errors.append(error)

	def _wrap_up(self):
		if len(self.errors) > 0:
			cprint('finished, but encountered %d errors:' % len(self.errors), 'red', attrs=['bold'])
			c = 0
			for error in self.errors:
				c += 1
				print ' %d. %s' % (c, error)
		else:
			cprint('finished with 0 registered errors', 'green', attrs=['bold'])
		print '\n',

class Table:

	rows = []
	column_titles = OrderedDict()
	column_sizes = OrderedDict()
	bordered = True

	def __init__(self, column_titles=(), bordered=True):
		for title in column_titles:
			self.add_column(title)
		self.bordered = bordered

	def add_column(self, column_name):
		if(column_name in self.column_titles):
			raise Exception('duplicate column names are not allowed')
		current_place = len(self.column_titles)
		self.column_titles[current_place] = str(column_name)
		self.column_sizes[current_place] = len(column_name) + 3
		return self

	def add_row(self, data):
		if len(data) != len(self.column_titles):
			raise Exception('invalid column count in row data: %s' % data)
		self.rows.append(data)
		self._verify_column_widths(data)
		return self

	def _verify_column_widths(self, data):
		c = 0
		for item in data:
			if (len(str(item)) + 3) > self.column_sizes[c]:
				self.column_sizes[c] = len(str(item))
			c += 1

	def __str__(self):
		format_str = ''
		final_str = ''
		for i, length in self.column_sizes.items():
			if(self.bordered):
				if i is 0:
					format_str += '|'
				format_str += ' %%-%d.%ds |' % (length, length)
			else:
				format_str += '%%-%d.%ds   ' % (length, length)
		format_str += '\n'
		if(self.bordered):
			table_border = '+'
			for i, size in self.column_sizes.items():
				table_border += '-%s-+' % ('-'*size)
			table_border += '\n'
			final_str += table_border

		final_str += format_str % tuple(title for i, title in self.column_titles.items())
		if(self.bordered):
			final_str += table_border
		else:
			final_str += format_str % tuple('-'*(self.column_sizes[i]) for i, title in self.column_titles.items())

		for data in self.rows:
			final_str += format_str % data

		if(self.bordered):
			final_str += table_border

		return '\n%s' % final_str

if __name__ == '__main__':
	t = Table(('one', 'two', 'three', 'four'))
	t.add_row(('foobarrrrrrrrr', 'baztaz', 'foobarbaz', 'bar'))
	print t