#!/bin/bash

# Universal AI Configuration Uninstaller
# Usage: curl -fsSL https://raw.githubusercontent.com/DevArtsLab/universal-ai-config/main/uninstall.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

INSTALL_DIR="${HOME}/.universal-ai-config"
BIN_DIR="${HOME}/.local/bin"
SYMLINK="${BIN_DIR}/ai-config"

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_info() {
    echo "ℹ $1"
}

confirm_uninstall() {
    print_warning "This will remove Universal AI Configuration from your system"
    print_warning "Configuration files in ~/.config/ai/ will be preserved"
    echo ""
    read -p "Are you sure you want to continue? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Uninstall cancelled"
        exit 0
    fi
}

remove_symlink() {
    if [ -L "$SYMLINK" ]; then
        print_info "Removing symlink..."
        rm "$SYMLINK"
        print_success "Removed symlink"
    else
        print_info "Symlink not found (may have been removed manually)"
    fi
}

remove_installation() {
    if [ -d "$INSTALL_DIR" ]; then
        print_info "Removing installation directory..."
        rm -rf "$INSTALL_DIR"
        print_success "Removed $INSTALL_DIR"
    else
        print_info "Installation directory not found"
    fi
}

ask_remove_config() {
    if [ -d "${HOME}/.config/ai" ]; then
        print_warning "Configuration files found at ~/.config/ai/"
        read -p "Do you want to remove configuration files as well? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing configuration files..."
            rm -rf "${HOME}/.config/ai"
            rm -rf "${HOME}/.local/share/ai"
            rm -rf "${HOME}/.local/state/ai"
            rm -rf "${HOME}/.cache/ai"
            print_success "Removed configuration files"
        else
            print_info "Configuration files preserved"
        fi
    fi
}

cleanup_path() {
    print_info "Checking PATH configuration..."
    
    # Detect shell config
    SHELL_CONFIG=""
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_CONFIG="${HOME}/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_CONFIG="${HOME}/.bashrc"
    fi
    
    if [ -n "$SHELL_CONFIG" ] && [ -f "$SHELL_CONFIG" ]; then
        if grep -q "Universal AI Config" "$SHELL_CONFIG"; then
            print_info "Removing PATH configuration from $SHELL_CONFIG"
            # Remove the lines we added
            sed -i.bak '/# Universal AI Config/,+2d' "$SHELL_CONFIG"
            print_success "Removed PATH configuration"
            print_warning "Please run: source $SHELL_CONFIG"
        fi
    fi
}

main() {
    echo "======================================"
    echo "Universal AI Configuration Uninstaller"
    echo "======================================"
    echo ""
    
    confirm_uninstall
    
    remove_symlink
    remove_installation
    ask_remove_config
    cleanup_path
    
    echo ""
    print_success "Uninstall complete!"
    echo ""
    print_info "Thank you for using Universal AI Configuration"
}

main
