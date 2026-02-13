"""Decoder for Uniswap V2 Factory PairCreated events."""

from web3 import Web3
from eth_abi import decode


def get_paircreated_event_signature() -> str:
    """
    Get the topic hash for PairCreated event.
    
    Event signature: PairCreated(address indexed token0, address indexed token1, address pair, uint)
    
    Returns:
        str: The keccak256 hash of the event signature (topic0)
    """
    return '0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9'


def decode_paircreated_event(log: dict) -> dict:
    """
    Decode a PairCreated event log.
    
    Event structure:
        - topic0: event signature hash
        - topic1: token0 (indexed)
        - topic2: token1 (indexed)
        - data: pair address and pair index (uint)
    
    Args:
        log: Raw log dictionary from eth_getLogs
        
    Returns:
        dict: Decoded event with fields:
            - pair_address: Address of the created pair contract
            - token0: Address of the first token
            - token1: Address of the second token
            - pair_index: Sequential index of the pair
            - block_number: Block number where pair was created
            - transaction_hash: Transaction hash that created the pair
    """
    try:
        # Extract indexed parameters from topics
        # topic0 is the event signature, topics[1] and [2] are token0 and token1
        topics = log['topics']
        
        if len(topics) < 3:
            raise ValueError(f"Invalid number of topics: {len(topics)}")
        
        # Convert topics to addresses (remove 0x and pad to 40 chars)
        token0 = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
        token1 = Web3.to_checksum_address('0x' + topics[2].hex()[-40:])
        
        # Decode non-indexed parameters from data
        # data contains: pair address (address) and pair index (uint256)
        data = log['data']
        
        # Convert to hex string and remove '0x' prefix
        if isinstance(data, str):
            if data.startswith('0x'):
                data = data[2:]
        elif isinstance(data, bytes):
            data = data.hex()
            if data.startswith('0x'):
                data = data[2:]
        
        # Decode: address (32 bytes padded) + uint256 (32 bytes)
        decoded = decode(['address', 'uint256'], bytes.fromhex(data))
        pair_address = Web3.to_checksum_address(decoded[0])
        pair_index = decoded[1]
        
        return {
            'pair_address': pair_address,
            'token0': token0,
            'token1': token1,
            'pair_index': pair_index,
            'block_number': log['blockNumber'],
            'transaction_hash': log['transactionHash'].hex() if isinstance(log['transactionHash'], bytes) else log['transactionHash']
        }
        
    except Exception as e:
        raise ValueError(f"Failed to decode PairCreated event: {e}") from e
