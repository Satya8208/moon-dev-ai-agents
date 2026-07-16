"""
Poker Advisor Web API
FastAPI backend connecting the web dashboard to the Poker God agent
Built with love by Moon Dev
"""

import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import poker agent components
from src.agents.poker.poker_agent import PokerAgent, GameMode, GameFormat, parse_cards
from src.agents.poker.core.hand_evaluator import Card
from src.agents.poker.strategy.preflop_engine import Position, FacingAction, PreflopAction
from src.agents.poker.strategy.postflop_engine import Street, PostflopAction

app = FastAPI(
    title="Poker Advisor API",
    description="Real-time poker strategy advice powered by Moon Dev's Poker God Agent",
    version="1.0.0"
)

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
static_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Global poker agent instance
poker_agent = PokerAgent(mode=GameMode.ADVISOR, game_format=GameFormat.CASH)

# Position mapping
POSITION_MAP = {
    'utg': Position.UTG,
    'utg1': Position.UTG1,
    'utg2': Position.UTG2,
    'mp': Position.MP,
    'mp2': Position.MP2,
    'hj': Position.HJ,
    'co': Position.CO,
    'btn': Position.BTN,
    'sb': Position.SB,
    'bb': Position.BB,
}

# Facing action mapping
FACING_MAP = {
    'unopened': FacingAction.UNOPENED,
    'limped': FacingAction.LIMPED,
    'raised': FacingAction.RAISED,
    'facing_raise': FacingAction.RAISED,
    '3bet': FacingAction.THREE_BET,
    'facing_3bet': FacingAction.THREE_BET,
    '4bet': FacingAction.FOUR_BET,
    'facing_4bet': FacingAction.FOUR_BET,
    '5bet': FacingAction.FIVE_BET,
    'all_in': FacingAction.ALL_IN,
}


# ===== Pydantic Models =====

class NewHandInput(BaseModel):
    hole_cards: str  # e.g., "AhKs"
    position: str = "btn"  # e.g., "btn", "co", "utg"


class BoardInput(BaseModel):
    cards: str  # e.g., "Kd7c2h"


class PotInput(BaseModel):
    pot_size: float
    bet_to_call: float = 0
    effective_stack: float = 100


class RangeInput(BaseModel):
    notation: str  # e.g., "22+,AKs,AQo+"


class PreflopRequest(BaseModel):
    facing: str = "unopened"
    raiser_position: Optional[str] = None


class PostflopRequest(BaseModel):
    in_position: bool = True


class EquityRequest(BaseModel):
    villain_range: str = ""
    iterations: int = 5000


class GTORequest(BaseModel):
    bet_size: Optional[float] = None


class AnalyzeRequest(BaseModel):
    hole_cards: str
    board: str = ""
    position: str = "btn"
    pot_size: float = 0
    bet_to_call: float = 0
    villain_range: str = ""
    facing: str = "unopened"
    effective_stack: float = 100


class ResultInput(BaseModel):
    won: bool
    amount: float


# ===== Helper Functions =====

def get_position(pos_str: str) -> Position:
    """Convert position string to Position enum"""
    return POSITION_MAP.get(pos_str.lower(), Position.BTN)


def get_facing_action(facing_str: str) -> FacingAction:
    """Convert facing action string to FacingAction enum"""
    return FACING_MAP.get(facing_str.lower(), FacingAction.UNOPENED)


def serialize_decision(decision) -> Dict[str, Any]:
    """Serialize a preflop/postflop decision to JSON-friendly dict"""
    if decision is None:
        return None

    result = {
        'action': decision.action.value if hasattr(decision.action, 'value') else str(decision.action),
        'reasoning': getattr(decision, 'reasoning', ''),
    }

    # Preflop decision fields
    if hasattr(decision, 'sizing') and decision.sizing is not None:
        result['sizing'] = decision.sizing
    if hasattr(decision, 'frequency'):
        result['frequency'] = decision.frequency
    if hasattr(decision, 'range_strength'):
        result['range_strength'] = decision.range_strength
    if hasattr(decision, 'alternative') and decision.alternative:
        result['alternative'] = decision.alternative.value
        result['alt_frequency'] = decision.alt_frequency

    # Postflop decision fields
    if hasattr(decision, 'sizing_fraction') and decision.sizing_fraction is not None:
        result['sizing_fraction'] = decision.sizing_fraction
        result['sizing_percent'] = int(decision.sizing_fraction * 100)

    return result


# ===== API Endpoints =====

@app.get("/")
async def root():
    """Serve the dashboard"""
    return FileResponse(static_dir / "index.html")


@app.post("/api/poker/new_hand")
async def new_hand(input: NewHandInput):
    """Start a new hand with hole cards and position"""
    try:
        cards = parse_cards(input.hole_cards)
        position = get_position(input.position)
        poker_agent.new_hand(cards, position)

        return {
            "success": True,
            "hole_cards": input.hole_cards,
            "position": position.name,
            "message": f"New hand started: {input.hole_cards} from {position.name}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/poker/set_board")
async def set_board(input: BoardInput):
    """Set the board cards (flop/turn/river)"""
    try:
        if input.cards.strip():
            cards = parse_cards(input.cards)
            poker_agent.set_board(cards)
            street = "PREFLOP"
            if len(cards) == 3:
                street = "FLOP"
            elif len(cards) == 4:
                street = "TURN"
            elif len(cards) == 5:
                street = "RIVER"
        else:
            poker_agent.hand_state.board = []
            street = "PREFLOP"

        return {
            "success": True,
            "board": input.cards,
            "street": street,
            "num_cards": len(poker_agent.hand_state.board)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/poker/set_pot")
async def set_pot(input: PotInput):
    """Set pot size, bet to call, and effective stack"""
    try:
        poker_agent.set_pot(input.pot_size, input.bet_to_call)
        poker_agent.hand_state.effective_stack = input.effective_stack

        return {
            "success": True,
            "pot_size": input.pot_size,
            "bet_to_call": input.bet_to_call,
            "effective_stack": input.effective_stack
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/poker/set_villain_range")
async def set_villain_range(input: RangeInput):
    """Set villain's estimated range"""
    try:
        poker_agent.set_villain_range(input.notation)

        # Get range percentage
        range_obj = poker_agent.hand_state.villain_range
        range_percent = len(range_obj.hands) / 1326 * 100 if range_obj else 0

        return {
            "success": True,
            "notation": input.notation,
            "range_percent": round(range_percent, 1),
            "num_combos": len(range_obj.hands) if range_obj else 0
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/poker/preflop_advice")
async def get_preflop_advice(request: PreflopRequest):
    """Get preflop recommendation"""
    try:
        facing = get_facing_action(request.facing)
        raiser_pos = get_position(request.raiser_position) if request.raiser_position else None

        decision = poker_agent.get_preflop_advice(facing, raiser_pos)

        return {
            "success": True,
            "decision": serialize_decision(decision),
            "position": poker_agent.hand_state.position.name,
            "facing": facing.value
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/poker/postflop_advice")
async def get_postflop_advice(request: PostflopRequest):
    """Get postflop recommendation"""
    try:
        result = poker_agent.get_postflop_advice(in_position=request.in_position)

        if result is None:
            return {
                "success": False,
                "error": "Need hole cards and board to analyze"
            }

        # Serialize the complex result
        response = {
            "success": True,
            "decision": serialize_decision(result['decision']),
            "hand_category": result['hand_category'].value if result.get('hand_category') else None,
            "hand_description": result['hand_result'].description if result.get('hand_result') else None,
            "board_texture": result['board_analysis'].texture.value if result.get('board_analysis') else None,
        }

        if result.get('equity'):
            response['equity'] = {
                'equity': round(result['equity']['equity'] * 100, 1),
                'win_rate': round(result['equity']['win_rate'] * 100, 1),
                'tie_rate': round(result['equity']['tie_rate'] * 100, 1)
            }

        # Add draws if present
        if result.get('board_analysis') and result['board_analysis'].draws:
            response['draws'] = [d.draw_type.value for d in result['board_analysis'].draws[:3]]

        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/poker/equity")
async def calculate_equity(request: EquityRequest):
    """Calculate equity vs a range"""
    try:
        result = poker_agent.get_equity(
            villain_range_str=request.villain_range if request.villain_range else None,
            iterations=request.iterations
        )

        if 'error' in result:
            return {"success": False, "error": result['error']}

        return {
            "success": True,
            "equity": round(result['equity'] * 100, 1),
            "win_rate": round(result['win_rate'] * 100, 1),
            "tie_rate": round(result['tie_rate'] * 100, 1),
            "loss_rate": round(result['loss_rate'] * 100, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/poker/pot_odds")
async def get_pot_odds():
    """Get pot odds analysis"""
    try:
        result = poker_agent.get_pot_odds()

        if 'error' in result:
            return {"success": False, "error": result['error']}

        return {
            "success": True,
            "pot_odds": round(result['pot_odds'] * 100, 1),
            "pot_odds_ratio": result['ratio'],
            "break_even_equity": round(result['break_even_equity'] * 100, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/poker/gto_metrics")
async def get_gto_metrics(request: GTORequest):
    """Get GTO metrics (MDF, alpha, bluff frequency)"""
    try:
        result = poker_agent.get_gto_metrics(bet_size=request.bet_size)

        return {
            "success": True,
            "mdf": round(result['mdf'] * 100, 1),
            "alpha": round(result['alpha'] * 100, 1),
            "bluff_freq": round(result['bluff_freq'] * 100, 1)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/poker/analyze")
async def analyze_full_state(request: AnalyzeRequest):
    """Full analysis - combines multiple endpoints for efficiency"""
    try:
        # Set up the hand state
        cards = parse_cards(request.hole_cards)
        position = get_position(request.position)
        poker_agent.new_hand(cards, position)

        # Set board if provided
        if request.board.strip():
            board_cards = parse_cards(request.board)
            poker_agent.set_board(board_cards)

        # Set pot
        poker_agent.set_pot(request.pot_size, request.bet_to_call)
        poker_agent.hand_state.effective_stack = request.effective_stack

        # Set villain range if provided
        if request.villain_range.strip():
            poker_agent.set_villain_range(request.villain_range)

        # Determine street
        board_len = len(poker_agent.hand_state.board)
        street = "PREFLOP" if board_len == 0 else ("FLOP" if board_len == 3 else ("TURN" if board_len == 4 else "RIVER"))

        response = {
            "success": True,
            "street": street,
            "position": position.name,
        }

        # Get advice based on street
        if street == "PREFLOP":
            facing = get_facing_action(request.facing)
            decision = poker_agent.get_preflop_advice(facing)
            response['decision'] = serialize_decision(decision)
            response['facing'] = facing.value
        else:
            result = poker_agent.get_postflop_advice(in_position=True)
            if result:
                response['decision'] = serialize_decision(result['decision'])
                response['hand_category'] = result['hand_category'].value if result.get('hand_category') else None
                response['hand_description'] = result['hand_result'].description if result.get('hand_result') else None
                response['board_texture'] = result['board_analysis'].texture.value if result.get('board_analysis') else None

                if result.get('board_analysis') and result['board_analysis'].draws:
                    response['draws'] = [d.draw_type.value for d in result['board_analysis'].draws[:3]]

        # Calculate equity if we have a villain range or board
        if request.villain_range.strip() or board_len > 0:
            try:
                eq_result = poker_agent.get_equity(
                    villain_range_str=request.villain_range if request.villain_range.strip() else None,
                    iterations=3000
                )
                if 'error' not in eq_result:
                    response['equity'] = {
                        'equity': round(eq_result['equity'] * 100, 1),
                        'win_rate': round(eq_result['win_rate'] * 100, 1),
                        'tie_rate': round(eq_result['tie_rate'] * 100, 1)
                    }
            except:
                pass

        # Calculate pot odds if there's a bet to call
        if request.bet_to_call > 0:
            try:
                odds_result = poker_agent.get_pot_odds()
                if 'error' not in odds_result:
                    response['pot_odds'] = {
                        'pot_odds': round(odds_result['pot_odds'] * 100, 1),
                        'ratio': odds_result['ratio'],
                        'break_even': round(odds_result['break_even_equity'] * 100, 1)
                    }
            except:
                pass

        # Calculate GTO metrics if we have pot info
        if request.pot_size > 0:
            try:
                gto_result = poker_agent.get_gto_metrics()
                response['gto_metrics'] = {
                    'mdf': round(gto_result['mdf'] * 100, 1),
                    'alpha': round(gto_result['alpha'] * 100, 1),
                    'bluff_freq': round(gto_result['bluff_freq'] * 100, 1)
                }
            except:
                pass

        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/poker/record_result")
async def record_result(input: ResultInput):
    """Record hand result (win/loss)"""
    try:
        poker_agent.record_result(input.won, input.amount)

        return {
            "success": True,
            "won": input.won,
            "amount": input.amount,
            "session_profit": poker_agent.session_stats.total_profit
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/poker/session_stats")
async def get_session_stats():
    """Get session statistics"""
    stats = poker_agent.session_stats

    return {
        "success": True,
        "hands_played": stats.hands_played,
        "hands_won": stats.hands_won,
        "win_rate": round(stats.win_rate * 100, 1),
        "total_profit": round(stats.total_profit, 2),
        "bb_per_100": round(stats.bb_per_100, 1),
        "biggest_pot_won": stats.biggest_pot_won,
        "biggest_pot_lost": stats.biggest_pot_lost,
        "vpip": stats.vpip,
        "pfr": stats.pfr,
        "three_bet": stats.three_bet
    }


@app.post("/api/poker/reset_session")
async def reset_session():
    """Reset session statistics"""
    global poker_agent
    poker_agent = PokerAgent(mode=GameMode.ADVISOR, game_format=GameFormat.CASH)

    return {
        "success": True,
        "message": "Session reset"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "poker-advisor"}


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("  POKER ADVISOR WEB DASHBOARD")
    print("  Built with love by Moon Dev")
    print("=" * 50)
    print("\n  Open http://localhost:8001 in your browser\n")
    print("=" * 50 + "\n")

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
