"""Main entry point for the Uniswap V2 indexer CLI."""

import sys


def main():
    """Main CLI dispatcher for commands."""
    # Get command from arguments, default to 'index-pairs'
    command = sys.argv[1] if len(sys.argv) > 1 else 'index-pairs'
    
    if command == 'index-pairs':
        from src.commands.index_pairs import run
        run()
    elif command == 'index-pair-events':
        from src.commands.index_pair_events import run
        run()
    elif command == 'help' or command == '--help' or command == '-h':
        print_help()
    else:
        print(f"Unknown command: {command}")
        print("Run 'python -m src.main help' for available commands")
        sys.exit(1)


def print_help():
    """Print available commands."""
    print("=== Uniswap V2 Indexer CLI ===\n")
    print("Available commands:")
    print("  index-pairs         Index Uniswap V2 pairs from Factory contract (default)")
    print("  index-pair-events   Index Pair events (Swap, Mint, Burn) from pairs CSV")
    print("  help                Show this help message")
    print("\nUsage:")
    print("  python -m src.main [command]")
    print("\nExamples:")
    print("  python -m src.main")
    print("  python -m src.main index-pairs")
    print("  python -m src.main index-pair-events")


if __name__ == "__main__":
    main()
