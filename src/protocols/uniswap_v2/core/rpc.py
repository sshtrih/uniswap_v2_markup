"""RPC connection utilities for Web3."""

from web3 import Web3


def get_web3(rpc_url: str) -> Web3:
    """
    Create and return a Web3 instance connected to the specified RPC URL.
    
    Args:
        rpc_url: The RPC endpoint URL to connect to
        
    Returns:
        Web3: Connected Web3 instance
        
    Raises:
        ConnectionError: If unable to connect to the RPC endpoint
    """
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    # Some RPC providers may return False for is_connected() but still work
    # Try an actual RPC call to verify connection
    if not w3.is_connected():
        try:
            # Verify with actual RPC call
            w3.eth.block_number
        except Exception:
            raise ConnectionError(f"Failed to connect to RPC endpoint: {rpc_url}")
    
    return w3


def get_latest_block(w3: Web3) -> int:
    """
    Get the latest block number from the blockchain.
    
    Args:
        w3: Connected Web3 instance
        
    Returns:
        int: The latest block number
    """
    return w3.eth.block_number
