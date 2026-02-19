"""Main entry point for the multi-protocol indexer CLI."""

import argparse
import importlib
import sys

from pathlib import Path


PROTOCOLS = ('uniswap_v2', 'uniswap_v3')

COMMANDS = ('index-pairs', 'index-pair-events', 'index-pools', 'index-pool-events', 'help')
COMMAND_TO_MODULE = {
    'index-pairs': 'index_pairs',
    'index-pair-events': 'index_pair_events',
    'index-pools': 'index_pools',
    'index-pool-events': 'index_pool_events',
}


def _project_root() -> Path:
    """Root directory of the project (parent of src/)."""
    return Path(__file__).resolve().parent.parent


def _commands_dir(protocol: str) -> Path:
    """Path to protocol's commands directory."""
    return _project_root() / 'src' / 'protocols' / protocol / 'commands'


def _available_protocols() -> list[str]:
    """Protocols that have a commands/ directory implemented."""
    return [p for p in PROTOCOLS if _commands_dir(p).is_dir()]


def main():
    """Main CLI dispatcher for commands."""
    parser = argparse.ArgumentParser(
        description='Multi-protocol blockchain indexer CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-p', '--protocol',
        nargs='?',
        default='uniswap_v2',
        choices=PROTOCOLS,
        help=f'Protocol to use (default: uniswap_v2). Available: {", ".join(PROTOCOLS)}'
    )
    parser.add_argument(
        'command',
        nargs='?',
        default='index-pairs',
        choices=COMMANDS,
        help='Command to execute (default: index-pairs)'
    )

    args = parser.parse_args()

    if args.command == 'help':
        print_help()
        return

    commands_dir = _commands_dir(args.protocol)
    if not commands_dir.is_dir():
        print(f"Error: Protocol '{args.protocol}' is not fully implemented.")
        print(f"Missing directory: {commands_dir}")
        print(f"Available protocols: {', '.join(_available_protocols())}")
        sys.exit(1)

    module_name = COMMAND_TO_MODULE[args.command]
    import_path = f'src.protocols.{args.protocol}.commands.{module_name}'
    mod = importlib.import_module(import_path)
    mod.run()


def print_help():
    """Print available commands."""
    print("=== Multi-Protocol Indexer CLI ===\n")
    print("Options:")
    print("  -p, --protocol NAME   Protocol to use (default: uniswap_v2)")
    print(f"                       Available: {', '.join(PROTOCOLS)}")
    print("\nCommands:")
    print("  index-pairs           Index pairs from Factory contract (V2)")
    print("  index-pair-events     Index pair events (Swap, Mint, Burn) from pairs CSV (V2)")
    print("  index-pools           Index pools from Factory contract (V3)")
    print("  index-pool-events     Index pool events (Initialize, Mint, Burn, Collect, Swap, Flash) from pools CSV (V3)")
    print("  help                  Show this help message")
    print("\nUsage:")
    print("  python -m src.main [-p PROTOCOL] [command]")
    print("\nExamples:")
    print("  python -m src.main index-pairs")
    print("  python -m src.main --protocol uniswap_v2 index-pairs")
    print("  python -m src.main -p uniswap_v2 index-pair-events")


if __name__ == "__main__":
    main()
