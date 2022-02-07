
import re
import requests
import sys


def load_patterns(dict, files):
	for file in files:
		with open(file + '.txt') as f:
			for line in f:
				elements = line.replace('\n', '').split('\t')
				dict[elements[0]] = elements[1]


def search_and_replace_function(line):
	sig = line.split('::')[1].split('(')[0]
	if len(sig) == 8:
		
		if not sig in functions:
			rsp = requests.get(f'https://raw.githubusercontent.com/ethereum-lists/4bytes/master/signatures/{sig}')
			if rsp.status_code == 404:
				functions[sig] = sig
			else:
				functions[sig] = rsp.text
		
		fname = functions[sig]
		i = fname.find('(')
		if i != -1:
			fname = fname[:i]
		line = line.replace(sig, fname)
	
	return line


def save_functions():
	print('Functions cache updated, saving...')
	with open("patterns_functions.txt", 'w') as f:
		for search, replace in sorted(functions.items()):
			f.write(search)
			f.write('\t')
			f.write(replace)
			f.write('\n')


patterns = {}
functions = {}

load_patterns(patterns, ['patterns_escape_sequences', 'patterns'])
load_patterns(functions, ['patterns_functions'])
functions_len = len(functions)

fname = sys.argv[1]
ftraces = open(fname, encoding ='utf8')

traces = '<ul class="tree">'
level = 0
prev_line = ''
started = False
for line in ftraces.read().splitlines():
	if line == '':
		continue
	
	if not started:
		if '[' in line and line[-1] == ')':
			started = True
		else:
			traces += '<li>' + line + '</li>'
			continue
		
	new_level = line.count('├') + line.count('│') + line.count('└')
	if level != new_level:
		if new_level > level:
			if '31m' in prev_line:
				traces += '<ul>'
			else:
				traces += '<ul style="display: none;">'
		else:
			traces += '</li></ul>'
	else:
		if level > 0:
			traces += '</li>'
	level = new_level
	
	if '::' in line:		
		line = search_and_replace_function(line)
	
	traces += '<li><div>' + line + '</div>'
	
	prev_line = line
	
traces += '</li></ul>'

traces = traces.replace('…', '...')
traces = traces.replace('[', 'ESC')


for search, replace in patterns.items():
	traces = re.sub(search, replace, traces, flags = re.IGNORECASE)
	
with open(fname + '.html', 'w', encoding ='utf8') as f:
	f.write("""
<html>
  <head>
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
    <style>
      p { margin: 0; }
	  ul { padding-left: 0; }
	  li { list-style-type: none; cursor: hand; }
    </style>
  </head>
  <body style="background-color:black;color:white;font-family:monospace">
""");
	f.write(traces)
	f.write("""
<script>
$(document).ready(function () {
    $("li").on("click", function (e) {
		e.stopPropagation();
		$(this).children('ul').toggle();       
	});
});
</script>
""")
	f.write('</body></html>')


if len(functions) != functions_len:
	save_functions()