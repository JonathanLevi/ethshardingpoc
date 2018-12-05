import binascii
from collections import defaultdict
import json
import os
import subprocess
import sys
import copy

from eth_keys import keys
from eth_utils import decode_hex, encode_hex, to_wei
from eth_typing import Address
from eth import constants
from eth.rlp.logs import Log
from eth.rlp.receipts import Receipt
from eth.db.atomic import AtomicDB
from eth.vm.forks.byzantium import ByzantiumVM
from eth.vm.forks.byzantium.transactions import ByzantiumTransaction
from eth.chains.base import MiningChain
import rlp

from blocks import *
from web3 import Web3
from genesis_state import *
from config import DEADBEEF, SHARD_IDS
from generate_transactions import format_transaction

abi = json.loads('[{"constant":false,"inputs":[{"name":"_shard_ID","type":"uint256"},{"name":"_sendGas","type":"uint256"},{"name":"_sendToAddress","type":"address"},{"name":"_data","type":"bytes"}],"name":"send","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"shard_ID","type":"uint256"},{"indexed":false,"name":"sendGas","type":"uint256"},{"indexed":false,"name":"sendFromAddress","type":"address"},{"indexed":true,"name":"sendToAddress","type":"address"},{"indexed":false,"name":"value","type":"uint256"},{"indexed":false,"name":"data","type":"bytes"},{"indexed":true,"name":"base","type":"uint256"},{"indexed":false,"name":"TTL","type":"uint256"}],"name":"SentMessage","type":"event"}]')

web3 = Web3()
contract = web3.eth.contract(address='0x000000000000000000000000000000000000002A', abi=abi)

klass = MiningChain.configure( __name__='TestChain', vm_configuration=( (constants.GENESIS_BLOCK_NUMBER, ByzantiumVM), ) )
chain = klass.from_genesis(AtomicDB(), genesis_params, genesis_state)
initial_state = chain.get_vm().state

alice_key = '0x4c0883a69102937d6231471b5dbb6204fe5129617082792ae468d01a3f362318'
alice_address = web3.eth.account.privateKeyToAccount(alice_key).address.lower()
alice_nonces = []

def make_byzantium_txs(txs, alice_nonce):
    byzantium_txs = []
    for tx in txs:
        tx = copy.copy(tx)
        print(tx.keys())
        if 'gasPrice' in tx.keys():
            tx['gas_price'] = tx['gasPrice']
            tx.pop('gasPrice')
        if 'input' in tx.keys():
            tx['data'] = tx['input']
            tx.pop('input')
        if 'hash' in tx.keys():
            tx.pop('hash')
        tx_fields = ['nonce', 'gas_price', 'gas', 'value', 'v', 'r', 's']
        for field in tx_fields:
            if field in tx.keys():
                if isinstance(tx[field], str):
                    tx[field] = int(tx[field], 16)
        if isinstance(tx['to'], str):
            tx['to'] = decode_hex(tx['to'])
        if isinstance(tx['data'], str):
            tx['data'] = decode_hex(tx['data'])
        print(tx)
        try:
            byzantium_tx = ByzantiumTransaction(**tx)
            if encode_hex(byzantium_tx.sender) == alice_address:
                tx['nonce'] = alice_nonce
                alice_nonce += 1
                tx.pop('v')
                tx.pop('r')
                tx.pop('s')
                unsigned_tx = ByzantiumTransaction.create_unsigned_transaction(**tx)
                byzantium_tx = unsigned_tx.as_signed_transaction(keys.PrivateKey(decode_hex(alice_key)))
            byzantium_txs.append(byzantium_tx)
        except TypeError:
            print(tx)
            assert False, "That tx"
            pass
    return byzantium_txs

# the “transactions” list is a list of transactions that come from the
#   mempool (originally a file full of test data?) and ones that are constructed from
#   `MessagePayload`s. (This is done via `web3.eth.account.signTransaction(…)`.)
# function apply(vm_state, [txs], mapping(S => received)) -> (vm_state, mapping(S => received) )
def apply_to_state(pre_state, txs, received_log, genesis_blocks):
    alice_nonce = pre_state.account_db.get_nonce(decode_hex(alice_address))
    txs = make_byzantium_txs(txs, alice_nonce)
    nonce = pre_state.account_db.get_nonce(decode_hex(pusher_address))

    flattened_payloads = [message.payload for l in received_log.values() for message in l]
    for payload in flattened_payloads:
        unsigned_tx = {
            "gas": 3000000,
            "gas_price": int("0x2", 16),
            "nonce": nonce,
            "to": payload.toAddress,
            "value": payload.value,
            "data": payload.data,
        }
        unsigned_tx = ByzantiumTransaction.create_unsigned_transaction(**unsigned_tx)
        tx = unsigned_tx.as_signed_transaction(keys.PrivateKey(decode_hex(pusher_key)))
        nonce += 1
        txs.append(tx)

    state_roots = []
    computations = []
    all_logs = []
    receipts = []

    for tx in txs:
        if encode_hex(tx.sender)==alice_address:
            assert tx.nonce not in alice_nonces, "Nonce {} has occured before".format(tx.nonce)
            alice_nonces.append(tx.nonce)
        state_root, computation = pre_state.apply_transaction(tx)
        state_roots.append(state_root)
        computations.append(computation)

        logs = [
            Log(address, topics, data)
            for address, topics, data
            in computation.get_log_entries()
        ]
        all_logs.append(logs)

        receipt = Receipt(
            state_root=state_root,
            gas_used=50, # This is a fake filled-in gas_used value
            logs=logs,
        )
        receipts.append(receipt)

    sent_log = {}
    for ID in SHARD_IDS:
        sent_log[ID] = []
    for receipt in receipts:
        for event in contract.events.SentMessage().processReceipt(receipt):
            sent_log[event.args.shard_ID].append(
                # This is not a message that will be stored in the sent log, it will be
                # postprocessed in make_block. Namely, the next hop shard will be computed,
                # the base block will be computed and TTL will be assigned.
                Message(
                    Block(event.args.shard_ID, sources={ID : genesis_blocks[ID] for ID in SHARD_IDS}),
                    10,
                    event.args.shard_ID,
                    MessagePayload(
                        event.args.sendFromAddress.lower()[2:],
                        event.args.sendToAddress.lower()[2:],
                        event.args.value,
                        event.args.data,
                    )
                )
            )

    return pre_state, sent_log
