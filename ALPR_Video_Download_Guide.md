
# ALPR Video Download Guide

## Quick Start (YouTube)
1. Search YouTube for these terms:
   - "traffic surveillance 4K"
   - "highway traffic camera HD"
   - "traffic intersection 1080p"
   - "vehicle surveillance clear plates"

2. Download with yt-dlp:
   ```bash
   yt-dlp -f "best[height>=1080]" -o "videos/quality/%(title)s.%(ext)s" [YOUTUBE_URL]
   ```

## Academic Datasets (Best Quality)

### UFPR-ALPR Dataset
- **URL**: https://web.inf.ufpr.br/vri/databases/ufpr-alpr/
- **Size**: ~2GB
- **Quality**: 1920x1080, 4500 images
- **License**: Research use

### AI City Challenge
- **URL**: https://www.aicitychallenge.org/
- **Size**: ~50GB  
- **Quality**: 960p+, 3 hours of video
- **License**: Research use

### CCPD Dataset
- **URL**: https://github.com/detectRecog/CCPD
- **Size**: ~10GB
- **Quality**: 290k+ images
- **License**: Research use

## Video Quality Checklist
- ✅ Resolution: 1080p or higher
- ✅ Duration: 5+ minutes
- ✅ File Size: 50MB+ (indicates good quality)
- ✅ Clear License Plates: Visible to human eye
- ✅ Good Lighting: Well-lit conditions
- ✅ Multiple Vehicles: Variety of plate types

## After Download
```bash
# Check video quality
python scripts/check_video_quality.py videos/quality/your_video.mp4

# Target: Quality Score 6+/8
```
