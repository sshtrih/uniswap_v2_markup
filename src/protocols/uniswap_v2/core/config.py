"""Configuration loader for Uniswap V2 indexer."""

import os
from dotenv import load_dotenv


def load_config() -> dict:
    """
    Load configuration from .env file.
    
    Returns:
        dict: Configuration dictionary with keys:
            - RPC_URL: Ethereum RPC endpoint URL
            - FACTORY_ADDRESS: Uniswap V2 Factory contract address (from UNISWAP_V2_FACTORY_ADDRESS env var)
            - START_BLOCK: Starting block number for indexing
            - BLOCK_RANGE: Number of blocks to index
            - BATCH_SIZE: Batch size for log requests
    """
    load_dotenv()
    
    config = {
        'RPC_URL': os.getenv('RPC_URL'),
        'FACTORY_ADDRESS': os.getenv('UNISWAP_V2_FACTORY_ADDRESS', '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'),
        'START_BLOCK': int(os.getenv('UNISWAP_V2_START_BLOCK', os.getenv('START_BLOCK', '10000835'))),  # Default: ~May 2020 (can be set to Factory deployment block)
        'BLOCK_RANGE': int(os.getenv('BLOCK_RANGE', '50000')),
        'BATCH_SIZE': int(os.getenv('BATCH_SIZE', '2000'))
    }
    
    # Validate required fields
    if not config['RPC_URL']:
        raise ValueError("RPC_URL is not set in .env file")
    if not config['FACTORY_ADDRESS']:
        raise ValueError("UNISWAP_V2_FACTORY_ADDRESS is not set in .env file")
    
    return config
