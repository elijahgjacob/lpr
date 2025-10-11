# Migration Guide to v1.0.0

## Overview

This guide helps you migrate from pre-1.0 versions to v1.0.0, which introduces timestamp/version tracking and batch Supabase uploads.

---

## 🔄 Breaking Changes

### 1. CSV Output Format

**Added Columns:**
- `Timestamp` (ISO 8601 format)
- `Version` (release version string)

**Impact**: Any scripts parsing CSV output need to handle 15 columns instead of 13.

### 2. Supabase Schema

**New Fields Required:**
- `timestamp` (TIMESTAMPTZ)
- `version` (VARCHAR(20))

**Impact**: Existing Supabase tables need schema update.

### 3. Upload Behavior

**Changed**: Individual inserts → Bulk batch upload

**Impact**: 
- Faster processing
- Detections appear all at once at end of run
- Requires `bulk_upload_detections()` call

---

## 📋 Migration Steps

### Step 1: Backup Existing Data

```bash
# Backup CSV files
cp -r results/ results_backup_$(date +%Y%m%d)/

# Backup Supabase (SQL)
# In Supabase Dashboard → Database → Backups
```

### Step 2: Update Code

```bash
# Pull latest code
git checkout feature/enhanced-tracking-and-progress
git pull origin feature/enhanced-tracking-and-progress

# Update dependencies (if any new ones)
pip install -r requirements.txt
```

### Step 3: Update Supabase Schema

```sql
-- Connect to your Supabase project
-- Run in SQL Editor

-- Add new columns to detections table
ALTER TABLE detections 
ADD COLUMN IF NOT EXISTS timestamp TIMESTAMPTZ DEFAULT NOW();

ALTER TABLE detections 
ADD COLUMN IF NOT EXISTS version VARCHAR(20) DEFAULT '1.0.0';

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp);
CREATE INDEX IF NOT EXISTS idx_detections_version ON detections(version);

-- Update existing rows with default values
UPDATE detections 
SET 
    timestamp = COALESCE(created_at, NOW()),
    version = '0.9.0'  -- Mark as pre-1.0 data
WHERE timestamp IS NULL;

-- Verify schema
SELECT 
    column_name, 
    data_type, 
    is_nullable 
FROM information_schema.columns 
WHERE table_name = 'detections';
```

### Step 4: Update CSV Parsing Scripts

**Before (Old Format):**

```python
import csv

with open('detections.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)  # 13 columns
    
    for row in reader:
        frame, vehicle_id, plate_text, confidence = row[0], row[1], row[2], row[3]
        vehicle_bbox = tuple(map(float, row[4:8]))
        plate_bbox = tuple(map(float, row[8:12]))
        # ... process
```

**After (New Format):**

```python
import csv
from datetime import datetime

with open('detections.csv', 'r') as f:
    reader = csv.DictReader(f)  # Use DictReader for easier access
    
    for row in reader:
        frame = int(row['Frame'])
        vehicle_id = int(row['Vehicle_ID'])
        plate_text = row['Plate_Text']
        confidence = float(row['Confidence'])
        
        vehicle_bbox = (
            float(row['Vehicle_X1']),
            float(row['Vehicle_Y1']),
            float(row['Vehicle_X2']),
            float(row['Vehicle_Y2'])
        )
        
        plate_bbox = (
            float(row['Plate_X1']),
            float(row['Plate_Y1']),
            float(row['Plate_X2']),
            float(row['Plate_Y2'])
        )
        
        # New fields
        timestamp = datetime.fromisoformat(row['Timestamp'])
        version = row['Version']
        
        # ... process
```

### Step 5: Test Migration

```bash
# Run on a small test video
python main.py \
  --video test_video.mp4 \
  --output results/migration_test.csv \
  --max-frames 100

# Verify CSV has 15 columns
head -1 results/migration_test.csv

# Should output:
# Frame,Vehicle_ID,Plate_Text,Confidence,...,Timestamp,Version

# Check Supabase data
# Query in Supabase dashboard:
SELECT * FROM detections ORDER BY timestamp DESC LIMIT 5;
```

---

## 🔧 Migrating Existing CSV Files

### Python Migration Script

```python
import csv
from datetime import datetime, timedelta

def migrate_csv(input_file, output_file, base_timestamp=None):
    """
    Migrate old CSV format to new format with timestamp and version.
    
    Args:
        input_file: Path to old CSV file
        output_file: Path to new CSV file
        base_timestamp: Starting timestamp (defaults to now)
    """
    if base_timestamp is None:
        base_timestamp = datetime.now()
    
    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
    
    # New header
    new_fieldnames = list(rows[0].keys()) + ['Timestamp', 'Version']
    
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=new_fieldnames)
        writer.writeheader()
        
        for i, row in enumerate(rows):
            # Add incremental timestamp (assuming 30 FPS)
            frame_num = int(row['Frame'])
            timestamp = base_timestamp + timedelta(seconds=frame_num/30.0)
            
            row['Timestamp'] = timestamp.isoformat()
            row['Version'] = '0.9.0'  # Mark as migrated
            
            writer.writerow(row)
    
    print(f"✓ Migrated {len(rows)} rows from {input_file} to {output_file}")

# Usage
migrate_csv('results/old_detections.csv', 'results/migrated_detections.csv')
```

### Batch Migration Script

```bash
#!/bin/bash
# migrate_all_csvs.sh

# Migrate all CSV files in results directory

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for file in results/*.csv; do
    if [[ ! $file =~ _migrated\.csv$ ]]; then
        base=$(basename "$file" .csv)
        output="results/${base}_migrated.csv"
        
        echo "Migrating $file to $output..."
        python3 << EOF
from migrate_csv import migrate_csv
migrate_csv('$file', '$output')
EOF
    fi
done

echo "✓ All CSV files migrated!"
```

---

## 🗄️ Migrating Supabase Data

### Add Timestamp to Existing Records

```sql
-- Option 1: Use created_at timestamp
UPDATE detections 
SET timestamp = created_at
WHERE timestamp IS NULL;

-- Option 2: Calculate from frame number and test run
UPDATE detections d
SET timestamp = tr.started_at + (d.frame_number / 30.0) * INTERVAL '1 second'
FROM test_runs tr
WHERE d.test_run_id = tr.id
  AND d.timestamp IS NULL;
```

### Add Version to Historical Data

```sql
-- Mark all pre-1.0 data
UPDATE detections 
SET version = '0.9.0'
WHERE version IS NULL;

-- Or set based on test_run date
UPDATE detections 
SET version = CASE 
    WHEN created_at < '2025-10-11' THEN '0.9.0'
    ELSE '1.0.0'
END
WHERE version IS NULL;
```

### Verify Migration

```sql
-- Check for NULL values
SELECT COUNT(*) as null_timestamps
FROM detections
WHERE timestamp IS NULL;

SELECT COUNT(*) as null_versions
FROM detections
WHERE version IS NULL;

-- Should both return 0

-- Check data distribution
SELECT 
    version,
    COUNT(*) as count,
    MIN(timestamp) as earliest,
    MAX(timestamp) as latest
FROM detections
GROUP BY version
ORDER BY version;
```

---

## ⚙️ Updating Integration Code

### REST API Integrations

**Before:**

```python
import requests

# Old endpoint expectations
detections = requests.get(f"{SUPABASE_URL}/rest/v1/detections?test_run_id=eq.{run_id}").json()

for det in detections:
    frame = det['frame_number']
    plate = det['plate_text']
    # ... process
```

**After:**

```python
import requests
from datetime import datetime

# New fields available
detections = requests.get(f"{SUPABASE_URL}/rest/v1/detections?test_run_id=eq.{run_id}").json()

for det in detections:
    frame = det['frame_number']
    plate = det['plate_text']
    
    # New fields
    timestamp = datetime.fromisoformat(det['timestamp'])
    version = det['version']
    
    # ... process
```

### Analytics Queries

**New capabilities with timestamp:**

```sql
-- Detections by hour
SELECT 
    DATE_TRUNC('hour', timestamp) as hour,
    COUNT(*) as detections
FROM detections
GROUP BY hour
ORDER BY hour;

-- Detections by version
SELECT 
    version,
    COUNT(*) as total_detections,
    COUNT(DISTINCT vehicle_id) as unique_vehicles,
    AVG(confidence) as avg_confidence
FROM detections
GROUP BY version;

-- Time-based analysis
SELECT 
    plate_text,
    MIN(timestamp) as first_seen,
    MAX(timestamp) as last_seen,
    MAX(timestamp) - MIN(timestamp) as duration
FROM detections
WHERE test_run_id = 'your-run-id'
GROUP BY plate_text;
```

---

## 🧪 Testing Your Migration

### Test Checklist

- [ ] Supabase schema updated (timestamp, version columns exist)
- [ ] Existing data has non-NULL timestamp and version
- [ ] New CSV files have 15 columns (including Timestamp, Version)
- [ ] Batch upload works (detections appear after processing completes)
- [ ] Progress bar displays correctly
- [ ] CSV parsing scripts updated
- [ ] API integrations handle new fields
- [ ] Analytics queries work with timestamp

### Validation Script

```python
import csv
from datetime import datetime
from supabase import create_client

def validate_migration():
    """Validate successful migration to v1.0.0"""
    
    errors = []
    
    # Check CSV format
    try:
        with open('results/test_output.csv', 'r') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            if 'Timestamp' not in headers:
                errors.append("CSV missing 'Timestamp' column")
            if 'Version' not in headers:
                errors.append("CSV missing 'Version' column")
            if len(headers) != 15:
                errors.append(f"CSV has {len(headers)} columns, expected 15")
                
            # Check first row
            row = next(reader)
            try:
                datetime.fromisoformat(row['Timestamp'])
            except:
                errors.append("Invalid timestamp format in CSV")
                
    except Exception as e:
        errors.append(f"CSV validation error: {e}")
    
    # Check Supabase
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Check schema
        result = supabase.table('detections').select('timestamp,version').limit(1).execute()
        
        if not result.data:
            errors.append("No data in detections table")
        else:
            row = result.data[0]
            if 'timestamp' not in row:
                errors.append("Supabase missing 'timestamp' field")
            if 'version' not in row:
                errors.append("Supabase missing 'version' field")
                
    except Exception as e:
        errors.append(f"Supabase validation error: {e}")
    
    # Report
    if errors:
        print("❌ Migration validation failed:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ Migration validation passed!")
        return True

if __name__ == '__main__':
    validate_migration()
```

---

## 🔄 Rollback Procedure

If you need to rollback:

### 1. Restore Code

```bash
# Switch back to previous version
git checkout main  # or your previous stable branch
```

### 2. Restore Supabase Schema (Optional)

```sql
-- Remove new columns if needed
ALTER TABLE detections 
DROP COLUMN IF EXISTS timestamp,
DROP COLUMN IF EXISTS version;

-- Restore from backup if necessary
-- (Use Supabase Dashboard → Database → Backups)
```

### 3. Restore CSV Files

```bash
# Restore from backup
cp -r results_backup_YYYYMMDD/* results/
```

---

## 📞 Support

If you encounter issues during migration:

1. **Check logs**: Review terminal output for errors
2. **Validate schema**: Ensure Supabase columns exist
3. **Test with sample**: Run on small video first
4. **Open issue**: Report bugs on GitHub

---

## 📚 Additional Resources

- **Configuration Guide**: `docs/CONFIGURATION_V1.md`
- **Changelog**: `CHANGELOG.md`
- **Schema Reference**: `supabase_schema.sql`

---

**Version**: 1.0.0  
**Last Updated**: October 11, 2025  
**Maintainer**: ALPR System Contributors

