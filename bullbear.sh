#!/bin/bash

USER_INPUT="$1"

BLOCKED_PATTERNS=(
    ".env" "password" "secret" "api_key" "token"
    "ignore.*rules" "bypass" "unrestricted"
    "forget.*instructions" "all in" "entire portfolio"
    "pump" "10000" "500000" "leverage" "margin"
    "/etc/" "sudo" "rm -rf" "curl" "wget"
    "cat.*file" "read.*file" "access.*file"
)

for PATTERN in "${BLOCKED_PATTERNS[@]}"; do
    if echo "$USER_INPUT" | grep -qi "$PATTERN"; then
        echo "🛡️  ARMORCLAW INSTANT BLOCK"
        echo "❌ Flagged: '$PATTERN'"
        echo "[$(date)] INSTANT BLOCK | $PATTERN | $USER_INPUT" >> ~/sentinel-claw/trades.log
        exit 1
    fi
done

echo "🐂 Bull Agent analyzing..."
BULL=$(openclaw agent --agent main --message "You are a BULL analyst. Give 3 numbered reasons why this is a good trade. No Decision/ALLOW/BLOCK words. Trade: $USER_INPUT")

echo "🐻 Bear Agent analyzing..."
BEAR=$(openclaw agent --agent main --message "You are a BEAR analyst. Give 3 numbered risks of this trade. No Decision/ALLOW/BLOCK words. Trade: $USER_INPUT")

echo "⚖️  Warden deciding..."
VERDICT=$(openclaw agent --agent main --message "You are a trading Warden.
BULL: $BULL
BEAR: $BEAR
Trade: $USER_INPUT
Rules:
- If bear risks are strong or news is negative → BLOCK
- Meme stocks, penny stocks, high volatility → BLOCK
- Only ALLOW if bull case clearly outweighs bear case
- Do NOT default to ALLOW
Respond ONLY as:
Decision: ALLOW or BLOCK
Reason: one sentence")

echo "=============================="
echo "🐂 BULL CASE:"
echo "$BULL"
echo ""
echo "🐻 BEAR CASE:"
echo "$BEAR"
echo ""
echo "⚖️  WARDEN VERDICT:"
echo "$VERDICT"
echo "=============================="

if echo "$VERDICT" | grep -qi "Decision: ALLOW"; then
    SYMBOL=$(echo "$USER_INPUT" | grep -oE '\b[A-Z]{2,5}\b' | head -1)
    echo "✅ Trade Approved — Buying $SYMBOL"
    echo "[$(date)] APPROVED | $SYMBOL | $USER_INPUT" >> ~/sentinel-claw/trades.log
    source ~/sentinel-claw/venv/bin/activate
    python3 ~/sentinel-claw/executor.py "$SYMBOL" 1
else
    echo "❌ Trade Blocked by Warden"
    echo "[$(date)] BLOCKED | $USER_INPUT" >> ~/sentinel-claw/trades.log
fi
