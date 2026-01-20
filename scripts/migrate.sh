#!/bin/bash
# Database migration script
# Usage: ./migrate.sh [command] [options]
#
# Commands:
#   upgrade     - Apply all pending migrations (default)
#   downgrade   - Revert last migration
#   current     - Show current revision
#   history     - Show migration history
#   heads       - Show head revisions
#   new         - Create new migration
#
# Examples:
#   ./migrate.sh                    # Apply all migrations
#   ./migrate.sh upgrade            # Apply all migrations
#   ./migrate.sh downgrade -1       # Revert last migration
#   ./migrate.sh current            # Show current version
#   ./migrate.sh new "add users"    # Create new migration

set -e

# Change to project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Load environment variables if .env exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Default command
COMMAND="${1:-upgrade}"

case "$COMMAND" in
    upgrade)
        echo "🔼 Applying database migrations..."
        alembic upgrade head
        echo "✅ Migrations applied successfully"
        ;;
    downgrade)
        REVISION="${2:--1}"
        echo "🔽 Reverting migrations to: $REVISION"
        alembic downgrade "$REVISION"
        echo "✅ Downgrade completed"
        ;;
    current)
        echo "📍 Current database revision:"
        alembic current
        ;;
    history)
        echo "📜 Migration history:"
        alembic history --verbose
        ;;
    heads)
        echo "🎯 Head revisions:"
        alembic heads
        ;;
    new)
        MESSAGE="${2:-auto_migration}"
        echo "📝 Creating new migration: $MESSAGE"
        alembic revision --autogenerate -m "$MESSAGE"
        echo "✅ Migration created"
        ;;
    stamp)
        REVISION="${2:-head}"
        echo "🏷️ Stamping database with revision: $REVISION"
        alembic stamp "$REVISION"
        echo "✅ Database stamped"
        ;;
    *)
        echo "Unknown command: $COMMAND"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  upgrade     - Apply all pending migrations (default)"
        echo "  downgrade   - Revert last migration"
        echo "  current     - Show current revision"
        echo "  history     - Show migration history"
        echo "  heads       - Show head revisions"
        echo "  new         - Create new migration"
        echo "  stamp       - Stamp database with revision without running migrations"
        exit 1
        ;;
esac
