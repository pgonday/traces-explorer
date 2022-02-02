
for f in $(find ../Aave/protocol-v2/contracts -type f -name '*.sol'); do
	echo "${f##*/}"
	tr -d '\r\n' < $f > aave_contracts/${f##*/}
done

grep -Po 'function [a-zA-Z0-9_]+\([^\)]*\)' aave_contracts/*.sol | sed -e 's/aave_contracts\///' -e 's/.sol:function /::/' > aave_functions.sol
py calculate_abi_encode.py aave_functions.sol | sort | uniq > patterns_functions.txt
rm aave_functions.sol

sed 's/^\(.*\)\t\(0x.\{4\}\).\{32\}\(.\{4\}\)$/\2…\3\t\1/' aave_polygon.txt > patterns_modules.txt
