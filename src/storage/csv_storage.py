"""Storage utilities for saving indexed pair data."""

import os
import pandas as pd
from typing import List


def save_pairs_to_csv(pairs: List[dict], filename: str) -> None:
    """
    Save list of pairs to CSV file in data/ directory.
    
    Args:
        pairs: List of pair dictionaries with fields:
            - pair_address: Address of the pair contract
            - token0: Address of first token
            - token1: Address of second token
            - pair_index: Sequential index of the pair
            - block_number: Block number where pair was created
            - timestamp: Unix timestamp of the block
            - transaction_hash: Transaction hash that created the pair
        filename: Output CSV filename (will be saved in data/ directory)
    """
    if not pairs:
        print("No pairs to save")
        return
    
    # Ensure data directory exists
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    
    # Create full path
    filepath = os.path.join(data_dir, filename)
    
    # Create DataFrame with specified column order
    df = pd.DataFrame(pairs, columns=[
        'pair_address',
        'token0',
        'token1',
        'pair_index',
        'block_number',
        'timestamp',
        'transaction_hash'
    ])
    
    # Save to CSV in UTF-8 without BOM to avoid encoding issues
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"Saved {len(pairs)} pairs to {filepath}")


def save_pair_events_to_csv(events: List[dict], filename: str) -> None:
    """
    Save list of Pair events (Swap, Mint, Burn) to CSV file in data/ directory.

    Args:
        events: List of event dicts with at least:
            - event_type: 'swap' | 'mint' | 'burn'
            - pair_address, sender, tx_from, block_number, transaction_hash, log_index
            - swap: amount0In, amount1In, amount0Out, amount1Out, to
            - mint/burn: amount0, amount1; burn also has to
        filename: Output CSV filename (will be saved in data/ directory)
    """
    if not events:
        print("No pair events to save")
        return

    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, filename)

    columns = [
        'event_type', 'pair_address', 'sender', 'tx_from',
        'amount0', 'amount1', 'amount0In', 'amount1In', 'amount0Out', 'amount1Out',
        'to', 'block_number', 'transaction_hash', 'log_index'
    ]
    rows = []
    for e in events:
        row = {k: e.get(k, '') for k in columns}
        rows.append(row)

    df = pd.DataFrame(rows, columns=columns)
    df.to_csv(filepath, index=False, encoding='utf-8')
    print(f"Saved {len(events)} pair events to {filepath}")
