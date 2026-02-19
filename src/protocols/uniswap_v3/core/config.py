"""Configuration loader for Uniswap V3 indexer."""

import os
from dotenv import load_dotenv


def load_config() -> dict:
    """
    Load configuration from .env file.
    
    Returns:
        dict: Configuration dictionary with keys:
            - RPC_URL: Ethereum RPC endpoint URL
            - FACTORY_ADDRESS: Uniswap V3 Factory contract address (from UNISWAP_V3_FACTORY_ADDRESS env var)
            - START_BLOCK: Starting block number for indexing
            - BLOCK_RANGE: Number of blocks to index
            - BATCH_SIZE: Batch size for log requests
    """
    load_dotenv()
    
    config = {
        'RPC_URL': os.getenv('RPC_URL'),
        'FACTORY_ADDRESS': os.getenv('UNISWAP_V3_FACTORY_ADDRESS', '0x1F98431c8aD98523631AE4a59f267346ea31F984'),
        'START_BLOCK': int(os.getenv('UNISWAP_V3_START_BLOCK', os.getenv('START_BLOCK', '12369621'))),  # Uniswap V3 Factory deployed block
        'BLOCK_RANGE': 5000,
        'BATCH_SIZE': int(os.getenv('BATCH_SIZE', '2000'))
    }
    
    # Validate required fields
    if not config['RPC_URL']:
        raise ValueError("RPC_URL is not set in .env file")
    
    return config
