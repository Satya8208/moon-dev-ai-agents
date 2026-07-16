"""
🥜 Nirvana Nuts Dashboard API
FastAPI backend for the growth engine
"""

import sys
import base64
import re
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.nirvana_nuts_agent import NirvanaNutsAgent
from src.agents.poker.poker_agent import PokerAgent
from src.agents.poker.core.hand_evaluator import Card
from src.agents.poker.core.poker_types import Position

app = FastAPI(
    title="Moon Dev AI Agents API",
    description="Unified API for Moon Dev Agents (Nirvana Nuts + Poker God)",
    version="1.1.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
agent = None  # Nirvana Nuts
poker_agent = None # Poker God

def get_agent():
    global agent
    if agent is None:
        agent = NirvanaNutsAgent()
    return agent

def get_poker_agent():
    global poker_agent
    if poker_agent is None:
        poker_agent = PokerAgent()
    return poker_agent


# Request/Response Models
class ReplyRequest(BaseModel):
    tweet: str

class PokerAdviceRequest(BaseModel):
    hole_cards: str  # "AhKh"
    board: str = ""  # "Kd 7c 2h"
    pot_size: float = 0.0
    bet_facing: float = 0.0
    position: str = "BTN"
    villain_range: Optional[str] = None

class ImageReplyRequest(BaseModel):
    image_data: str  # Base64 encoded image (can include data:image/... prefix)
    caption: str = ""  # Optional caption text

class ReplyOption(BaseModel):
    mode: str
    reply: str
    char_count: int

class AnalysisResult(BaseModel):
    tone: str
    assumptions: str
    angle: str
    recommended_mode: str
    why: str
    engagement_potential: str

class ReplyResponse(BaseModel):
    analysis: AnalysisResult
    replies: List[ReplyOption]

class ImageAnalysisResult(BaseModel):
    image_type: str
    visible_text: str
    description: str
    actual_message: str
    tone: str
    hook: str

class ImageReplyResponse(BaseModel):
    image_analysis: ImageAnalysisResult
    analysis: AnalysisResult
    replies: List[ReplyOption]

class TweetRequest(BaseModel):
    topic: Optional[str] = None
    count: int = 5

class TweetResponse(BaseModel):
    topic: str
    tweets: List[dict]

class ThreadRequest(BaseModel):
    topic: str
    length: int = 5
    thesis: Optional[str] = None

class ThreadResponse(BaseModel):
    topic: str
    tweets: List[dict]


# Endpoints
@app.get("/")
async def root():
    return {"message": "🥜 Nirvana Nuts Growth Engine API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/replies", response_model=ReplyResponse)
async def generate_replies(request: ReplyRequest):
    """Generate reply options for a tweet"""
    try:
        agent = get_agent()

        # Get analysis
        analysis = agent.analyze_tweet(request.tweet)

        # Generate replies for each mode
        modes = ["savage", "funny", "philosophical", "controversial", "nuclear"]
        replies = []

        for mode in modes:
            reply_text = agent.generate_reply(request.tweet, mode, analysis)
            replies.append({
                "mode": mode,
                "reply": reply_text,
                "char_count": len(reply_text)
            })

        return {
            "analysis": {
                "tone": analysis.get("tone", "unknown"),
                "assumptions": analysis.get("assumptions", "unknown"),
                "angle": analysis.get("angle", "unknown"),
                "recommended_mode": analysis.get("recommended_mode", "savage"),
                "why": analysis.get("why", ""),
                "engagement_potential": analysis.get("engagement_potential", "medium")
            },
            "replies": replies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/image-replies", response_model=ImageReplyResponse)
async def generate_image_replies(request: ImageReplyRequest):
    """Generate reply options for an image tweet"""
    try:
        agent = get_agent()
        print(f"[API] Processing image reply request with caption: {request.caption[:50]}..." if request.caption else "[API] Processing image reply (no caption)")

        # Parse the base64 image data
        image_data = request.image_data
        image_media_type = "image/png"  # Default

        # Handle data URL format (data:image/png;base64,...)
        if image_data.startswith("data:"):
            # Extract media type and base64 data
            match = re.match(r"data:(image/[^;]+);base64,(.+)", image_data)
            if match:
                image_media_type = match.group(1)
                image_data = match.group(2)
            else:
                # Try simpler format
                if ";base64," in image_data:
                    image_data = image_data.split(";base64,")[1]

        # Generate replies using the agent
        replies, analysis, image_analysis = agent.generate_replies_for_image(
            image_data=image_data,
            caption=request.caption,
            image_media_type=image_media_type
        )

        return {
            "image_analysis": {
                "image_type": image_analysis.get("image_type", "unknown"),
                "visible_text": image_analysis.get("visible_text", ""),
                "description": image_analysis.get("description", ""),
                "actual_message": image_analysis.get("actual_message", image_analysis.get("context", "")),
                "tone": image_analysis.get("tone", "unknown"),
                "hook": image_analysis.get("hook", "")
            },
            "analysis": {
                "tone": analysis.get("tone", "unknown"),
                "assumptions": analysis.get("assumptions", "unknown"),
                "angle": analysis.get("angle", "unknown"),
                "recommended_mode": analysis.get("recommended_mode", "savage"),
                "why": analysis.get("why", ""),
                "engagement_potential": analysis.get("engagement_potential", "medium")
            },
            "replies": [
                {"mode": r["mode"], "reply": r["reply"], "char_count": len(r["reply"])}
                for r in replies
            ]
        }
    except Exception as e:
        print(f"[API] Error generating image replies: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tweets", response_model=TweetResponse)
async def generate_tweets(request: TweetRequest):
    """Generate original tweet ideas"""
    try:
        agent = get_agent()
        print(f"[API] Generating {request.count} tweets on topic: {request.topic}")

        tweets = agent.generate_tweets(request.topic, request.count)

        if not tweets:
            print("[API] Warning: No tweets generated, returning empty list")
            tweets = []

        topic_used = request.topic or "random topic"

        result = {
            "topic": topic_used,
            "tweets": [{"text": t, "char_count": len(t)} for t in tweets if t]
        }
        print(f"[API] Returning {len(result['tweets'])} tweets")
        return result

    except Exception as e:
        print(f"[API] Error generating tweets: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/thread", response_model=ThreadResponse)
async def generate_thread(request: ThreadRequest):
    """Generate a Twitter thread"""
    try:
        agent = get_agent()
        print(f"[API] Generating {request.length}-tweet thread on: {request.topic}")

        thread = agent.generate_thread(request.topic, request.length, request.thesis)

        if not thread:
            print("[API] Warning: No thread generated")
            thread = []

        roles = ["HOOK"] + ["BODY"] * (len(thread) - 2) + ["CLOSER"] if len(thread) > 1 else ["HOOK"]

        result = {
            "topic": request.topic,
            "tweets": [
                {"text": t, "char_count": len(t), "role": roles[i] if i < len(roles) else "BODY"}
                for i, t in enumerate(thread) if t
            ]
        }
        print(f"[API] Returning {len(result['tweets'])} thread tweets")
        return result

    except Exception as e:
        print(f"[API] Error generating thread: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/poker/advice")
async def get_poker_advice(request: PokerAdviceRequest):
    """Get God Mode poker advice"""
    try:
        god = get_poker_agent()
        
        # Parse inputs
        cards = []
        if request.hole_cards:
            # Simple parser or use agent's internal
            # Assuming parse_cards is available or we implement simple logic
            # god.parse_cards is not exposed, let's just assume string passed to new_hand? 
            # No, new_hand expects List[Card].
            # We need to parse.
            from src.agents.poker.poker_agent import parse_cards
            cards = parse_cards(request.hole_cards)
            
        board = []
        if request.board:
            from src.agents.poker.poker_agent import parse_cards
            board = parse_cards(request.board)
            
        pos_enum = Position.BTN
        try:
            pos_enum = Position[request.position.upper()]
        except:
            pass
            
        # Update State
        god.new_hand(cards, pos_enum)
        god.set_board(board)
        god.set_pot(request.pot_size, request.bet_facing)
        
        if request.villain_range:
            god.set_villain_range(request.villain_range)
            
        # Get advice
        advice = god.get_postflop_advice()
        
        # Format response
        if advice:
            return {
                "decision": advice['decision'].action.value,
                "sizing": advice['decision'].sizing_fraction,
                "reasoning": advice['decision'].reasoning,
                "equity": advice.get('equity', {}).get('equity', 0),
                "hand_class": advice['hand_category'].value
            }
        return {"error": "Could not generate advice"}

    except Exception as e:
        print(f"[API] Poker Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
