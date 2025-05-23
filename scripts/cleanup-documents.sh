#!/bin/bash

# Document Cleanup Script for Patrick's Development Environment
# This script helps maintain a clean project structure

echo "🧹 Starting Document Cleanup Process..."

# Function to display size of directories
show_size() {
    echo "📊 Current storage usage:"
    du -sh /home/patrick/Documents/*/ 2>/dev/null | sort -hr | head -20
}

# Function to clean node_modules
clean_node_modules() {
    echo "🗑️  Cleaning node_modules directories..."
    find /home/patrick/Documents -name "node_modules" -type d -prune | while read dir; do
        echo "Removing: $dir"
        rm -rf "$dir"
    done
    echo "✅ node_modules cleaned!"
}

# Function to clean dist/build folders
clean_dist() {
    echo "🗑️  Cleaning dist/build directories..."
    find /home/patrick/Documents -name "dist" -type d -prune | while read dir; do
        # Skip if it's in node_modules (already deleted)
        if [[ ! "$dir" =~ "node_modules" ]]; then
            echo "Removing: $dir"
            rm -rf "$dir"
        fi
    done
    echo "✅ dist folders cleaned!"
}

# Function to organize projects
organize_projects() {
    echo "📁 Organizing projects by category..."
    
    # Create category folders if they don't exist
    mkdir -p /home/patrick/Documents/archive/inactive
    mkdir -p /home/patrick/Documents/personal/work-files
    
    # Move work files
    if [ -d "/home/patrick/Documents/work" ]; then
        echo "Moving work files to personal directory..."
        mv /home/patrick/Documents/work /home/patrick/Documents/personal/
    fi
    
    # Move home stuff
    if [ -d "/home/patrick/Documents/homeStuff" ]; then
        echo "Moving homeStuff to personal directory..."
        mv /home/patrick/Documents/homeStuff /home/patrick/Documents/personal/
    fi
    
    echo "✅ Projects organized!"
}

# Function to create project index
create_index() {
    echo "📝 Creating project index..."
    cat > /home/patrick/Documents/PROJECT_INDEX.md << 'EOF'
# Project Index

## Active Projects
- **agentic-persona** - AI agent development framework
- **cannabis-finder** - Cannabis strain finder and recommendations
- **MotorcycleWkspMgtApp** - Workshop management system
- **vuebudgetfire** - Personal finance management
- **UFC-Betting-System** - Sports betting analysis platform
- **music-service-proxy** - Multi-service music proxy

## Maintenance Projects
- **color-harmony** - Music/color therapy game
- **receipt-scanner** - OCR receipt management

## Archived Projects
- **space_story** - Interactive story app
- **mushroom_adventure** - Adventure game
- **procrastinator99** - Task gamification

## Development Standards
- Primary Stack: Vue 3 + TypeScript + Firebase
- Build Tool: Vite
- Styling: Tailwind CSS
- State: Pinia
- Version Control: Git with main branch

## Quick Commands
- Start dev: `npm run dev`
- Build: `npm run build`
- Test: `npm test`
- Deploy: `npm run deploy`
EOF
    echo "✅ Project index created!"
}

# Main menu
echo "
🧹 Document Cleanup Options:
1. Show current storage usage
2. Clean all node_modules (saves ~1.8GB)
3. Clean all dist folders (saves ~500MB)
4. Organize projects into categories
5. Create project index
6. Full cleanup (2+3+4+5)
0. Exit
"

read -p "Select option: " option

case $option in
    1) show_size ;;
    2) clean_node_modules ;;
    3) clean_dist ;;
    4) organize_projects ;;
    5) create_index ;;
    6) 
        clean_node_modules
        clean_dist
        organize_projects
        create_index
        show_size
        ;;
    0) echo "👋 Cleanup cancelled" ;;
    *) echo "❌ Invalid option" ;;
esac

echo "
✨ Cleanup process completed!
💡 Tip: Run 'npm install' in any project before working on it again.
"