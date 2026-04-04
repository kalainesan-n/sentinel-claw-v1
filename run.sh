#!/bin/bash

USER_INPUT="$1"

PROMPT="
You are a secure AI trading system.

User request:
$USER_INPUT

Rules:
- High risk → BLOCK
- Large trade → BLOCK
- Unsafe request → BLOCK
- Otherwise → ALLOW

Output format:
Decision: ALLOW or BLOCK
Reason: short explanation
"

echo "🤖 Running AI decision..."

RESULT=$(openclaw agent --agent main --message "$PROMPT")

echo "$RESULT"

# Extract decision
DECISION=$(echo "$RESULT" | grep -i "Decision:" | awk '{print $2}')

if [ "$DECISION" == "ALLOW" ]; then
    echo "----------------------------------"
    echo "✅ Trade Approved"
    # Extract symbol and quantity from input
    SYMBOL=$(echo "$USER_INPUT" | grep -oE '[A-Z]{2,5}')
    QTY=1
    echo "📈 Executing: BUY $QTY shares of $SYMBOL"
    source ~/sentinel-claw/venv/bin/activate
    python3 ~/sentinel-claw/executor.py "$SYMBOL" "$QTY"
else
    echo "----------------------------------"
    echo "❌ Trade Blocked by Warden"
fi
