#!/bin/bash
# Setup script for custom git hooks

echo "Setting up custom git hooks..."

# Configure git to use our custom hooks directory
git config core.hooksPath .githooks

# Make hooks executable (Unix/Linux/Mac)
chmod +x .githooks/pre-push 2>/dev/null

echo "✅ Custom git hooks configured!"
echo ""
echo "Branch protection status:"

# Check current setting
if [ -f .env ]; then
    export $(grep -E '^ALLOW_DIRECT_PUSH_TO_MAIN=' .env | xargs)
fi

ALLOW_DIRECT_PUSH="${ALLOW_DIRECT_PUSH_TO_MAIN:-true}"

if [ "$ALLOW_DIRECT_PUSH" = "true" ]; then
    echo "  ⚠️  Direct pushes to main: ALLOWED (development mode)"
    echo "  To enable protection: Set ALLOW_DIRECT_PUSH_TO_MAIN=false in .env"
else
    echo "  ✅ Direct pushes to main: BLOCKED (protected mode)"
    echo "  To disable protection: Set ALLOW_DIRECT_PUSH_TO_MAIN=true in .env"
fi

echo ""
echo "Note: You still have pre-commit hooks for code quality."