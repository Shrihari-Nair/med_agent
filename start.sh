#!/bin/bash
# Simple backwards-compatible startup script
# Forwards to the properly organized script
exec ./scripts/start.sh "$@" 