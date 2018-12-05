from eth_keys import keys
from eth_utils import decode_hex, encode_hex, to_wei
from eth_typing import Address
from eth import constants
from web3 import Web3
from config import DEADBEEF

web3 = Web3()

# same "pusher" address on each shard
pusher_key = '0x6c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318'
pusher_address = web3.eth.account.privateKeyToAccount(pusher_key).address.lower()

genesis_params = {
        'parent_hash': constants.GENESIS_PARENT_HASH,
        'uncles_hash': constants.EMPTY_UNCLE_HASH,
        'coinbase': constants.ZERO_ADDRESS,
        'transaction_root': constants.BLANK_ROOT_HASH,
        'receipt_root': constants.BLANK_ROOT_HASH,
        'difficulty': int("0x20000", 16),
        'block_number': constants.GENESIS_BLOCK_NUMBER,
        'gas_limit': int("0x750a163df65e8a", 16),
        'timestamp': 1539724066,
        'extra_data': constants.GENESIS_EXTRA_DATA,
        'nonce': constants.GENESIS_NONCE
    }

# just gonna reuse this initial state on each shard.
genesis_state = {
  decode_hex(pusher_address): {
    "balance": int("0x5ffd4878be161d74", 16),
    "code": b'',
    "nonce": 0,
    "storage": {}
  },
  decode_hex(DEADBEEF.lower()): {
    "balance": int("0x1", 16),
    "code": b'',
    "nonce": 0,
    "storage": {}
  },
  decode_hex("0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b"): {
    "balance": int("0x5ffd4878be161d74", 16),
    "code": b'',
    "nonce": 0,
    "storage": {}
  },
  decode_hex("0x2c7536E3605D9C16a7a3D7b1898e529396a65c23"): {
    "balance": int("0x5ffd4878be161d74", 16),
    "code": b'',
    "nonce": 0,
    "storage": {}
  },
  decode_hex("0xc227e8f6eE49f35ddf4dd73F105cF743914B11Af"): {
    "balance": int("0x5ffd4878be161d74", 16),
    "code": b'',
    "nonce": 0,
    "storage": {}
  },
  decode_hex("0x8a8eafb1cf62bfbeb1741769dae1a9dd47996192"):{
    "balance": int("0xfeedbead", 16),
    "code": b'',
    "nonce" : 0,
    "storage": {}
  },
  decode_hex("0x000000000000000000000000000000000000002a"): {
    "balance": 0,
    "nonce": 0,
    "storage": {},
    "code": decode_hex("0x608060405260043610610041576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063e09ee87014610046575b600080fd5b6100d46004803603810190808035906020019092919080359060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001908201803590602001908080601f01602080910402602001604051908101604052809392919081815260200183838082843782019150505050505091929192905050506100d6565b005b6000806000439250349150339050438573ffffffffffffffffffffffffffffffffffffffff16887fe9fbdfd23831dbc2bdec9e9ef0d5ac734f56996d4211992cc083e97f2770ba428933348a600054604051808681526020018573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200184815260200180602001838152602001828103825284818151815260200191508051906020019080838360005b838110156101a957808201518184015260208101905061018e565b50505050905090810190601f1680156101d65780820380516001836020036101000a031916815260200191505b50965050505050505060405180910390a4505050505050505600a165627a7a7230582086844d62bfd54b247b20657c69410cefe95f27dcb63829d23c83f0d60883191e0029"),
  }
}
