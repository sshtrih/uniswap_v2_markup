"""Indexer for Uniswap V2 Pair events (Swap, Mint, Burn)."""

import os
import time
from typing import List

import pandas as pd
from web3 import Web3
from tqdm import tqdm

from src.decoders.event_decoder import (
    get_swap_event_signature,
    get_mint_event_signature,
    get_burn_event_signature,
    decode_pair_event,
)


def load_pair_addresses(csv_path: str) -> List[str]:
    """
    Load pair addresses from CSV file.

    Reads the CSV (e.g. data/uniswap_v2_pairs.csv) and returns a list of unique
    pair contract addresses.

    Args:
        csv_path: Path to CSV file with a 'pair_address' column.

    Returns:
        List of unique pair addresses (checksummed).
    """
    if not os.path.isfile(csv_path):
        raise FileNotFoundError(f"Pairs CSV not found: {csv_path}")
    df = pd.read_csv(csv_path, encoding='utf-8-sig')
    # Normalize: strip BOM and whitespace; accept column that ends with "pair_address" (handles BOM/mojibake prefix)
    _bom = '\ufeff'
    df.columns = [str(c).lstrip(_bom).strip() if isinstance(c, str) else c for c in df.columns]
    if 'pair_address' not in df.columns:
        for c in df.columns:
            if isinstance(c, str) and 'pair_address' in c.strip():
                df = df.rename(columns={c: 'pair_address'})
                break
    if 'pair_address' not in df.columns:
        raise ValueError(f"CSV must have 'pair_address' column; found: {list(df.columns)}")
    addresses = df['pair_address'].dropna().astype(str).str.strip().unique().tolist()
    return [Web3.to_checksum_address(addr) for addr in addresses]


def fetch_pair_logs_in_batches(
    w3: Web3,
    pair_addresses: List[str],
    start_block: int,
    end_block: int,
    batch_size: int,
) -> List[dict]:
    """
    Fetch Swap, Mint, and Burn logs for the given pair addresses in block batches.

    Uses eth_getLogs with filter by addresses and topic0 (Swap, Mint, Burn).
    Retries failed batches with exponential backoff (up to 3 attempts).
    Shows progress via tqdm.

    Args:
        w3: Connected Web3 instance.
        pair_addresses: List of Pair contract addresses to scan.
        start_block: First block (inclusive).
        end_block: Last block (inclusive).
        batch_size: Number of blocks per batch.

    Returns:
        List of raw log dictionaries from all batches.
    """
    if not pair_addresses:
        return []

    topic0_swap = get_swap_event_signature()
    topic0_mint = get_mint_event_signature()
    topic0_burn = get_burn_event_signature()
    topics = [topic0_swap, topic0_mint, topic0_burn]

    total_blocks = end_block - start_block + 1
    num_batches = (total_blocks + batch_size - 1) // batch_size
    all_logs = []

    print(f"Fetching Pair logs from block {start_block} to {end_block} ({total_blocks} blocks)")
    print(f"Pairs: {len(pair_addresses)}, batch size: {batch_size} blocks ({num_batches} batches)")

    with tqdm(total=num_batches, desc="Fetching Pair logs", unit="batch") as pbar:
        for batch_start in range(start_block, end_block + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, end_block)
            retry_count = 0
            max_retries = 3

            while retry_count < max_retries:
                try:
                    logs = w3.eth.get_logs({
                        'fromBlock': batch_start,
                        'toBlock': batch_end,
                        'address': pair_addresses,
                        'topics': [topics],
                    })
                    all_logs.extend(logs)
                    pbar.update(1)
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        print(f"\nError fetching logs for blocks {batch_start}-{batch_end}: {e}")
                        print("Max retries reached, skipping this batch")
                        pbar.update(1)
                        break
                    print(f"\nRetry {retry_count}/{max_retries} for blocks {batch_start}-{batch_end}")
                    time.sleep(2 ** retry_count)

    return all_logs


def index_pair_events(
    w3: Web3,
    config: dict,
    csv_path: str = 'data/uniswap_v2_pairs.csv',
) -> List[dict]:
    """
    Main indexing function: load pair addresses, fetch logs in batches, decode all events.

    Args:
        w3: Connected Web3 instance.
        config: Configuration dict with START_BLOCK, BLOCK_RANGE, BATCH_SIZE.
        csv_path: Path to CSV with pair_address column (default: data/uniswap_v2_pairs.csv).

    Returns:
        List of decoded Pair events (swap, mint, burn), each with event_type and type-specific fields.
    """
    pair_addresses = load_pair_addresses(csv_path)
    print(f"Loaded {len(pair_addresses)} pair addresses from {csv_path}")

    start_block = config['START_BLOCK']
    block_range = config['BLOCK_RANGE']
    batch_size = config['BATCH_SIZE']
    end_block = start_block + block_range - 1

    logs = fetch_pair_logs_in_batches(
        w3, pair_addresses, start_block, end_block, batch_size
    )
    print(f"\nFound {len(logs)} Pair events (Swap/Mint/Burn)")

    if not logs:
        return []

    events = []
    for log in tqdm(logs, desc="Decoding events", unit="event"):
        try:
            events.append(decode_pair_event(log))
        except Exception as e:
            print(f"\nError decoding event in tx {log.get('transactionHash', 'unknown')}: {e}")

    print(f"\nSuccessfully decoded {len(events)} Pair events")
    return events
