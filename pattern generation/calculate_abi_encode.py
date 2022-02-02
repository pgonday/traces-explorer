import re
import sys
import sha3

# pb when mapping(=>) in param !
pattern_function = re.compile(r'^.*::(.*)\((.*)\)$')

fname = sys.argv[1]
with open(fname) as file:
	for line in file:		
		m = pattern_function.match(line)
		if m.group(2) == '':
			clean = m.group(1) + '()'
		else:
			params = m.group(2).split(",")
			clean_params = []
			for param in params:
				clean_params.append(param.strip().split(" ")[0])

			clean = m.group(1) + '(' + ','.join(clean_params) + ')'
		
		k = sha3.keccak_256()
		k.update(str.encode(clean))
		print('::' +  k.hexdigest()[:8] + '\t' + '::' + m.group(1))
