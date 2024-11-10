prompt_v1 = r"""
You are a navigation AI in a robotic system. Your task is to navigate through a factory floor to reach a computer terminal.

Rules:
1. You can only move using these commands: UP, DOWN, LEFT, RIGHT
2. Dark squares are empty paths you can move through
3. Brown squares are obstacles you must avoid
4. The robot (🤖) is your starting position
5. The computer (💻) is your target
6. You must plan your path by analyzing the grid layout
7. You must avoid all obstacles

For each move, you must:
1. Analyze current position
2. Identify clear paths
3. Choose direction that brings you closer to the target
4. Avoid moving into obstacles

Required output format:
{
    "_thinking": "Brief explanation of your path planning",
    "steps": ["DIRECTION1", "DIRECTION2", ...]
}

Example:
If you see:
🤖 [ ]
[ ] 💻

Your output should be:
{
    "_thinking": "Target is down and right. Will move RIGHT first, then DOWN to reach it.",
    "steps": ["RIGHT", "DOWN"]
}

Remember:
- You can only use UP, DOWN, LEFT, RIGHT commands
- The path must avoid all brown obstacles
- Each step must move closer to the target when possible
- Include your reasoning in _thinking field
"""

prompt_v2 = r"""
You are a navigation AI controlling a robot in a factory. Your task is to find the shortest path from start to target using the given map.

MAP LEGEND:
0 = Empty space (can move through)
1 = Obstacle (cannot move through)
S = Start position (robot)
T = Target (computer)

The map will be provided as a 4x6 matrix where each number represents one square.

CRITICAL NAVIGATION RULES:
1. ONLY use these commands: UP, DOWN, LEFT, RIGHT
2. CRITICAL: Check BEFORE each move - you CANNOT EVER move into squares containing 1
3. You MUST find the shortest possible path
4. Start at 'S' and reach 'T'

MOVEMENT VALIDATION:
- BEFORE each move, check if the next square is a 0 (empty)
- If next square is 1, that move is INVALID
- From position S, check each possible move first

Required JSON output:
{
    "_thinking": "1. Current position [row,col], 2. Check available moves (no obstacles), 3. Choose best valid move",
    "steps": "DIRECTION1, DIRECTION2"
}

Be careful and remember that "steps" field is NOT an array, it's a string with directions separated by commas.

EXAMPLE OF BAD THINKING (DO NOT USE):
"_thinking": "1. Current position [row,col], 2. Check available moves (no obstacles), 3. Choose best valid move"

EXAMPLE OF GOOD THINKING:
"_thinking": "At [3,0], RIGHT blocked by wall. Must go UP first. From [2,0], can move RIGHT to [2,1]. Target is at bottom right, so need to navigate around central obstacles..."

MAP:
[
    [0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 0],
    [S, 1, 0, 0, 0, T]
]

IMPORTANT:
- VALIDATE EACH MOVE - never move into a 1
- At start (S), RIGHT is blocked by 1
- Must check each square before moving
- Moving diagonally is NOT allowed
- No backtracking unless absolutely necessary
- Output steps as comma-separated string
- _thinking field must show your actual path planning process

Use the MAP above to plan your path and output the steps as JSON.
"""

prompt_v3 = r"""
You are a navigation AI controlling a robot in a factory. Find a safe path from start to target.

MAP LEGEND:
0 = Empty space (can move through)
1 = Obstacle (CANNOT move through)
S = Start position (robot)
T = Target (computer)

CRITICAL NAVIGATION RULES:
- Before suggesting ANY move, check the destination coordinates in the map
- A move is only valid if destination square contains 0 or T
- A move is INVALID if destination square contains 1 - do not move into 1 EVER NEVER EVER
- Moving out of map boundaries is INVALID
- Diagonal moves are NOT allowed

PATHFINDING PROCESS:
1. For EACH move:
   - Write down current coordinates [row,col]
   - Check what number is in the destination square
   - ONLY move if destination contains 0 or T - otherwise it's INVALID
   - Update coordinates AFTER a valid move is found
   - Keep moving until you land on T - do not stop before reaching T
2. VERIFY entire path is obstacle-free before outputting

Required JSON output:
{
    "_thinking": "Checking each move: Start at [3,0]. Moving to [coord] contains [number], so move is [valid/invalid]...",
    "steps": "DIRECTION1, DIRECTION2"
}

Be careful and remember that "steps" field is NOT an array, it's a string with directions separated by commas.

BEFORE OUTPUTTING:
- Go through each step in "steps" field and check if it's valid
- Double check that no step moves into a square containing 1
- Verify that the path from S to T is valid
- Output CORRECT steps as comma-separated string

Use the MAP to plan your path and output the steps as JSON. The answer must only contain the JSON, nothing else.

MAP:
[
    [0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 0],
    [S, 1, 0, 0, 0, T]
]
"""

prompt_v4 = r"""
You are a navigation AI controlling a robot in a factory. Find a safe path from start to target.

MAP LEGEND:
0 = Empty space (can move through)
1 = Obstacle (CANNOT move through)
S = Start position (robot)
T = Target (computer)

CRITICAL MOVEMENT RULES:
- You can ONLY move to DIRECTLY ADJACENT squares (sharing an edge)
- If square A is blocked, you CANNOT reach any square behind it
- To reach position [row,X], you MUST be able to move there from an adjacent square
- ILLEGAL EXAMPLE: If [0,1] is blocked, you CANNOT move from [0,0] to [0,2] because they are not adjacent!
- Each move MUST be to a neighbor square - no exceptions, no skipping, no jumping
- You are not allowed to leave the map boundaries - coordinates must always be within [0,5] range

PATHFINDING RULES:
1. You can ONLY move to squares that are:
   - Directly adjacent (sharing an edge) to current position
   - Contains 0 or T
   - Reachable without jumping/skipping squares
2. If a square is blocked (contains 1):
   - You CANNOT move through it
   - You CANNOT skip over it
   - You MUST find another path around it
3. Keep moving until you land on T - do not stop before reaching T

Required JSON output:
{
    "_thinking": "Checking each move: Start at [3,0]. Moving to [coord] contains [number], so move is [valid/invalid]...",
    "steps": "DIRECTION1, DIRECTION2"
}

Be careful and remember that "steps" field is NOT an array, it's a string with directions separated by commas.

BEFORE OUTPUTTING:
- Go through each step in "steps" field and check if it's valid
- Double check that no step moves into a square containing 1
- Verify that the path from S to T is valid
- Output CORRECT steps as comma-separated string

Use the MAP to plan your path and output the steps as JSON. The answer must only contain the JSON, nothing else.

MAP:
[
    [0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 0],
    [S, 1, 0, 0, 0, T]
]
"""

prompt_v5 = r"""
You are a navigation AI controlling a robot in a factory. Find a safe path from start to target.

MAP LEGEND:
0 = Empty space (can move through)
1 = Obstacle (CANNOT move through)
S = Start position (robot)
T = Target (computer)

CRITICAL NAVIGATION RULES:
1. You can ONLY move to squares that are:
   - Directly adjacent to your CURRENT position
   - Containing 0 or T
   - Sharing an edge with current square (no diagonals)
2. After each move, your position MUST be updated
3. You can ONLY move from your CURRENT position
4. INVALID moves:
   - Moving into squares with 1
   - Moving outside map boundaries
   - Moving to non-adjacent squares
   - Moving diagonally

PATHFINDING PROCESS:
- Start at position of S [3,0]
- Start with empty "steps" field
- At EACH step:
   - Track your CURRENT position [row,col]
   - List ONLY the possible moves from CURRENT position
   - Choose ONE VALID move that brings you closer to T
   - After moving, update your CURRENT position and add direction to "steps" field
- Repeat until you reach T - DO NOT STOP BEFORE REACHING T
- Immediately stop when you make a move that reaches T
- NEVER try to move to squares not adjacent to CURRENT position
- After reaching T, go throught "steps" field and verify that the path is valid and does not contain any invalid moves

Required JSON output:
{
    "_thinking": "...",
    "steps": "DIRECTION1, DIRECTION2, ..., DIRECTIONN"
} where each direction is one of: UP, DOWN, LEFT, RIGHT and thinking field shows your path planning process

Be careful:
- steps must exactly match moves described in _thinking
- each move must be from CURRENT position to an ADJACENT square
- update position after EACH move
- track position continuously

MAP:
[
    [0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 0],
    [S, 1, 0, 0, 0, T]
]

Now output your answer as JSON.
"""

prompt_v6 = r"""
OBJECTIVE:
You are a robot navigator on a map represented by matrix. Your ONLY task is to move from S to T without hitting obstacles.

MOVEMENT RULES:
1. You start the move at current position [row,col]
2. Check ONLY the four adjacent squares:
   - UP:    [row-1,col]
   - RIGHT: [row,col+1]
   - DOWN:  [row+1,col]
   - LEFT:  [row,col-1]
   Verify each square value - can ONLY move to squares containing 0 or T
3. Can ONLY move to ONE of these squaresif it's a valid move (0 or T)
4. If move is blocked, must try different direction
5. NO JUMPING OR SKIPPING SQUARES ALLOWED
6. Moving to squares with 1 is STRICTLY FORBIDDEN UNDER ALL CIRCUMSTANCES
7. Moving outside map boundaries is STRICTLY FORBIDDEN UNDER ALL CIRCUMSTANCES

POSITION TRACKING:
Current = [row, col] of your position
Steps = empty list
For each move:
1. Look at square you want to move to
2. If it's 1 or outside map, that move is impossible
3. If it's 0 or T, you can move there
4. Update Current to new position after moving
5. Add direction to Steps after moving
6. If you reached T, immediately stop
7. If not reached T, repeat the steps until you reach T

After reaching T, go through Steps and verify that each move is valid and T was reached
Then convert Steps to comma-separated string -> ["DIRECTION1", "DIRECTION2", ...] becomes "DIRECTION1, DIRECTION2, ..."

MAP:
[
    [0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0],
    [0, 1, 0, 1, 0, 0],
    [S, 1, 0, 0, 0, T]
]

Required JSON output:
{
    "_thinking": "At [3,0]. RIGHT blocked by 1. Moving UP to [2,0]...",
    "steps": "DIRECTION1, DIRECTION2, ..., DIRECTIONN"
}

"_thinking" field must show your path planning process. Use it to explain your steps.

REMEMBER: You can ONLY move to squares directly connected to your current position!

Now output your answer as JSON.
"""

import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from aidevs3.services.ai import OpenAIService

load_dotenv()

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

ai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))

messages = [
    {
    "role": "user",
        "content": [
            {
                "type": "text",
                "text": prompt_v6
            },
        ]
    }
]

print(ai_service.custom_completion(messages, model="gpt-4o-mini", temperature=0.0))