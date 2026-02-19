"""Storage utilities for saving indexed pool data."""

import os
import pandas as pd
from typing import List


def save_pools_to_csv(pools: List[dict], filename: str) -> None:
    """
    Save list of pools to CSV file in data/ directory.
    
    Args:
        pools: List of pool dictionaries with fields:
            - pool_address: Address of the pool contract
            - token0: Address of the first token
            - token1: Address of the second token
            - fee: Fee tier (uint24)
            - tick_spacing: Tick spacing for the pool (int24)
            - pair_index: Sequential index of the pool
            - block_number: Block number where pool was created
            - timestamp: Unix timestamp of the block
            - transaction_hash: Transaction hash that created the pool
        filename: Output CSV filename (will be saved in data/ directory)
    """
    if not pools:
        print("No pools to save")
        return
    
    # Ensure data directory exists
    data_dir = 'data/uniswap_v3'
    os.makedirs(data_dir, exist_ok=True)
    
    # Create full path
    filepath = os.path.join(data_dir, filename)
    
    # Create DataFrame with specified column order
    df = pd.DataFrame(pools, columns=[
        'pool_address',
        'token0',
        'token1',
        'fee',
        'tick_spacing',
        'pair_index',
        'block_number',
        'timestamp',
        'transaction_hash'
    ])
    
    # Save to CSV in UTF-8 without BOM to avoid encoding issues
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"Saved {len(pools)} pools to {filepath}")


def save_pool_events_to_csv(events: List[dict], filename: str) -> None:
    """
    Save list of Pool events (Initialize, Mint, Burn, Collect, Swap, Flash) to CSV file in data/ directory.

    Args:
        events: List of event dicts with at least:
            - event_type: 'initialize' | 'mint' | 'burn' | 'collect' | 'swap' | 'flash'
            - pool_address, tx_from, block_number, transaction_hash, log_index
            - initialize: sqrtPriceX96, tick
            - mint: sender, owner, tickLower, tickUpper, amount, amount0, amount1
            - burn: owner, tickLower, tickUpper, amount, amount0, amount1
            - collect: owner, tickLower, tickUpper, amount0, amount1
            - swap: sender, recipient, amount0, amount1, sqrtPriceX96, liquidity, tick
            - flash: sender, recipient, amount0, amount1, paid0, paid1
        filename: Output CSV filename (will be saved in data/ directory)
    """
    if not events:
        print("No pool events to save")
        return

    data_dir = 'data/uniswap_v3'
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, filename)

    # Define all possible columns for all event types
    columns = [
        'event_type', 'pool_address', 'tx_from',
        # Initialize fields
        'sqrtPriceX96', 'tick',
        # Mint/Burn fields
        'sender', 'owner', 'tickLower', 'tickUpper', 'amount', 'amount0', 'amount1',
        # Collect fields (amount0, amount1 already included above)
        # Swap fields
        'recipient', 'liquidity',
        # Flash fields
        'paid0', 'paid1',
        # Common fields
        'block_number', 'transaction_hash', 'log_index'
    ]

    rows = []
    for e in events:
        row = {k: e.get(k, '') for k in columns}
        rows.append(row)

    df = pd.DataFrame(rows, columns=columns)
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"Saved {len(events)} pool events to {filepath}")
