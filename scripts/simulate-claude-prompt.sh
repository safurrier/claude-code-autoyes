#!/bin/bash
echo "=== Claude Prompt Simulator ==="
echo "This will simulate Claude prompts for testing auto-yes functionality"
echo ""
echo "❯ 1. Yes"
echo "❯ 2. No"
echo "❯ 3. Skip"
echo ""
echo -n "Do you want to continue with this operation? "
read -t 30 response
echo ""
echo "Response received: $response"
echo "Test complete!"