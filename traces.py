
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
for line in ftraces.read().splitlines():
	if line == '':
		continue

	if '::' in line:
		line = search_and_replace_function(line)

	line = line.replace('<', '&lt;')
	line = line.replace('>', '&gt;')
	
	if '├─' in line or ('[' == line[0] and ')' == line[-1]):
		traces += '<ul>'
	
	traces += '<li><a href="#">' + line + '</a>\n'
	
	if '└' in line:
		traces += '</li></ul></li>'
traces += '</ul>'

traces = traces.replace('…', '...')
traces = traces.replace('[', 'ESC')


for search, replace in patterns.items():
	traces = re.sub(search, replace, traces, flags = re.IGNORECASE)
	
with open(fname + '.html', 'w', encoding ='utf8') as f:
	f.write("""
<html>
  <head>
    <style>
      p { margin: 0; }
	  ul { padding-left: 0; }
	  li { list-style-type: none; }
	  /*ul.tree li ul { display: none; }*/
	  ul.tree li.open > ul { display: block; }
	  ul.tree li a { color: white; text-decoration: none; }
    </style>
  </head>
  <body style="background-color:black;color:white;font-family:monospace">
""");
	f.write(traces)
	f.write("""
<script>
window.addEventListener("load", function(){
var tree = document.querySelectorAll('ul.tree a:not(:last-child)');
for(var i = 0; i < tree.length; i++){
    tree[i].addEventListener('click', function(e) {
        var parent = e.target.parentElement;
        var classList = parent.classList;
        if(classList.contains("open")) {
            classList.remove('open');
            var opensubs = parent.querySelectorAll(':scope .open');
            for(var i = 0; i < opensubs.length; i++){
                opensubs[i].classList.remove('open');
            }
        } else {
            classList.add('open');
        }
        e.preventDefault();
    });
}
});
</script>
""")
	f.write('</body></html>')


if len(functions) != functions_len:
	save_functions()