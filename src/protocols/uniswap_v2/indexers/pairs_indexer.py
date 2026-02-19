"""Indexer for Uniswap V2 Pair events (Swap, Mint, Burn)."""

import os
import time
from typing import List

import pandas as pd
from web3 import Web3
from tqdm import tqdm

from src.protocols.uniswap_v2.decoders.event_decoder import (
    get_swap_event_signature,
    get_mint_event_signature,
    get_burn_event_signature,
    decode_pair_event,
)


def _tx_hash_hex(tx_hash) -> str:
    """Normalize transaction hash to hex string."""
    if isinstance(tx_hash, bytes):
        return tx_hash.hex()
    return tx_hash


def get_transaction_sender(w3: Web3, tx_hash: str, cache: dict, last_request_time: list) -> str:
    """
    Get transaction sender (from address) with caching, rate limiting, and retry.

    Args:
        w3: Connected Web3 instance
        tx_hash: Transaction hash (hex string)
        cache: Dictionary to cache transaction senders
        last_request_time: Single-element list [float] tracking last RPC call time

    Returns:
        str: Checksummed address of transaction sender (empty string on error)
    """
    if tx_hash in cache:
        return cache[tx_hash]

    max_retries = 5
    min_delay = 0.15

    for attempt in range(max_retries):
        elapsed = time.time() - last_request_time[0]
        if elapsed < min_delay:
            time.sleep(min_delay - elapsed)

        try:
            tx = w3.eth.get_transaction(tx_hash)
            last_request_time[0] = time.time()
            cache[tx_hash] = Web3.to_checksum_address(tx['from'])
            return cache[tx_hash]
        except Exception as e:
            last_request_time[0] = time.time()
            err = str(e)
            if '429' in err or 'Too Many Requests' in err or '-32603' in err or 'temporarily unavailable' in err:
                wait = 2 ** (attempt + 1)
                print(f"\n  Rate limited on tx {tx_hash[:18]}..., retry {attempt+1}/{max_retries} in {wait}s")
                time.sleep(wait)
                continue
            print(f"\nError fetching transaction {tx_hash}: {e}")
            cache[tx_hash] = ''
            return ''

    print(f"\nFailed to fetch tx {tx_hash} after {max_retries} retries")
    cache[tx_hash] = ''
    return ''


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


def _fetch_logs_with_retry(
    w3: Web3,
    pair_addresses: List[str],
    topics: List[str],
    batch_start: int,
    batch_end: int,
    max_retries: int = 3,
) -> List[dict]:
    """
    Fetch logs for a specific block range with retry and automatic range splitting.
    
    Args:
        w3: Connected Web3 instance
        pair_addresses: List of pair addresses
        topics: List of event topic signatures
        batch_start: Start block
        batch_end: End block
        max_retries: Maximum retry attempts
        
    Returns:
        List of log dictionaries
    """
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logs = w3.eth.get_logs({
                'fromBlock': batch_start,
                'toBlock': batch_end,
                'address': pair_addresses,
                'topics': [topics],
            })
            return logs
        except Exception as e:
            error_str = str(e)
            error_dict = e.args[0] if e.args and isinstance(e.args[0], dict) else {}
            
            # Check for -32005 error: too many results
            if '-32005' in error_str or (isinstance(error_dict, dict) and error_dict.get('code') == -32005):
                # Extract suggested range from error
                data = error_dict.get('data', {})
                if isinstance(data, dict) and 'from' in data and 'to' in data:
                    suggested_from = int(data['from'], 16) if isinstance(data['from'], str) else data['from']
                    suggested_to = int(data['to'], 16) if isinstance(data['to'], str) else data['to']
                    
                    # Split the range in half and recursively fetch
                    mid_block = (batch_start + batch_end) // 2
                    print(f"\nToo many results for blocks {batch_start}-{batch_end}, splitting at block {mid_block}")
                    
                    logs1 = _fetch_logs_with_retry(w3, pair_addresses, topics, batch_start, mid_block, max_retries)
                    logs2 = _fetch_logs_with_retry(w3, pair_addresses, topics, mid_block + 1, batch_end, max_retries)
                    return logs1 + logs2
                else:
                    # If no suggested range, split in half
                    mid_block = (batch_start + batch_end) // 2
                    if mid_block == batch_start:
                        # Can't split further, return empty
                        print(f"\nCannot split range {batch_start}-{batch_end} further, skipping")
                        return []
                    print(f"\nToo many results for blocks {batch_start}-{batch_end}, splitting at block {mid_block}")
                    logs1 = _fetch_logs_with_retry(w3, pair_addresses, topics, batch_start, mid_block, max_retries)
                    logs2 = _fetch_logs_with_retry(w3, pair_addresses, topics, mid_block + 1, batch_end, max_retries)
                    return logs1 + logs2
            
            # For other errors, retry with exponential backoff
            retry_count += 1
            if retry_count >= max_retries:
                print(f"\nError fetching logs for blocks {batch_start}-{batch_end}: {e}")
                return []
            print(f"\nRetry {retry_count}/{max_retries} for blocks {batch_start}-{batch_end}")
            time.sleep(2 ** retry_count)
    
    return []


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
    Automatically handles -32005 errors (too many results) by splitting ranges.
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
            
            logs = _fetch_logs_with_retry(w3, pair_addresses, topics, batch_start, batch_end)
            all_logs.extend(logs)
            pbar.update(1)

    return all_logs


def index_pair_events(
    w3: Web3,
    config: dict,
    csv_path: str = 'data/uniswap_v2/uniswap_v2_pairs.csv',
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
    tx_sender_cache = {}
    last_request_time = [0.0]

    print("Decoding events and fetching transaction senders...")
    for log in tqdm(logs, desc="Decoding events", unit="event"):
        try:
            event = decode_pair_event(log)
            tx_hash = _tx_hash_hex(log['transactionHash'])
            tx_from = get_transaction_sender(w3, tx_hash, tx_sender_cache, last_request_time)
            event['tx_from'] = tx_from
            events.append(event)
        except Exception as e:
            print(f"\nError decoding event in tx {log.get('transactionHash', 'unknown')}: {e}")

    print(f"\nSuccessfully decoded {len(events)} Pair events")
    return events
