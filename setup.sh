#!/bin/bash

# Check Python version
python_version=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)
python_version_numeric=$(echo $python_version | awk -F. '{print $1 * 100 + $2}')

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Checking Python version..."

# Check if Python is installed and if version is 3.10+
if [ -z "$python_version" ]; then
  echo -e "${RED}Python not found!${NC}"
  has_python310=false
elif [ $python_version_numeric -lt 310 ]; then
  echo -e "${YELLOW}Python version $python_version detected.${NC}"
  echo -e "${YELLOW}This project requires Python 3.10+ for CrewAI compatibility.${NC}"
  has_python310=false
else
  echo -e "${GREEN}Python version $python_version detected. This meets requirements.${NC}"
  has_python310=true
fi

# Check if conda is installed
if command -v conda >/dev/null 2>&1; then
  has_conda=true
  echo -e "${GREEN}Conda is installed.${NC}"
else
  has_conda=false
  echo -e "${YELLOW}Conda is not installed.${NC}"
fi

# Offer installation options
if [ "$has_python310" = false ]; then
  echo ""
  echo "You have two options to proceed:"
  
  if [ "$has_conda" = true ]; then
    echo "1. Create a conda environment with Python 3.10 (Recommended)"
    echo "   Command: conda env create -f environment.yml"
  else
    echo "1. Install Miniconda and create an environment with Python 3.10 (Recommended)"
    echo "   See: https://docs.conda.io/en/latest/miniconda.html"
  fi
  
  echo "2. Install Python 3.10+ on your system"
  echo "   See: https://www.python.org/downloads/"
  echo ""
  
  # If conda is available, offer to create the environment
  if [ "$has_conda" = true ]; then
    read -p "Do you want to create a conda environment now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      echo "Creating conda environment..."
      conda env create -f environment.yml
      echo -e "${GREEN}Environment 'make_n8n' created.${NC}"
      echo "To activate, run: conda activate make_n8n"
    fi
  fi
else
  # Python 3.10+ is available, so offer to install with pip
  echo "Python 3.10+ is available. Installing dependencies with pip..."
  pip install -r requirements.txt
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}Dependencies installed successfully.${NC}"
    echo "You can now run the application with: python src/make_to_n8n_converter.py"
  else
    echo -e "${RED}Failed to install dependencies.${NC}"
    echo "Please try installing manually with: pip install -r requirements.txt"
  fi
fi

echo ""
echo "Setup complete!" 