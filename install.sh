#!/bin/bash

# Universal AI Configuration Installer
# Usage:
#   Interactive: curl -fsSL https://raw.githubusercontent.com/DevArtsLab/universal-ai-config/main/install.sh | bash
#   Non-interactive: curl -fsSL https://raw.githubusercontent.com/DevArtsLab/universal-ai-config/main/install.sh | bash -s -- --yes

set -e

# Parse arguments
AUTO_YES=false
for arg in "$@"; do
    case $arg in
        --yes|-y)
            AUTO_YES=true
            shift
            ;;
        *)
            # Unknown option
            ;;
    esac
done

# Detect non-interactive environment (no TTY or CI)
if [ -t 0 ]; then
    IS_INTERACTIVE=true
else
    IS_INTERACTIVE=false
fi

if [ "$CI" = "true" ] || [ "$NONINTERACTIVE" = "1" ]; then
    AUTO_YES=true
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO="DevArtsLab/universal-ai-config"
BRANCH="main"
INSTALL_DIR="${HOME}/.universal-ai-config"
VENV_DIR="${INSTALL_DIR}/venv"

# Functions
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

confirm() {
    local prompt="$1"
    local default="$2"
    
    if [ "$AUTO_YES" = true ]; then
        return 0
    fi
    
    if [ "$IS_INTERACTIVE" = false ]; then
        # In non-interactive mode without --yes, default to no
        if [ "$default" = "Y" ]; then
            return 0
        else
            return 1
        fi
    fi
    
    read -p "$prompt (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    fi
    return 1
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        print_info "Please install Python 3.8 or higher"
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Found Python $python_version"
    
    # Check if version is >= 3.8
    if [ "$(printf '%s\n' "3.8" "$python_version" | sort -V | head -n1)" != "3.8" ]; then
        print_error "Python 3.8 or higher is required (found $python_version)"
        exit 1
    fi
}

check_pip() {
    if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
        print_error "pip is not installed"
        print_info "Please install pip"
        exit 1
    fi
    print_success "Found pip"
}

detect_existing_installation() {
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Existing installation found at $INSTALL_DIR"
        
        if confirm "Do you want to remove it and reinstall?" "N"; then
            print_info "Removing existing installation..."
            rm -rf "$INSTALL_DIR"
        else
            print_info "Keeping existing installation"
            exit 0
        fi
    fi
}

create_install_dir() {
    print_info "Creating installation directory..."
    mkdir -p "$INSTALL_DIR"
    print_success "Created $INSTALL_DIR"
}

download_package() {
    print_info "Downloading package from GitHub..."
    
    # Try downloading the package
    cd "$INSTALL_DIR"
    
    if command -v curl &> /dev/null; then
        curl -fsSL "https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz" -o universal-ai-config.tar.gz
    elif command -v wget &> /dev/null; then
        wget -q "https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz" -O universal-ai-config.tar.gz
    else
        print_error "Neither curl nor wget is available"
        exit 1
    fi
    
    print_success "Downloaded package"
    
    # Extract
    print_info "Extracting package..."
    tar -xzf universal-ai-config.tar.gz
    mv "universal-ai-config-${BRANCH}"/* .
    rm -rf "universal-ai-config-${BRANCH}" universal-ai-config.tar.gz
    print_success "Extracted package"
}

install_via_pip() {
    print_info "Installing via pip..."
    
    # Create virtual environment
    print_info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install package
    pip install -e .
    
    print_success "Installed package"
}

create_symlink() {
    print_info "Creating symlink to ai-config command..."
    
    BIN_DIR="${HOME}/.local/bin"
    mkdir -p "$BIN_DIR"
    
    # Create symlink
    ln -sf "${VENV_DIR}/bin/ai-config" "${BIN_DIR}/ai-config"
    
    # Make executable
    chmod +x "${BIN_DIR}/ai-config"
    
    print_success "Created symlink at ${BIN_DIR}/ai-config"
}

update_path() {
    print_info "Checking PATH configuration..."
    
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":${HOME}/.local/bin:"* ]]; then
        print_warning "~/.local/bin is not in your PATH"
        
        # Detect shell
        SHELL_CONFIG=""
        if [ -n "$ZSH_VERSION" ]; then
            SHELL_CONFIG="${HOME}/.zshrc"
        elif [ -n "$BASH_VERSION" ]; then
            SHELL_CONFIG="${HOME}/.bashrc"
        fi
        
        if [ -n "$SHELL_CONFIG" ]; then
            print_info "Adding to $SHELL_CONFIG"
            echo "" >> "$SHELL_CONFIG"
            echo "# Universal AI Config" >> "$SHELL_CONFIG"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_CONFIG"
            print_success "Added to $SHELL_CONFIG"
            print_warning "Please run: source $SHELL_CONFIG"
        else
            print_warning "Please add ~/.local/bin to your PATH manually"
        fi
    else
        print_success "~/.local/bin is already in PATH"
    fi
}

detect_legacy_configs() {
    print_info "Checking for legacy configurations..."
    
    LEGACY_FOUND=0
    
    if [ -d "${HOME}/.config/devin" ]; then
        print_warning "Found Devin config at ~/.config/devin"
        LEGACY_FOUND=1
    fi
    
    if [ -d "${HOME}/.codium" ]; then
        print_warning "Found Codium config at ~/.codium"
        LEGACY_FOUND=1
    fi
    
    if [ -d "${HOME}/.windsurf" ]; then
        print_warning "Found Windsurf config at ~/.windsurf"
        LEGACY_FOUND=1
    fi
    
    if [ -d "${HOME}/.config/claude" ]; then
        print_warning "Found Claude config at ~/.config/claude"
        LEGACY_FOUND=1
    fi
    
    return $LEGACY_FOUND
}

prompt_migration() {
    if detect_legacy_configs; then
        echo ""
        print_warning "Legacy configurations detected"
        
        if confirm "Do you want to migrate them to the new unified config?" "N"; then
            return 0
        fi
    fi
    return 1
}

initialize_config() {
    print_info "Initializing configuration..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Initialize
    ai-config init
    
    print_success "Configuration initialized"
}

migrate_configs() {
    print_info "Migrating legacy configurations..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Migrate
    ai-config migrate
    
    print_success "Migration complete"
}

validate_installation() {
    print_info "Validating installation..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Validate
    ai-config validate
    
    print_success "Installation validated"
}

show_status() {
    print_info "Installation status:"
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Show status
    ai-config status
}

cleanup() {
    print_info "Cleaning up..."
    # No cleanup needed for now
}

main() {
    echo "======================================"
    echo "Universal AI Configuration Installer"
    echo "======================================"
    echo ""
    
    # Check prerequisites
    check_python
    check_pip
    
    # Detect existing installation
    detect_existing_installation
    
    # Create install directory
    create_install_dir
    
    # Download package
    download_package
    
    # Install via pip
    install_via_pip
    
    # Create symlink
    create_symlink
    
    # Update PATH
    update_path
    
    echo ""
    print_success "Installation complete!"
    echo ""
    
    # Check for legacy configs
    if prompt_migration; then
        migrate_configs
    else
        initialize_config
    fi
    
    # Validate
    validate_installation
    
    echo ""
    print_success "All done!"
    echo ""
    print_info "You can now use: ai-config"
    print_info "Run 'ai-config --help' for available commands"
    echo ""
    
    # Show status
    show_status
    
    cleanup
}

# Run main function
main
