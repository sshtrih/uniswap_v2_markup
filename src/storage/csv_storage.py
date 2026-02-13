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
    
    # Save to CSV
    df.to_csv(filepath, index=False)
    print(f"Saved {len(pairs)} pairs to {filepath}")
