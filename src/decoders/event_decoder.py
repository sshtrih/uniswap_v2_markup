"""Decoder for Uniswap V2 Factory PairCreated and Pair (Swap, Mint, Burn) events."""

from web3 import Web3
from eth_abi import decode


# Pair event signatures (topic0) - keccak256 of event signature
_SWAP_TOPIC = Web3.keccak(text='Swap(address,uint256,uint256,uint256,uint256,address)').hex()
_MINT_TOPIC = Web3.keccak(text='Mint(address,uint256,uint256)').hex()
_BURN_TOPIC = Web3.keccak(text='Burn(address,uint256,uint256,address)').hex()


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


def get_swap_event_signature() -> str:
    """
    Get the topic hash for Pair Swap event.

    Event signature: Swap(address indexed sender, uint amount0In, uint amount1In, uint amount0Out, uint amount1Out, address indexed to)

    Returns:
        str: The keccak256 hash of the event signature (topic0)
    """
    return _SWAP_TOPIC


def get_mint_event_signature() -> str:
    """
    Get the topic hash for Pair Mint event.

    Event signature: Mint(address indexed sender, uint amount0, uint amount1)

    Returns:
        str: The keccak256 hash of the event signature (topic0)
    """
    return _MINT_TOPIC


def get_burn_event_signature() -> str:
    """
    Get the topic hash for Pair Burn event.

    Event signature: Burn(address indexed sender, uint amount0, uint amount1, address indexed to)

    Returns:
        str: The keccak256 hash of the event signature (topic0)
    """
    return _BURN_TOPIC


def _hex_to_bytes(data) -> bytes:
    """Convert log data (str or bytes) to bytes for ABI decode."""
    if isinstance(data, str):
        data = data[2:] if data.startswith('0x') else data
        return bytes.fromhex(data)
    if isinstance(data, bytes):
        return data
    raise ValueError(f"Unexpected data type: {type(data)}")


def _tx_hash_hex(tx_hash) -> str:
    """Normalize transaction hash to hex string."""
    if isinstance(tx_hash, bytes):
        return tx_hash.hex()
    return tx_hash


def decode_swap_event(log: dict) -> dict:
    """
    Decode a Pair Swap event log.

    Event: Swap(address indexed sender, uint amount0In, uint amount1In, uint amount0Out, uint amount1Out, address indexed to)
    topic1=sender, topic2=to, data=amount0In, amount1In, amount0Out, amount1Out

    Args:
        log: Raw log dictionary from eth_getLogs

    Returns:
        dict: pair_address, sender, amount0In, amount1In, amount0Out, amount1Out, to, block_number, transaction_hash, log_index
    """
    try:
        topics = log['topics']
        if len(topics) < 3:
            raise ValueError(f"Invalid number of topics for Swap: {len(topics)}")
        sender = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
        to = Web3.to_checksum_address('0x' + topics[2].hex()[-40:])
        data = _hex_to_bytes(log['data'])
        amount0In, amount1In, amount0Out, amount1Out = decode(
            ['uint256', 'uint256', 'uint256', 'uint256'], data
        )
        pair_address = Web3.to_checksum_address(log['address'])
        return {
            'event_type': 'swap',
            'pair_address': pair_address,
            'sender': sender,
            'amount0In': amount0In,
            'amount1In': amount1In,
            'amount0Out': amount0Out,
            'amount1Out': amount1Out,
            'to': to,
            'block_number': log['blockNumber'],
            'transaction_hash': _tx_hash_hex(log['transactionHash']),
            'log_index': log['logIndex'],
        }
    except Exception as e:
        raise ValueError(f"Failed to decode Swap event: {e}") from e


def decode_mint_event(log: dict) -> dict:
    """
    Decode a Pair Mint event log.

    Event: Mint(address indexed sender, uint amount0, uint amount1)
    topic1=sender, data=amount0, amount1

    Args:
        log: Raw log dictionary from eth_getLogs

    Returns:
        dict: pair_address, sender, amount0, amount1, block_number, transaction_hash, log_index
    """
    try:
        topics = log['topics']
        if len(topics) < 2:
            raise ValueError(f"Invalid number of topics for Mint: {len(topics)}")
        sender = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
        data = _hex_to_bytes(log['data'])
        amount0, amount1 = decode(['uint256', 'uint256'], data)
        pair_address = Web3.to_checksum_address(log['address'])
        return {
            'event_type': 'mint',
            'pair_address': pair_address,
            'sender': sender,
            'amount0': amount0,
            'amount1': amount1,
            'block_number': log['blockNumber'],
            'transaction_hash': _tx_hash_hex(log['transactionHash']),
            'log_index': log['logIndex'],
        }
    except Exception as e:
        raise ValueError(f"Failed to decode Mint event: {e}") from e


def decode_burn_event(log: dict) -> dict:
    """
    Decode a Pair Burn event log.

    Event: Burn(address indexed sender, uint amount0, uint amount1, address indexed to)
    topic1=sender, topic2=to, data=amount0, amount1

    Args:
        log: Raw log dictionary from eth_getLogs

    Returns:
        dict: pair_address, sender, amount0, amount1, to, block_number, transaction_hash, log_index
    """
    try:
        topics = log['topics']
        if len(topics) < 3:
            raise ValueError(f"Invalid number of topics for Burn: {len(topics)}")
        sender = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
        to = Web3.to_checksum_address('0x' + topics[2].hex()[-40:])
        data = _hex_to_bytes(log['data'])
        amount0, amount1 = decode(['uint256', 'uint256'], data)
        pair_address = Web3.to_checksum_address(log['address'])
        return {
            'event_type': 'burn',
            'pair_address': pair_address,
            'sender': sender,
            'amount0': amount0,
            'amount1': amount1,
            'to': to,
            'block_number': log['blockNumber'],
            'transaction_hash': _tx_hash_hex(log['transactionHash']),
            'log_index': log['logIndex'],
        }
    except Exception as e:
        raise ValueError(f"Failed to decode Burn event: {e}") from e


def decode_pair_event(log: dict) -> dict:
    """
    Determine Pair event type (swap, mint, burn) and decode using the appropriate decoder.

    Args:
        log: Raw log dictionary from eth_getLogs

    Returns:
        dict: Decoded event with event_type and type-specific fields
    """
    raw = log['topics'][0]
    topic0 = (raw.hex() if isinstance(raw, bytes) else raw).lower().replace('0x', '')
    swap = _SWAP_TOPIC.lower().replace('0x', '')
    mint = _MINT_TOPIC.lower().replace('0x', '')
    burn = _BURN_TOPIC.lower().replace('0x', '')
    if topic0 == swap:
        return decode_swap_event(log)
    if topic0 == mint:
        return decode_mint_event(log)
    if topic0 == burn:
        return decode_burn_event(log)
    raise ValueError(f"Unknown Pair event topic0: {topic0}")
