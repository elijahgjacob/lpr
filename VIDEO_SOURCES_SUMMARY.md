# 🎯 Best Video Sources for ALPR Evaluation

## 📊 Current Status
- **Your current video**: 640x360, 0.9MB, 10 seconds - **Poor quality**
- **Target quality**: 1920x1080+, 50MB+, 5+ minutes - **Excellent quality**

## 🥇 **TOP RECOMMENDATIONS**

### **1. UFPR-ALPR Dataset (BEST OPTION)**
- **Quality**: ⭐⭐⭐⭐⭐ (Academic grade)
- **Size**: 4,500 images, 1920x1080 resolution
- **Download**: https://web.inf.ufpr.br/vri/databases/ufpr-alpr/
- **License**: Research use
- **Command**: `python scripts/download_ufpr_dataset.py`

### **2. AI City Challenge Dataset**
- **Quality**: ⭐⭐⭐⭐⭐ (Research grade)
- **Size**: 3 hours of video, 960p+ resolution
- **Download**: https://www.aicitychallenge.org/
- **License**: Research use

### **3. YouTube Videos (FASTEST)**
- **Quality**: ⭐⭐⭐⭐ (Manual selection needed)
- **Time**: 15-30 minutes to find good videos
- **Search terms**:
  - "traffic surveillance 4K high quality"
  - "highway traffic camera HD license plates"
  - "traffic intersection 1080p clear plates"

## 🚀 **QUICK START (Choose One)**

### **Option A: Academic Dataset (Recommended)**
```bash
# Download UFPR-ALPR dataset
python scripts/download_ufpr_dataset.py

# This gives you 4,500 high-quality images with annotations
```

### **Option B: YouTube Videos (Fastest)**
```bash
# 1. Search YouTube for these terms:
#    - "traffic surveillance 4K"
#    - "highway traffic camera HD"

# 2. When you find a good video, download it:
yt-dlp -f "best[height>=1080]" -o "videos/quality/%(title)s.%(ext)s" [YOUTUBE_URL]

# 3. Check quality:
python scripts/check_video_quality.py videos/quality/your_video.mp4
```

### **Option C: Stock Video Sites**
- **Pexels**: Free traffic videos
- **Pixabay**: Free 4K traffic footage
- **Videvo**: Free surveillance videos

## 📋 **Video Quality Checklist**
- ✅ **Resolution**: 1920x1080 or higher
- ✅ **Duration**: 5+ minutes
- ✅ **File Size**: 50MB+ (indicates good quality)
- ✅ **Clear Plates**: License plates visible to human eye
- ✅ **Good Lighting**: Well-lit conditions
- ✅ **Multiple Vehicles**: Variety of plate types

## 🎯 **Target Quality Score: 6+/8**

## 📁 **File Structure**
```
videos/
├── quality/           # High-quality videos
├── datasets/          # Academic datasets
└── sample_traffic.mp4 # Your current low-quality video
```

## 🔧 **Tools Created**
- `scripts/download_ufpr_dataset.py` - Download academic dataset
- `scripts/find_youtube_videos.py` - Find YouTube videos
- `scripts/check_video_quality.py` - Check video quality
- `ALPR_Video_Download_Guide.md` - Comprehensive guide

## 🎉 **Next Steps**
1. **Choose your approach** (Academic dataset or YouTube)
2. **Download videos** using the scripts
3. **Check quality** with quality checker
4. **Extract frames** for ground truth labeling
5. **Improve your ALPR system** with better data!

---

**Recommendation**: Start with the UFPR-ALPR dataset for the best quality, then supplement with YouTube videos for variety.
