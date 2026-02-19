"""Command to index Uniswap V3 pools from Factory contract."""

from src.protocols.uniswap_v3.core.config import load_config
from src.protocols.uniswap_v3.core.rpc import get_web3
from src.protocols.uniswap_v3.indexers.factory_indexer import index_pools
from src.protocols.uniswap_v3.storage.csv_storage import save_pools_to_csv


def run():
    """Execute the pool indexing command."""
    print("=== Uniswap V3 Pool Indexer ===\n")
    
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
    
    # Index pools
    pools = index_pools(w3, config)
    
    # Save to CSV
    if pools:
        output_filename = 'uniswap_v3_pools.csv'
        save_pools_to_csv(pools, output_filename)
        print(f"\nIndexing complete! Found {len(pools)} pools")
    else:
        print("\nNo pools found in the specified block range")
