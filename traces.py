
import sys
import re

patterns_files = ['patterns_escape_sequences', 'patterns_tokens', 'patterns_modules', 'patterns_functions']
patterns = []

for pfile in patterns_files:
	with open(pfile + '.txt') as f:
		for line in f:
			elements = line.replace('\n', '').split('\t')
			patterns.append({
				'search': elements[0],
				'replace': elements[1]
			})

fname = sys.argv[1]
ftraces = open(fname, encoding ='utf8')

traces = ""
for line in ftraces.read().splitlines():
	line = line.replace('<', '&lt;')
	line = line.replace('>', '&gt;')
	traces += '<p>' + line + '</p>'

traces = traces.replace('…', '...')
traces = traces.replace('[', 'ESC')


for pattern in patterns:
	search = pattern['search']
	replace = pattern['replace']
	traces = re.sub(search, replace, traces, flags = re.IGNORECASE)
	
with open(fname + '.html', 'w', encoding ='utf8') as f:
	f.write('<html><head><style>p { margin: 0; }</style></head><body style="background-color:black;color:white;font-family:monospace">');
	f.write(traces)
	f.write('</body></html>')
