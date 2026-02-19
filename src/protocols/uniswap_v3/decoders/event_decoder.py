"""Decoder for Uniswap V3 Factory PoolCreated and Pool (Initialize, Mint, Burn, Collect, Swap, Flash) events."""

from web3 import Web3
from eth_abi import decode


# Pool event signatures (topic0) - keccak256 of event signature
_INITIALIZE_TOPIC = Web3.keccak(text='Initialize(uint160,int24)').hex()
_MINT_TOPIC = Web3.keccak(text='Mint(address,address,int24,int24,uint128,uint256,uint256)').hex()
_BURN_TOPIC = Web3.keccak(text='Burn(address,int24,int24,uint128,uint256,uint256)').hex()
_COLLECT_TOPIC = Web3.keccak(text='Collect(address,address,int24,int24,uint128,uint128)').hex()
_SWAP_TOPIC = Web3.keccak(text='Swap(address,address,int256,int256,uint160,uint128,int24)').hex()
_FLASH_TOPIC = Web3.keccak(text='Flash(address,address,uint256,uint256,uint256,uint256)').hex()


def get_poolcreated_event_signature() -> str:
    """
    Get the topic hash for PoolCreated event.
    
    Event signature: PoolCreated(address indexed token0, address indexed token1, uint24 indexed fee, int24 tickSpacing, address pool)
    
    Returns:
        str: The keccak256 hash of the event signature (topic0)
    """
    return '0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118'


def decode_poolcreated_event(log: dict) -> dict:
    """
    Decode a PoolCreated event log.
    
    Event structure:
        - topic0: event signature hash
        - topic1: token0 (indexed)
        - topic2: token1 (indexed)
        - topic3: fee (indexed)
        - data: tickSpacing (int24) and pool address (address)
    
    Args:
        log: Raw log dictionary from eth_getLogs
        
    Returns:
        dict: Decoded event with fields:
            - pool_address: Address of the created pool contract
            - token0: Address of the first token
            - token1: Address of the second token
            - fee: Fee tier (uint24)
            - tick_spacing: Tick spacing for the pool (int24)
            - block_number: Block number where pool was created
            - transaction_hash: Transaction hash that created the pool
    """
    try:
        topics = log['topics']
        
        if len(topics) < 4:
            raise ValueError(f"Invalid number of topics: {len(topics)}")
        
        # Extract indexed parameters from topics
        token0 = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
        token1 = Web3.to_checksum_address('0x' + topics[2].hex()[-40:])
        
        # topic3 is fee (uint24, padded to 32 bytes)
        # Extract last 3 bytes (uint24) from the 32-byte padded value
        topic3_bytes = topics[3] if isinstance(topics[3], bytes) else bytes.fromhex(topics[3].replace('0x', ''))
        fee = int.from_bytes(topic3_bytes[-3:], byteorder='big')
        
        # Decode non-indexed parameters from data
        # data contains: tickSpacing (int24, 32 bytes padded) + pool address (address, 32 bytes padded)
        data = log['data']
        
        # Convert to hex string and remove '0x' prefix
        if isinstance(data, str):
            if data.startswith('0x'):
                data = data[2:]
        elif isinstance(data, bytes):
            data = data.hex()
            if data.startswith('0x'):
                data = data[2:]
        
        # Decode: int24 tickSpacing (32 bytes) + address pool (32 bytes)
        decoded = decode(['int24', 'address'], bytes.fromhex(data))
        tick_spacing = decoded[0]
        pool_address = Web3.to_checksum_address(decoded[1])
        
        return {
            'pool_address': pool_address,
            'token0': token0,
            'token1': token1,
            'fee': fee,
            'tick_spacing': tick_spacing,
            'block_number': log['blockNumber'],
            'transaction_hash': log['transactionHash'].hex() if isinstance(log['transactionHash'], bytes) else log['transactionHash']
        }
        
    except Exception as e:
        raise ValueError(f"Failed to decode PoolCreated event: {e}") from e


def get_initialize_event_signature() -> str:
    """
    Get the topic hash for Pool Initialize event.
    
    Event signature: Initialize(uint160 sqrtPriceX96, int24 tick)
    
    Returns:
        str: The keccak256 hash of the event signature (topic0)
    """
    return _INITIALIZE_TOPIC


def get_mint_event_signature() -> str:
    """
    Get the topic hash for Pool Mint event.
    
    Event signature: Mint(address sender, address indexed owner, int24 indexed tickLower, int24 indexed tickUpper, uint128 amount, uint256 amount0, uint256 amount1)
    
    Returns:
        str: The keccak256 hash of the event signature (topic0)
    """
    return _MINT_TOPIC


def get_burn_event_signature() -> str:
    """
    Get the topic hash for Pool Burn event.
    
    Event signature: Burn(address indexed owner, int24 indexed tickLower, int24 indexed tickUpper, uint128 amount, uint256 amount0, uint256 amount1)
    
    Returns:
        str: The keccak256 hash of the event signature (topic0)
    """
    return _BURN_TOPIC


def get_collect_event_signature() -> str:
    """
    Get the topic hash for Pool Collect event.
    
    Event signature: Collect(address indexed owner, address recipient, int24 indexed tickLower, int24 indexed tickUpper, uint128 amount0, uint128 amount1)
    
    Returns:
        str: The keccak256 hash of the event signature (topic0)
    """
    return _COLLECT_TOPIC


def get_swap_event_signature() -> str:
    """
    Get the topic hash for Pool Swap event.
    
    Event signature: Swap(address indexed sender, address indexed recipient, int256 amount0, int256 amount1, uint160 sqrtPriceX96, uint128 liquidity, int24 tick)
    
    Returns:
        str: The keccak256 hash of the event signature (topic0)
    """
    return _SWAP_TOPIC


def get_flash_event_signature() -> str:
    """
    Get the topic hash for Pool Flash event.
    
    Event signature: Flash(address indexed sender, address indexed recipient, uint256 amount0, uint256 amount1, uint256 paid0, uint256 paid1)
    
    Returns:
        str: The keccak256 hash of the event signature (topic0)
    """
    return _FLASH_TOPIC


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


def decode_initialize_event(log: dict) -> dict:
    """
    Decode a Pool Initialize event log.
    
    Event: Initialize(uint160 sqrtPriceX96, int24 tick)
    No indexed parameters, all data in data field.
    
    Args:
        log: Raw log dictionary from eth_getLogs
    
    Returns:
        dict: pool_address, sqrtPriceX96, tick, block_number, transaction_hash, log_index
    """
    try:
        data = _hex_to_bytes(log['data'])
        sqrtPriceX96, tick = decode(['uint160', 'int24'], data)
        pool_address = Web3.to_checksum_address(log['address'])
        return {
            'event_type': 'initialize',
            'pool_address': pool_address,
            'sqrtPriceX96': sqrtPriceX96,
            'tick': tick,
            'block_number': log['blockNumber'],
            'transaction_hash': _tx_hash_hex(log['transactionHash']),
            'log_index': log['logIndex'],
        }
    except Exception as e:
        raise ValueError(f"Failed to decode Initialize event: {e}") from e


def decode_mint_event(log: dict) -> dict:
    """
    Decode a Pool Mint event log.
    
    Event: Mint(address sender, address indexed owner, int24 indexed tickLower, int24 indexed tickUpper, uint128 amount, uint256 amount0, uint256 amount1)
    topic1=owner, topic2=tickLower, topic3=tickUpper
    data=sender(address), amount(uint128), amount0(uint256), amount1(uint256)
    
    Args:
        log: Raw log dictionary from eth_getLogs
    
    Returns:
        dict: pool_address, sender, owner, tickLower, tickUpper, amount, amount0, amount1, block_number, transaction_hash, log_index
    """
    try:
        topics = log['topics']
        if len(topics) < 4:
            raise ValueError(f"Invalid number of topics for Mint: {len(topics)}")
        owner = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
        tickLower = int.from_bytes(topics[2] if isinstance(topics[2], bytes) else bytes.fromhex(topics[2].replace('0x', '')), byteorder='big', signed=True)
        tickUpper = int.from_bytes(topics[3] if isinstance(topics[3], bytes) else bytes.fromhex(topics[3].replace('0x', '')), byteorder='big', signed=True)
        data = _hex_to_bytes(log['data'])
        sender, amount, amount0, amount1 = decode(
            ['address', 'uint128', 'uint256', 'uint256'], data
        )
        sender = Web3.to_checksum_address(sender)
        pool_address = Web3.to_checksum_address(log['address'])
        return {
            'event_type': 'mint',
            'pool_address': pool_address,
            'sender': sender,
            'owner': owner,
            'tickLower': tickLower,
            'tickUpper': tickUpper,
            'amount': amount,
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
    Decode a Pool Burn event log.
    
    Event: Burn(address indexed owner, int24 indexed tickLower, int24 indexed tickUpper, uint128 amount, uint256 amount0, uint256 amount1)
    topic1=owner, topic2=tickLower, topic3=tickUpper
    data=amount(uint128), amount0(uint256), amount1(uint256)
    
    Args:
        log: Raw log dictionary from eth_getLogs
    
    Returns:
        dict: pool_address, owner, tickLower, tickUpper, amount, amount0, amount1, block_number, transaction_hash, log_index
    """
    try:
        topics = log['topics']
        if len(topics) < 4:
            raise ValueError(f"Invalid number of topics for Burn: {len(topics)}")
        owner = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
        tickLower = int.from_bytes(topics[2] if isinstance(topics[2], bytes) else bytes.fromhex(topics[2].replace('0x', '')), byteorder='big', signed=True)
        tickUpper = int.from_bytes(topics[3] if isinstance(topics[3], bytes) else bytes.fromhex(topics[3].replace('0x', '')), byteorder='big', signed=True)
        data = _hex_to_bytes(log['data'])
        amount, amount0, amount1 = decode(
            ['uint128', 'uint256', 'uint256'], data
        )
        pool_address = Web3.to_checksum_address(log['address'])
        return {
            'event_type': 'burn',
            'pool_address': pool_address,
            'owner': owner,
            'tickLower': tickLower,
            'tickUpper': tickUpper,
            'amount': amount,
            'amount0': amount0,
            'amount1': amount1,
            'block_number': log['blockNumber'],
            'transaction_hash': _tx_hash_hex(log['transactionHash']),
            'log_index': log['logIndex'],
        }
    except Exception as e:
        raise ValueError(f"Failed to decode Burn event: {e}") from e


def decode_collect_event(log: dict) -> dict:
    """
    Decode a Pool Collect event log.
    
    Event: Collect(address indexed owner, address recipient, int24 indexed tickLower, int24 indexed tickUpper, uint128 amount0, uint128 amount1)
    topic1=owner, topic2=tickLower, topic3=tickUpper
    data=recipient(address), amount0(uint128), amount1(uint128)
    
    Args:
        log: Raw log dictionary from eth_getLogs
    
    Returns:
        dict: pool_address, owner, recipient, tickLower, tickUpper, amount0, amount1, block_number, transaction_hash, log_index
    """
    try:
        topics = log['topics']
        if len(topics) < 4:
            raise ValueError(f"Invalid number of topics for Collect: {len(topics)}")
        owner = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
        tickLower = int.from_bytes(topics[2] if isinstance(topics[2], bytes) else bytes.fromhex(topics[2].replace('0x', '')), byteorder='big', signed=True)
        tickUpper = int.from_bytes(topics[3] if isinstance(topics[3], bytes) else bytes.fromhex(topics[3].replace('0x', '')), byteorder='big', signed=True)
        data = _hex_to_bytes(log['data'])
        recipient, amount0, amount1 = decode(
            ['address', 'uint128', 'uint128'], data
        )
        recipient = Web3.to_checksum_address(recipient)
        pool_address = Web3.to_checksum_address(log['address'])
        return {
            'event_type': 'collect',
            'pool_address': pool_address,
            'owner': owner,
            'recipient': recipient,
            'tickLower': tickLower,
            'tickUpper': tickUpper,
            'amount0': amount0,
            'amount1': amount1,
            'block_number': log['blockNumber'],
            'transaction_hash': _tx_hash_hex(log['transactionHash']),
            'log_index': log['logIndex'],
        }
    except Exception as e:
        raise ValueError(f"Failed to decode Collect event: {e}") from e


def decode_swap_event(log: dict) -> dict:
    """
    Decode a Pool Swap event log.
    
    Event: Swap(address indexed sender, address indexed recipient, int256 amount0, int256 amount1, uint160 sqrtPriceX96, uint128 liquidity, int24 tick)
    topic1=sender, topic2=recipient, data=amount0, amount1, sqrtPriceX96, liquidity, tick
    
    Args:
        log: Raw log dictionary from eth_getLogs
    
    Returns:
        dict: pool_address, sender, recipient, amount0, amount1, sqrtPriceX96, liquidity, tick, block_number, transaction_hash, log_index
    """
    try:
        topics = log['topics']
        if len(topics) < 3:
            raise ValueError(f"Invalid number of topics for Swap: {len(topics)}")
        sender = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
        recipient = Web3.to_checksum_address('0x' + topics[2].hex()[-40:])
        data = _hex_to_bytes(log['data'])
        amount0, amount1, sqrtPriceX96, liquidity, tick = decode(
            ['int256', 'int256', 'uint160', 'uint128', 'int24'], data
        )
        pool_address = Web3.to_checksum_address(log['address'])
        return {
            'event_type': 'swap',
            'pool_address': pool_address,
            'sender': sender,
            'recipient': recipient,
            'amount0': amount0,  # Can be negative
            'amount1': amount1,  # Can be negative
            'sqrtPriceX96': sqrtPriceX96,
            'liquidity': liquidity,
            'tick': tick,
            'block_number': log['blockNumber'],
            'transaction_hash': _tx_hash_hex(log['transactionHash']),
            'log_index': log['logIndex'],
        }
    except Exception as e:
        raise ValueError(f"Failed to decode Swap event: {e}") from e


def decode_flash_event(log: dict) -> dict:
    """
    Decode a Pool Flash event log.
    
    Event: Flash(address indexed sender, address indexed recipient, uint256 amount0, uint256 amount1, uint256 paid0, uint256 paid1)
    topic1=sender, topic2=recipient, data=amount0, amount1, paid0, paid1
    
    Args:
        log: Raw log dictionary from eth_getLogs
    
    Returns:
        dict: pool_address, sender, recipient, amount0, amount1, paid0, paid1, block_number, transaction_hash, log_index
    """
    try:
        topics = log['topics']
        if len(topics) < 3:
            raise ValueError(f"Invalid number of topics for Flash: {len(topics)}")
        sender = Web3.to_checksum_address('0x' + topics[1].hex()[-40:])
        recipient = Web3.to_checksum_address('0x' + topics[2].hex()[-40:])
        data = _hex_to_bytes(log['data'])
        amount0, amount1, paid0, paid1 = decode(
            ['uint256', 'uint256', 'uint256', 'uint256'], data
        )
        pool_address = Web3.to_checksum_address(log['address'])
        return {
            'event_type': 'flash',
            'pool_address': pool_address,
            'sender': sender,
            'recipient': recipient,
            'amount0': amount0,
            'amount1': amount1,
            'paid0': paid0,
            'paid1': paid1,
            'block_number': log['blockNumber'],
            'transaction_hash': _tx_hash_hex(log['transactionHash']),
            'log_index': log['logIndex'],
        }
    except Exception as e:
        raise ValueError(f"Failed to decode Flash event: {e}") from e


def decode_pool_event(log: dict) -> dict:
    """
    Determine Pool event type (initialize, mint, burn, collect, swap, flash) and decode using the appropriate decoder.
    
    Args:
        log: Raw log dictionary from eth_getLogs
    
    Returns:
        dict: Decoded event with event_type and type-specific fields
    """
    raw = log['topics'][0]
    topic0 = (raw.hex() if isinstance(raw, bytes) else raw).lower().replace('0x', '')
    
    initialize = _INITIALIZE_TOPIC.lower().replace('0x', '')
    mint = _MINT_TOPIC.lower().replace('0x', '')
    burn = _BURN_TOPIC.lower().replace('0x', '')
    collect = _COLLECT_TOPIC.lower().replace('0x', '')
    swap = _SWAP_TOPIC.lower().replace('0x', '')
    flash = _FLASH_TOPIC.lower().replace('0x', '')
    
    if topic0 == initialize:
        return decode_initialize_event(log)
    if topic0 == mint:
        return decode_mint_event(log)
    if topic0 == burn:
        return decode_burn_event(log)
    if topic0 == collect:
        return decode_collect_event(log)
    if topic0 == swap:
        return decode_swap_event(log)
    if topic0 == flash:
        return decode_flash_event(log)
    
    raise ValueError(f"Unknown Pool event topic0: {topic0}")
