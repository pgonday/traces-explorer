
import decimal
import json
import requests
import time
import sys

from web3 import Web3

LENDING_POOL_ADDRESSES_PROVIDER_ADDRESS = '0xB53C1a33016B2DC2fF3653530bfF1848a515c8c5'


env = {}
with open('.env') as f:
	for line in f:
		name, value = line.split('=')
		env[name] = value
apikey = env['ETHERSCAN_API_KEY']


def load_json(filename):
	with open(f'abis/{filename}.json', 'r') as f:
		abi = json.load(f)
	return abi


def load(action, address):
	if len(apikey) == 0:
		time.sleep(1) # Rate limit EtherScan API
	rsp = requests.get(f'https://api.etherscan.io/api?module=contract&action={action}&address={address}&apikey={apikey}')
	return json.loads(rsp.content)['result']


def load_abi(address):
	return load('getabi', address)


def load_source_code(address):
	return load('getsourcecode', address)


def get_proxy_implementation(address):	
	abi = load_abi(address)
	if 'newImplementation' in abi:
		impl_address = w3.eth.get_storage_at(address, '0x360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc')
		return '0x' + Web3.toHex(impl_address)[26:]
	elif 'updateImplementation' in abi:
		proxy = w3.eth.contract(address = address, abi = proxy_abi)
		return proxy.functions.implementation().call()
	
	return None


def get_asset(address):
	token = w3.eth.contract(address = address, abi = erc20_abi)
	symbol = token.functions.symbol().call()
	print(symbol, file=sys.stderr)
	impl = get_proxy_implementation(address)
	if impl:
		display_address_variants(impl, symbol)
		display_address_variants(address, symbol + ' (Proxy)')
	else:
		display_address_variants(address, symbol)


# Variants for addresses:
# - full address (0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063)
# - compact address (0x8f3C...A063)
# - return parameter (0x0000000000000000000000008f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063)
# - parameter (0000000000000000000000008f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063)
def display_address_variants(address, name):
	print(address, name, sep = '\t')
	print(address[:6] + '...' + address[-4:], name, sep = '\t')
	print('0x000000000000000000000000' + address[2:], name, sep = '\t')
	print('000000000000000000000000' + address[2:], name, sep = '\t')


def get_contract(address, contract_name = ''):
	impl = get_proxy_implementation(address)
	
	if not contract_name:
		source = load_source_code(impl if impl else address)
		contract_name = source[0]['ContractName']
	
	print(contract_name, file=sys.stderr)
	if impl:
		display_address_variants(address, contract_name + ' (Proxy)')
		display_address_variants(impl, contract_name)
	else:
		display_address_variants(address, contract_name)
	

w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'))

lending_pool_addresses_provider = w3.eth.contract(address = LENDING_POOL_ADDRESSES_PROVIDER_ADDRESS, abi = load_json('lendingpooladdressesprovider'))
lending_pool_address = lending_pool_addresses_provider.functions.getLendingPool().call()
lending_pool = w3.eth.contract(address = lending_pool_address, abi = load_json('lendingpool'))

erc20_abi = load_json('erc20')
atoken_abi = load_json('atoken')
proxy_abi = load_json('proxy')

# Get assets
list = lending_pool.functions.getReservesList().call()
for asset in list:
	reserve_data = lending_pool.functions.getReserveData(asset).call()	
	
	# aToken
	atoken_address = reserve_data[7]
	get_asset(atoken_address)

	# underlying token
	atoken = w3.eth.contract(address = atoken_address, abi = atoken_abi)
	underlying_token_address = atoken.functions.UNDERLYING_ASSET_ADDRESS().call()
	get_asset(underlying_token_address)

	# stable debt token
	get_asset(reserve_data[8])
	
	# variable debt token
	get_asset(reserve_data[9])


# Get contracts
get_contract(lending_pool_addresses_provider.address)
get_contract(lending_pool.address)
get_contract(lending_pool_addresses_provider.functions.getPriceOracle().call())
get_contract(lending_pool_addresses_provider.functions.getAddress('0x1000000000000000000000000000000000000000000000000000000000000000').call())
#get_contract('0x357D51124f59836DeD84c8a1730D72B749d8BC23') # IncentivesController
#get_contract('0xCC7dF14A5dE0145cE3438CBf29dF1cA84e56a9B5', 'ValidationLogic') # ValidationLogic library
