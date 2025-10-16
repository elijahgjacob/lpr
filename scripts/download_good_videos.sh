#!/bin/bash

# Script to download high-quality ALPR videos
# Install yt-dlp first: pip install yt-dlp

echo "=== DOWNLOADING HIGH-QUALITY ALPR VIDEOS ==="

# Create videos directory
mkdir -p videos/quality

# Download high-quality traffic videos from YouTube
# These are examples - replace with actual good video URLs you find

echo "Searching for high-quality traffic videos..."
echo "Look for these search terms on YouTube:"
echo "- 'traffic surveillance 4K high quality'"
echo "- 'highway traffic camera HD'"
echo "- 'license plate recognition test video'"
echo "- 'traffic intersection 1080p'"

# Example command (replace VIDEO_URL with actual URL):
# yt-dlp -f "best[height>=1080]" -o "videos/quality/traffic_%(title)s.%(ext)s" VIDEO_URL

echo ""
echo "Manual download instructions:"
echo "1. Go to YouTube"
echo "2. Search for: 'traffic surveillance 4K'"
echo "3. Look for videos with:"
echo "   - 1080p or higher resolution"
echo "   - Clear license plates visible"
echo "   - Good lighting"
echo "   - 5-15 minutes duration"
echo "4. Copy the URL and run:"
echo "   yt-dlp -f 'best[height>=1080]' -o 'videos/quality/%(title)s.%(ext)s' [URL]"

echo ""
echo "Alternative: Download from academic datasets:"
echo "1. OpenALPR Benchmarks: https://github.com/openalpr/benchmarks"
echo "2. CCPD Dataset: https://github.com/detectRecog/CCPD"
echo "3. UFPR-ALPR: https://web.inf.ufpr.br/vri/databases/ufpr-alpr/"
