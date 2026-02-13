"""Storage utilities for saving indexed pair data."""

import pandas as pd
from typing import List


def save_pairs_to_csv(pairs: List[dict], filename: str) -> None:
    """
    Save list of pairs to CSV file.
    
    Args:
        pairs: List of pair dictionaries with fields:
            - pair_address: Address of the pair contract
            - token0: Address of first token
            - token1: Address of second token
            - pair_index: Sequential index of the pair
            - block_number: Block number where pair was created
            - timestamp: Unix timestamp of the block
            - transaction_hash: Transaction hash that created the pair
        filename: Output CSV filename
    """
    if not pairs:
        print("No pairs to save")
        return
    
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
    df.to_csv(filename, index=False)
    print(f"Saved {len(pairs)} pairs to {filename}")
