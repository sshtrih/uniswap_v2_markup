"""Command to index Uniswap V2 Pair events (Swap, Mint, Burn) from pairs CSV."""

from src.core.config import load_config
from src.core.rpc import get_web3
from src.indexers.pairs_indexer import index_pair_events
from src.storage.csv_storage import save_pair_events_to_csv


def run():
    """Execute the pair events indexing command."""
    print("=== Uniswap V2 Pair Events Indexer ===\n")

    print("Loading configuration...")
    config = load_config()
    print(f"Block Range: {config['START_BLOCK']} to {config['START_BLOCK'] + config['BLOCK_RANGE'] - 1}")
    print(f"Batch Size: {config['BATCH_SIZE']}\n")

    print(f"Connecting to RPC: {config['RPC_URL']}")
    w3 = get_web3(config['RPC_URL'])
    print("Successfully connected to RPC\n")

    events = index_pair_events(w3, config, csv_path="data/uniswap_v2_pairs.csv")

    if events:
        save_pair_events_to_csv(events, "uniswap_v2_pair_events.csv")
        swap_count = sum(1 for e in events if e.get("event_type") == "swap")
        mint_count = sum(1 for e in events if e.get("event_type") == "mint")
        burn_count = sum(1 for e in events if e.get("event_type") == "burn")
        print(f"\nSummary: {swap_count} Swap, {mint_count} Mint, {burn_count} Burn")
    else:
        print("\nNo Pair events found in the specified block range")
