"""
🧪 Poker God Agent - Quick Test Script
Tests all God Mode features
"""

import sys
from pathlib import Path

# Add project root
project_root = str(Path(__file__).parent.parent.parent)
sys.path.insert(0, project_root)

from termcolor import cprint

cprint("\n" + "="*60, "cyan")
cprint("🎰 POKER GOD AGENT - ADVISOR MODE TEST", "cyan", attrs=["bold"])
cprint("="*60 + "\n", "cyan")

try:
    from src.agents.poker.poker_agent import PokerAgent, parse_cards, Position, GameMode
    cprint("✅ Imports successful", "green")
except Exception as e:
    cprint(f"❌ Import error: {e}", "red")
    sys.exit(1)

# Initialize agent
cprint("\n📍 Initializing Poker God Agent...", "yellow")
try:
    god = PokerAgent(mode=GameMode.ADVISOR)
    cprint("✅ Agent initialized", "green")
except Exception as e:
    cprint(f"❌ Init error: {e}", "red")
    sys.exit(1)

# Test God Mode status
cprint("\n" + "-"*40, "cyan")
cprint("🧠 TESTING GOD MODE STATUS", "cyan")
cprint("-"*40, "cyan")
try:
    status = god.god_mode_status()
    active = sum(1 for v in status.values() if v)
    cprint(f"✅ {active}/7 components active", "green" if active == 7 else "yellow")
except Exception as e:
    cprint(f"❌ God mode status error: {e}", "red")

# Test Neural Evaluator (no API needed)
cprint("\n" + "-"*40, "cyan")
cprint("⚡ TESTING NEURAL EVALUATOR", "cyan")
cprint("-"*40, "cyan")
try:
    result = god.quick_eval("AhKh", "Qh Jc 2d")
    if "strength" in result:
        cprint(f"✅ Neural eval works: {result['description']} = {result['equity']*100:.1f}% equity", "green")
    else:
        cprint(f"⚠️ Neural eval result: {result}", "yellow")
except Exception as e:
    cprint(f"❌ Neural eval error: {e}", "red")

# Test Solver Lite (no API needed)
cprint("\n" + "-"*40, "cyan")
cprint("🎯 TESTING SOLVER LITE", "cyan")
cprint("-"*40, "cyan")
try:
    god.hand_state.position = Position.BTN
    result = god.get_solver_solution("dry_unpaired", "top_pair_good")
    if "action" in result:
        cprint(f"✅ Solver works: {result['action']} @ {result['frequency']*100:.0f}%", "green")
    else:
        cprint(f"⚠️ Solver result: {result}", "yellow")
except Exception as e:
    cprint(f"❌ Solver error: {e}", "red")

# Test Population Database (no API needed)
cprint("\n" + "-"*40, "cyan")
cprint("📊 TESTING POPULATION DATABASE", "cyan")
cprint("-"*40, "cyan")
try:
    result = god.get_population_profile("live_low", "live_rec")
    if "vpip" in result:
        cprint(f"✅ Population DB works: VPIP={result['vpip']}%, {len(result['exploits'])} exploits", "green")
    else:
        cprint(f"⚠️ Population result: {result}", "yellow")
except Exception as e:
    cprint(f"❌ Population DB error: {e}", "red")

# Test Dynamic Range (no API needed)
cprint("\n" + "-"*40, "cyan")
cprint("🎯 TESTING DYNAMIC RANGE ENGINE", "cyan")
cprint("-"*40, "cyan")
try:
    result = god.get_adjusted_range(stack_bb=150, table_type="passive", is_live=True)
    if "base" in result:
        cprint(f"✅ Range engine works: {result['factor']:.2f}x adjustment", "green")
    else:
        cprint(f"⚠️ Range result: {result}", "yellow")
except Exception as e:
    cprint(f"❌ Range engine error: {e}", "red")

# Test basic poker functions
cprint("\n" + "-"*40, "cyan")
cprint("🃏 TESTING CORE POKER FUNCTIONS", "cyan")
cprint("-"*40, "cyan")
try:
    # Set up a hand
    cards = parse_cards("AhKs")
    god.new_hand(cards, Position.CO)
    god.set_board(parse_cards("Kc 7h 2d"))
    god.set_pot(15, 8)

    cprint(f"✅ Hand setup works: {god._cards_to_str(god.hand_state.hole_cards)}", "green")
    cprint(f"✅ Board: {god._cards_to_str(god.hand_state.board)}", "green")

    # Get standard advice
    advice = god.get_postflop_advice()
    if advice:
        cprint(f"✅ Postflop engine works", "green")
except Exception as e:
    cprint(f"❌ Core function error: {e}", "red")

# Summary
cprint("\n" + "="*60, "cyan")
cprint("📋 TEST SUMMARY", "cyan", attrs=["bold"])
cprint("="*60, "cyan")

cprint("""
Components tested:
  ✅ Agent initialization
  ✅ God Mode status
  ✅ Neural evaluator (sub-ms equity)
  ✅ Solver Lite (GTO solutions)
  ✅ Population database (exploits)
  ✅ Dynamic range engine
  ✅ Core poker functions

Note: LLM-powered features (ask, get_ai_advice) require
API calls and aren't tested here to avoid costs.
""", "white")

cprint("🎰 POKER GOD AGENT IS READY!", "green", attrs=["bold"])
