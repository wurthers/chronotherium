#!/bin/bash


# Install pip3 if it is not already installed
if [[ ! $( dpkg -s python3-pip ) ]]; then
  echo "Installing pip3..."
  sudo apt install python3-pip
fi

# Install bearlibterminal
if [[ ! $( pip3 show bearlibterminal ) ]]; then
  echo "Installing bearlibterminal..."
  sudo -H pip3 install bearlibterminal
fi

# Install bearlibterminal
if [[ ! $( pip3 show pyinstaller ) ]]; then
  echo "Installing bearlibterminal..."
  sudo -H pip3 install pyinstaller
fi

echo "Setup complete!"
