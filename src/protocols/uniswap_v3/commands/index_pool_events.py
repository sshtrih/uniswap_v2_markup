"""Command to index Uniswap V3 Pool events (Initialize, Mint, Burn, Collect, Swap, Flash) from pools CSV."""

from src.protocols.uniswap_v3.core.rpc import get_web3
from src.protocols.uniswap_v3.indexers.pools_indexer import index_pool_events
from src.protocols.uniswap_v3.core.config import load_config
from src.protocols.uniswap_v3.storage.csv_storage import save_pool_events_to_csv


def run():
    """Execute the pool events indexing command."""
    print("=== Uniswap V3 Pool Events Indexer ===\n")

    print("Loading configuration...")
    config = load_config()
    print(f"Block Range: {config['START_BLOCK']} to {config['START_BLOCK'] + config['BLOCK_RANGE'] - 1}")
    print(f"Batch Size: {config['BATCH_SIZE']}\n")

    print(f"Connecting to RPC: {config['RPC_URL']}")
    w3 = get_web3(config['RPC_URL'])
    print("Successfully connected to RPC\n")

    events = index_pool_events(w3, config, csv_path="data/uniswap_v3/uniswap_v3_pools.csv")

    if events:
        save_pool_events_to_csv(events, "uniswap_v3_pool_events.csv")
        initialize_count = sum(1 for e in events if e.get("event_type") == "initialize")
        mint_count = sum(1 for e in events if e.get("event_type") == "mint")
        burn_count = sum(1 for e in events if e.get("event_type") == "burn")
        collect_count = sum(1 for e in events if e.get("event_type") == "collect")
        swap_count = sum(1 for e in events if e.get("event_type") == "swap")
        flash_count = sum(1 for e in events if e.get("event_type") == "flash")
        print(f"\nSummary: {initialize_count} Initialize, {mint_count} Mint, {burn_count} Burn, "
              f"{collect_count} Collect, {swap_count} Swap, {flash_count} Flash")
    else:
        print("\nNo Pool events found in the specified block range")
