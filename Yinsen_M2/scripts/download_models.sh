#!/bin/bash

# This script doesn't need to download Whisper models as they're downloaded automatically
# when first used, but we'll keep it and add instructional content

echo "Whisper models will be downloaded automatically when the system first runs."
echo "Models are stored in your local cache directory by default."
echo "Available model sizes: tiny, base, small, medium, large"
echo ""
echo "Model sizes and approximate memory requirements:"
echo "- tiny: ~150MB"
echo "- base: ~300MB"
echo "- small: ~500MB"
echo "- medium: ~1.5GB"
echo "- large: ~3GB"
echo ""
echo "Current config uses the medium model which requires ~2.5GB of GPU memory"
echo "Configure your preferred model size in config/config.yaml" 