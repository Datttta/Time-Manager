#!/usr/bin/env bash

if grep -qi microsoft /proc/version 2>/dev/null; then
  echo "Running on WSL (Windows Subsystem for Linux)"
elif [ "$(uname -s)" = "Linux" ]; then
  echo "Running on native Linux"
fi
