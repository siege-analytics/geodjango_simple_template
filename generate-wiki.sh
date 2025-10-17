#!/bin/bash
# Generate customized wiki content from templates

set -e

echo "=== GeoDjango Wiki Content Generator ==="

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Create one with your configuration."
    exit 1
fi

# Source environment variables
export $(grep -v '^#' .env | xargs)

# Set defaults if not set
PROJECT_NAME=${PROJECT_NAME:-geodjango_app}
PROJECT_PREFIX=${PROJECT_PREFIX:-gd}
POSTGRES_USER=${POSTGRES_USER:-dheerajchand}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-strongpasswd}
POSTGRES_DB=${POSTGRES_DB:-geodjango_database}
POSTGRES_PORT=${POSTGRES_PORT:-54321}
DJANGO_PORT=${DJANGO_PORT:-1337}

echo "📝 Generating wiki content for: $PROJECT_NAME"
echo "🏷️  Project prefix: $PROJECT_PREFIX"

# Create wiki directory
mkdir -p wiki

# Generate Home.md
echo "Generating Home.md..."
envsubst < wiki-template/Home.md > wiki/Home.md

# Copy documentation
echo "Copying documentation..."
cp DOCUMENTATION.md wiki/Complete-Documentation.md

echo ""
echo "✅ Wiki content generated in ./wiki/ directory"
echo ""
echo "📋 Generated files:"
echo "  - wiki/Home.md"
echo "  - wiki/Complete-Documentation.md"
echo ""
echo "🚀 Next steps:"
echo "  1. Review generated content"
echo "  2. Upload to your GitLab/GitHub wiki"
echo "  3. Customize further as needed"
echo ""
echo "💡 Tip: The generated content uses your .env configuration"
echo "   and can be safely used in private repositories without"
echo "   exposing template defaults."
