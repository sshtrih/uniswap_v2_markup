"""Main entry point for the multi-protocol indexer CLI."""

import argparse
import os
import sys

# Протоколы с командами index-pairs и index-pair-events
PROTOCOLS = ('uniswap_v2', 'uniswap_v3')


def main():
    """Main CLI dispatcher for commands."""
    parser = argparse.ArgumentParser(
        description='Multi-protocol blockchain indexer CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-p', '--protocol',
        default='uniswap_v2',
        choices=PROTOCOLS,
        help=f'Protocol to use (default: uniswap_v2). Available: {", ".join(PROTOCOLS)}'
    )
    parser.add_argument(
        'command',
        nargs='?',
        default='index-pairs',
        choices=['index-pairs', 'index-pair-events', 'help'],
        help='Command to execute (default: index-pairs)'
    )
    
    args = parser.parse_args()

    if args.command == 'help':
        print_help()
        return
    
    # Проверяем существование модуля протокола перед импортом
    import_path = f'src.protocols.{args.protocol}.commands'
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    commands_dir = os.path.join(project_root, 'src', 'protocols', args.protocol, 'commands')

    if not os.path.isdir(commands_dir):
        print(f"Error: Protocol '{args.protocol}' is not fully implemented.")
        print(f"Missing directory: {commands_dir}")
        print(f"Available protocols: {', '.join([p for p in PROTOCOLS if os.path.isdir(os.path.join(project_root, 'src', 'protocols', p, 'commands'))])}")
        sys.exit(1)
    
    # Динамически загружаем модуль протокола
    if args.command == 'index-pairs':
        mod = __import__(f'{import_path}.index_pairs', fromlist=('run',))
        mod.run()
    elif args.command == 'index-pair-events':
        mod = __import__(f'{import_path}.index_pair_events', fromlist=('run',))
        mod.run()
    else:
        parser.print_help()
        sys.exit(1)


def print_help():
    """Print available commands."""
    print("=== Multi-Protocol Indexer CLI ===\n")
    print("Options:")
    print("  -p, --protocol NAME   Protocol to use (default: uniswap_v2)")
    print(f"                       Available: {', '.join(PROTOCOLS)}")
    print("\nCommands:")
    print("  index-pairs           Index pairs from Factory contract")
    print("  index-pair-events     Index pair events (Swap, Mint, Burn) from pairs CSV")
    print("  help                  Show this help message")
    print("\nUsage:")
    print("  python -m src.main [-p PROTOCOL] [command]")
    print("\nExamples:")
    print("  python -m src.main index-pairs")
    print("  python -m src.main --protocol uniswap_v2 index-pairs")
    print("  python -m src.main -p uniswap_v2 index-pair-events")


if __name__ == "__main__":
    main()
