"""Indexer for Uniswap V2 Factory PairCreated events."""

import time
from typing import List, Dict
from web3 import Web3
from tqdm import tqdm

from src.protocols.uniswap_v2.decoders.event_decoder import get_paircreated_event_signature, decode_paircreated_event


def fetch_logs_in_batches(
    w3: Web3,
    factory_address: str,
    start_block: int,
    end_block: int,
    batch_size: int
) -> List[dict]:
    """
    Fetch PairCreated event logs in batches to avoid RPC limits.
    
    Args:
        w3: Connected Web3 instance
        factory_address: Uniswap V2 Factory contract address
        start_block: Starting block number
        end_block: Ending block number
        batch_size: Number of blocks per batch
        
    Returns:
        List[dict]: List of raw log dictionaries
    """
    event_signature = get_paircreated_event_signature()
    all_logs = []
    
    # Calculate number of batches
    total_blocks = end_block - start_block + 1
    num_batches = (total_blocks + batch_size - 1) // batch_size
    
    print(f"Fetching logs from block {start_block} to {end_block} ({total_blocks} blocks)")
    print(f"Using batch size: {batch_size} blocks ({num_batches} batches)")
    
    # Fetch logs in batches with progress bar
    with tqdm(total=num_batches, desc="Fetching logs", unit="batch") as pbar:
        for batch_start in range(start_block, end_block + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, end_block)
            
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    # Fetch logs for this batch
                    logs = w3.eth.get_logs({
                        'fromBlock': batch_start,
                        'toBlock': batch_end,
                        'address': Web3.to_checksum_address(factory_address),
                        'topics': [event_signature]
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
                    else:
                        print(f"\nRetry {retry_count}/{max_retries} for blocks {batch_start}-{batch_end}")
                        time.sleep(2 ** retry_count)  # Exponential backoff
    
    return all_logs


def get_block_timestamp(w3: Web3, block_number: int, cache: dict) -> int:
    """
    Get timestamp for a block with caching.
    
    Args:
        w3: Connected Web3 instance
        block_number: Block number to get timestamp for
        cache: Dictionary to cache timestamps
        
    Returns:
        int: Unix timestamp of the block
    """
    if block_number not in cache:
        try:
            block = w3.eth.get_block(block_number)
            cache[block_number] = block['timestamp']
        except Exception as e:
            print(f"Error fetching block {block_number}: {e}")
            cache[block_number] = 0
    
    return cache[block_number]


def index_pairs(w3: Web3, config: dict) -> List[dict]:
    """
    Index Uniswap V2 pairs from Factory contract events.
    
    Args:
        w3: Connected Web3 instance
        config: Configuration dictionary with keys:
            - FACTORY_ADDRESS: Factory contract address
            - START_BLOCK: Starting block number
            - BLOCK_RANGE: Number of blocks to index
            - BATCH_SIZE: Batch size for log requests
            
    Returns:
        List[dict]: List of decoded pair data with timestamps
    """
    factory_address = config['FACTORY_ADDRESS']
    start_block = config['START_BLOCK']
    block_range = config['BLOCK_RANGE']
    batch_size = config['BATCH_SIZE']
    
    end_block = start_block + block_range - 1
    
    # Fetch logs in batches
    logs = fetch_logs_in_batches(w3, factory_address, start_block, end_block, batch_size)
    
    print(f"\nFound {len(logs)} PairCreated events")
    
    if not logs:
        return []
    
    # Decode events
    pairs = []
    timestamp_cache = {}
    
    print("Decoding events and fetching timestamps...")
    with tqdm(total=len(logs), desc="Processing events", unit="event") as pbar:
        for log in logs:
            try:
                # Decode the event
                pair_data = decode_paircreated_event(log)
                
                # Add timestamp
                timestamp = get_block_timestamp(w3, pair_data['block_number'], timestamp_cache)
                pair_data['timestamp'] = timestamp
                
                pairs.append(pair_data)
                
            except Exception as e:
                print(f"\nError decoding event in tx {log.get('transactionHash', 'unknown')}: {e}")
            
            pbar.update(1)
    
    print(f"\nSuccessfully decoded {len(pairs)} pairs")
    
    return pairs
