#!/bin/bash

# Script to delete all repositories except Trust
# This script uses GitHub CLI (gh) to delete repositories
# Make sure you have GitHub CLI installed and authenticated before running

echo "Starting repository deletion process..."
echo "This will delete all repositories except 'Trust'"
echo ""

# Array of repositories to delete
REPOS_TO_DELETE=(
    "Annon-Boot"
    "Annon-Moble"
    "Annon-OS-Backend"
    "Annon-Safety"
    "AnnonOS"
    "Energy-Conservation"
)

# Counter for tracking deletions
DELETED=0
FAILED=0

# Delete each repository
for repo in "${REPOS_TO_DELETE[@]}"; do
    echo "Deleting repository: $repo"
    if gh repo delete "Tole1775/$repo" --confirm; then
        echo "✓ Successfully deleted: $repo"
        ((DELETED++))
    else
        echo "✗ Failed to delete: $repo"
        ((FAILED++))
    fi
    echo ""
done

# Summary
echo "========================================="
echo "Deletion process complete!"
echo "Successfully deleted: $DELETED repositories"
echo "Failed deletions: $FAILED repositories"
echo "Repository 'Trust' has been preserved"
echo "========================================="
