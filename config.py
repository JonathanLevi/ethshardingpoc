import random as rand
from web3 import Web3
import copy
import sys
from collections import defaultdict

ORBIT_MODE = False
if 'orbit' in sys.argv:
    ORBIT_MODE = True
# whether to generate more blocks in shards 0 and 1 (makes ORBITs happen faster)
MORE_BLOCKS_IN = None #[0, 1, 3, 4] # create more blocks in these shards. Set to None to disable

SWITCH_BLOCK_EXTRA = 2 # a multiplier for switch block weights (is added on top of regular weight)

if not ORBIT_MODE:
    INITIAL_TOPOLOGY = [[1, 2], [3, 4], [5], [], [], [6], []]
else:
    INITIAL_TOPOLOGY = [[1], []]
NUM_SHARDS = len(INITIAL_TOPOLOGY)

NUM_VALIDATORS_PER_SHARD = 5
NUM_VALIDATORS = 1 + NUM_VALIDATORS_PER_SHARD*NUM_SHARDS

SHARD_IDS = list(range(NUM_SHARDS))
VALIDATOR_NAMES = []
for i in range(NUM_VALIDATORS):
    VALIDATOR_NAMES.append(i)
VALIDATOR_WEIGHTS = {}
for v in VALIDATOR_NAMES:
    VALIDATOR_WEIGHTS[v] = rand.uniform(7, 10)


assert all([x > y for (y, lst) in enumerate(INITIAL_TOPOLOGY) for x in lst])

VALIDATOR_SHARD_ASSIGNMENT = {}
SHARD_VALIDATOR_ASSIGNMENT = {}

remaining_validators = copy.copy(VALIDATOR_NAMES)
remaining_validators.remove(0)

for ID in SHARD_IDS:
    sample = rand.sample(remaining_validators, NUM_VALIDATORS_PER_SHARD)

    SHARD_VALIDATOR_ASSIGNMENT[ID] = sample
    for v in sample:
        remaining_validators.remove(v)
        VALIDATOR_SHARD_ASSIGNMENT[v] = ID
print(VALIDATOR_SHARD_ASSIGNMENT)

TTL_CONSTANT = 5
TTL_SWITCH_CONSTANT = 1
assert TTL_CONSTANT > 0

NUM_TRANSACTIONS = 100

# Experiment parameters
NUM_ROUNDS = 1000
NUM_WITHIN_SHARD_RECEIPTS_PER_ROUND = NUM_SHARDS * 5 // 2
NUM_BETWEEN_SHARD_RECEIPTS_PER_ROUND = NUM_SHARDS * 7 // 2
MEMPOOL_DRAIN_RATE = 5

# In ORBIT_MODE the first orbit happens at SWITCH_ROUND, not at either of the ORBIT_ROUNDs
SWITCH_ROUND = 5
ORBIT_ROUND_1 = 45
ORBIT_ROUND_2 = 85

# Instant broadcast
FREE_INSTANT_BROADCAST = False

# Validity check options
VALIDITY_CHECKS_OFF = False
VALIDITY_CHECKS_WARNING_OFF = False

# The deadbeef address
DEADBEEF = Web3.toChecksumAddress(hex(1271270613000041655817448348132275889066893754095))

# Reporting Parameters
REPORTING = True
SHOW_FRAMES = True
SAVE_FRAMES = False
FIG_SIZE = (30, 20)
REPORT_INTERVAL = 1
PAUSE_LENGTH = 0.000000001
DISPLAY_WIDTH = 250
DISPLAY_HEIGHT = 250
DISPLAY_MARGIN = 5
SHARD_X_SPACING = 5
SHARD_Y_SPACING = 5
SHARD_MESSAGE_YOFFSET = 10
SHARD_MESSAGE_XOFFSET = 5

CONSENSUS_MESSAGE_HEIGHTS_TO_DISPLAY_IN_ROOT = 25

# Set to True to restrict routing to paths specified in MSG_ROUTES
RESTRICT_ROUTING = True

# Define message routes in a dict {source: [destination1, destination2, ...]}
if not ORBIT_MODE:
    MSG_ROUTES = {3: [6], 6: [3]}
else:
    MSG_ROUTES = {1: [0], 0: [1]}
