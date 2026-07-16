#!/usr/bin/env python3
"""
Crypto Polymarket Trading Agent - CLI Runner

Usage:
    python scripts/run_crypto_polymarket.py --mode dry_run
    python scripts/run_crypto_polymarket.py --mode paper --cycles 10
    python scripts/run_crypto_polymarket.py --mode live --interval 600

Built with love by Moon Dev
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def print_banner():
    """Print startup banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🌙 CRYPTO POLYMARKET TRADING AGENT 🌙                       ║
    ║                                                               ║
    ║   Built with love by Moon Dev                                 ║
    ║                                                               ║
    ║   Features:                                                   ║
    ║   • Multi-signal aggregation (Whale, Liquidation, Funding)    ║
    ║   • AI Swarm consensus (Claude, GPT, DeepSeek, Grok)          ║
    ║   • Polymarket prediction market trading                      ║
    ║   • Risk management & position tracking                       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_environment():
    """Check required environment variables."""
    required = []
    optional = [
        ("ANTHROPIC_KEY", "Claude AI models"),
        ("OPENAI_API_KEY", "GPT-4 models"),
        ("DEEPSEEK_KEY", "DeepSeek models"),
        ("XAI_API_KEY", "Grok models"),
        ("MOONDEV_API_KEY", "MoonDev market data API"),
        ("POLYMARKET_PRIVATE_KEY", "Polymarket trading (live mode only)"),
    ]

    print("\n📋 Environment Check:\n")

    all_ok = True
    for var, desc in optional:
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"   ✅ {var}: {masked} ({desc})")
        else:
            print(f"   ⚠️  {var}: Not set ({desc})")
            if var in ["ANTHROPIC_KEY", "MOONDEV_API_KEY"]:
                all_ok = False

    print()
    return all_ok


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Crypto Polymarket Trading Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run mode (no actual trades, logs only)
  python scripts/run_crypto_polymarket.py --mode dry_run

  # Paper trading mode (simulated trades with paper balance)
  python scripts/run_crypto_polymarket.py --mode paper --cycles 10

  # Live trading mode (real trades on Polymarket)
  python scripts/run_crypto_polymarket.py --mode live --interval 600

  # Run a single cycle for testing
  python scripts/run_crypto_polymarket.py --mode dry_run --cycles 1

  # Show current status
  python scripts/run_crypto_polymarket.py --status
        """
    )

    parser.add_argument(
        "--mode",
        choices=["dry_run", "paper", "live"],
        default="dry_run",
        help="Execution mode (default: dry_run)"
    )

    parser.add_argument(
        "--cycles",
        type=int,
        default=0,
        help="Number of cycles to run (0 = infinite, default: 0)"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Cycle interval in seconds (default: 300)"
    )

    parser.add_argument(
        "--status",
        action="store_true",
        help="Print current status and exit"
    )

    parser.add_argument(
        "--no-banner",
        action="store_true",
        help="Skip startup banner"
    )

    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.70,
        help="Minimum swarm confidence to trade (default: 0.70)"
    )

    parser.add_argument(
        "--max-exposure",
        type=float,
        default=50000,
        help="Maximum total USD exposure (default: 50000)"
    )

    args = parser.parse_args()

    # Print banner
    if not args.no_banner:
        print_banner()

    # Check environment
    env_ok = check_environment()

    if not env_ok:
        print("⚠️  Some recommended environment variables are not set.")
        print("   The agent may have limited functionality.\n")

    # Import after path setup
    from src.agents.crypto_polymarket.config import CryptoPolymarketConfig, ExecutionMode
    from src.agents.crypto_polymarket.orchestrator import CryptoPolymarketOrchestrator

    # Create config
    config = CryptoPolymarketConfig(
        execution_mode=ExecutionMode(args.mode),
        cycle_interval_seconds=args.interval,
        min_confidence_threshold=args.min_confidence,
        max_total_exposure_usd=args.max_exposure,
    )

    # Create orchestrator
    orchestrator = CryptoPolymarketOrchestrator(config)

    # Handle status request
    if args.status:
        orchestrator.print_status()
        return

    # Warn about live mode
    if args.mode == "live":
        print("\n" + "="*60)
        print("⚠️  WARNING: LIVE TRADING MODE")
        print("="*60)
        print("\nYou are about to run the agent in LIVE mode.")
        print("This will execute REAL trades on Polymarket using your funds.")
        print("\nCurrent settings:")
        print(f"   Max Exposure: ${args.max_exposure:,.0f}")
        print(f"   Min Confidence: {args.min_confidence:.0%}")
        print(f"   Cycle Interval: {args.interval}s")
        print()

        confirm = input("Type 'CONFIRM' to proceed: ")
        if confirm != "CONFIRM":
            print("\n❌ Aborted - live trading not confirmed\n")
            return

    # Run the agent
    try:
        asyncio.run(orchestrator.run(cycles=args.cycles))
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")


if __name__ == "__main__":
    main()
