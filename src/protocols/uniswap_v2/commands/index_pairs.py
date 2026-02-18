"""Command to index Uniswap V2 pairs from Factory contract."""

from src.protocols.uniswap_v2.core.config import load_config
from src.protocols.uniswap_v2.core.rpc import get_web3
from src.protocols.uniswap_v2.indexers.factory_indexer import index_pairs
from src.protocols.uniswap_v2.storage.csv_storage import save_pairs_to_csv


def run():
    """Execute the pair indexing command."""
    print("=== Uniswap V2 Pair Indexer ===\n")
    
    # Load configuration
    print("Loading configuration...")
    config = load_config()
    print(f"Factory Address: {config['FACTORY_ADDRESS']}")
    print(f"Block Range: {config['START_BLOCK']} to {config['START_BLOCK'] + config['BLOCK_RANGE'] - 1}")
    print(f"Batch Size: {config['BATCH_SIZE']}\n")
    
    # Connect to RPC
    print(f"Connecting to RPC: {config['RPC_URL']}")
    w3 = get_web3(config['RPC_URL'])
    print("Successfully connected to RPC\n")
    
    # Index pairs
    pairs = index_pairs(w3, config)
    
    # Save to CSV
    if pairs:
        output_filename = 'uniswap_v2_pairs.csv'
        save_pairs_to_csv(pairs, output_filename)
        print(f"\nIndexing complete! Found {len(pairs)} pairs")
    else:
        print("\nNo pairs found in the specified block range")
