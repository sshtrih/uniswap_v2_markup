"""Configuration loader for Uniswap V2 indexer."""

import os
from dotenv import load_dotenv


def load_config() -> dict:
    """
    Load configuration from .env file.
    
    Returns:
        dict: Configuration dictionary with keys:
            - RPC_URL: Ethereum RPC endpoint URL
            - FACTORY_ADDRESS: Uniswap V2 Factory contract address
            - START_BLOCK: Starting block number for indexing
            - BLOCK_RANGE: Number of blocks to index
            - BATCH_SIZE: Batch size for log requests
    """
    load_dotenv()
    
    config = {
        'RPC_URL': os.getenv('RPC_URL'),
        'FACTORY_ADDRESS': os.getenv('FACTORY_ADDRESS'),
        'START_BLOCK': int(os.getenv('START_BLOCK', '10000835')),
        'BLOCK_RANGE': int(os.getenv('BLOCK_RANGE', '50000')),
        'BATCH_SIZE': int(os.getenv('BATCH_SIZE', '2000'))
    }
    
    # Validate required fields
    if not config['RPC_URL']:
        raise ValueError("RPC_URL is not set in .env file")
    if not config['FACTORY_ADDRESS']:
        raise ValueError("FACTORY_ADDRESS is not set in .env file")
    
    return config
