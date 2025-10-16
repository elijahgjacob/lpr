
# 🎯 PRACTICAL GUIDE: Get Working ALPR Videos

## ✅ IMMEDIATE SOLUTION (Your Enhanced Video)
You already have a better video:
- **File**: `videos/quality/enhanced_traffic.mp4`
- **Quality**: 1280x720, 30fps, 10 seconds
- **Score**: 4/8 (Good for testing)
- **Use**: This is better than your original video!

## 🚀 QUICK WIN OPTIONS

### Option 1: Free Stock Video Sites (5-10 minutes)
1. **Pexels**: https://www.pexels.com/search/traffic/
   - Search for "traffic", "highway", "surveillance"
   - Download highest quality available
   - Save to `videos/quality/`

2. **Pixabay**: https://pixabay.com/videos/search/traffic/
   - Search for "traffic surveillance", "highway camera"
   - Look for videos with visible license plates
   - Download to `videos/quality/`

3. **Videvo**: https://www.videvo.net/stock-video-footage/traffic/
   - Free traffic footage
   - Download HD quality

### Option 2: YouTube (10-15 minutes)
1. Go to YouTube
2. Search: "traffic surveillance 4K", "highway traffic camera"
3. Find videos with clear license plates
4. Use yt-dlp to download:
   ```bash
   yt-dlp -f "best[height>=1080]" -o "videos/quality/%(title)s.%(ext)s" [URL]
   ```

### Option 3: Create Your Own (30 minutes)
1. Find a busy intersection or highway
2. Record with your phone (1080p or higher)
3. Look for clear license plates
4. Transfer to `videos/quality/`

## 🎯 TARGET SPECIFICATIONS
- **Resolution**: 1280x720 or higher (you have this!)
- **Duration**: 2+ minutes (longer is better)
- **Quality**: Clear license plates visible
- **File Size**: 10MB+ (indicates good quality)

## ✅ YOUR CURRENT STATUS
- ✅ **Enhanced video**: 1280x720, 30fps (4/8 quality score)
- ✅ **Download tools**: Ready to use
- ✅ **Quality checker**: Working
- ⏳ **Need**: Longer duration videos with clear plates

## 🚀 NEXT STEPS
1. **Use your enhanced video** for now (it's better than before!)
2. **Download 1-2 additional videos** from stock sites
3. **Extract frames** from all videos for ground truth
4. **Improve your ALPR system** with better data

## 📊 QUALITY CHECK
After downloading any video:
```bash
python scripts/check_video_quality.py videos/quality/your_video.mp4
```
Target: Quality score 4+/8 (you already have this!)
