-- Supabase Database Schema for ALPR System
-- This schema stores test runs, detections, and performance metrics

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- ===========================================================================
-- Table: test_runs
-- Tracks each video processing run
-- ===========================================================================
create table if not exists test_runs (
    id uuid primary key default uuid_generate_v4(),
    video_name text not null,
    start_time timestamp with time zone not null,
    end_time timestamp with time zone,
    total_frames integer,
    detection_method text check (detection_method in ('roboflow', 'local')),
    created_at timestamp with time zone default now()
);

-- Index for faster queries
create index idx_test_runs_video_name on test_runs(video_name);
create index idx_test_runs_created_at on test_runs(created_at desc);

-- Comments
comment on table test_runs is 'Tracks each video processing run';
comment on column test_runs.video_name is 'Name of the video file processed';
comment on column test_runs.detection_method is 'Method used for plate detection (roboflow or local)';

-- ===========================================================================
-- Table: detections
-- Individual license plate detections
-- ===========================================================================
create table if not exists detections (
    id uuid primary key default uuid_generate_v4(),
    test_run_id uuid not null references test_runs(id) on delete cascade,
    frame_number integer not null,
    vehicle_id integer not null,
    plate_text text not null,
    confidence real not null check (confidence >= 0 and confidence <= 1),
    bbox_x1 real not null,
    bbox_y1 real not null,
    bbox_x2 real not null,
    bbox_y2 real not null,
    created_at timestamp with time zone default now()
);

-- Indexes for faster queries
create index idx_detections_test_run_id on detections(test_run_id);
create index idx_detections_vehicle_id on detections(test_run_id, vehicle_id);
create index idx_detections_plate_text on detections(plate_text);
create index idx_detections_frame_number on detections(test_run_id, frame_number);

-- Comments
comment on table detections is 'Individual license plate detections from video frames';
comment on column detections.frame_number is 'Frame number where detection occurred';
comment on column detections.vehicle_id is 'Tracking ID assigned to vehicle by SORT';
comment on column detections.plate_text is 'Recognized license plate text';
comment on column detections.confidence is 'OCR confidence score (0-1)';

-- ===========================================================================
-- Table: performance_metrics
-- Performance statistics per test run
-- ===========================================================================
create table if not exists performance_metrics (
    id uuid primary key default uuid_generate_v4(),
    test_run_id uuid not null references test_runs(id) on delete cascade,
    total_vehicles integer not null default 0,
    total_plates_detected integer not null default 0,
    avg_confidence real,
    processing_fps real,
    created_at timestamp with time zone default now()
);

-- Index
create index idx_performance_metrics_test_run_id on performance_metrics(test_run_id);

-- Comments
comment on table performance_metrics is 'Performance statistics for each test run';
comment on column performance_metrics.total_vehicles is 'Total number of unique vehicles detected';
comment on column performance_metrics.total_plates_detected is 'Total number of license plates detected';
comment on column performance_metrics.avg_confidence is 'Average OCR confidence across all detections';
comment on column performance_metrics.processing_fps is 'Frames processed per second';

-- ===========================================================================
-- Useful Views
-- ===========================================================================

-- View: test_run_summary
-- Provides a summary of each test run with aggregated statistics
create or replace view test_run_summary as
select 
    tr.id,
    tr.video_name,
    tr.start_time,
    tr.end_time,
    tr.total_frames,
    tr.detection_method,
    count(distinct d.vehicle_id) as unique_vehicles,
    count(d.id) as total_detections,
    count(distinct d.plate_text) as unique_plates,
    avg(d.confidence) as avg_confidence,
    pm.processing_fps,
    extract(epoch from (tr.end_time - tr.start_time)) as processing_time_seconds
from test_runs tr
left join detections d on tr.id = d.test_run_id
left join performance_metrics pm on tr.id = pm.test_run_id
group by tr.id, tr.video_name, tr.start_time, tr.end_time, tr.total_frames, 
         tr.detection_method, pm.processing_fps;

comment on view test_run_summary is 'Summary view of test runs with aggregated statistics';

-- View: vehicle_tracking
-- Shows all detections grouped by vehicle with first and last seen frames
create or replace view vehicle_tracking as
select 
    tr.id as test_run_id,
    tr.video_name,
    d.vehicle_id,
    d.plate_text,
    min(d.frame_number) as first_frame,
    max(d.frame_number) as last_frame,
    max(d.frame_number) - min(d.frame_number) as frames_tracked,
    count(*) as detection_count,
    avg(d.confidence) as avg_confidence
from test_runs tr
join detections d on tr.id = d.test_run_id
group by tr.id, tr.video_name, d.vehicle_id, d.plate_text
order by tr.id, d.vehicle_id;

comment on view vehicle_tracking is 'Vehicle tracking information with first/last frames';

-- ===========================================================================
-- Row Level Security (RLS) Policies
-- Uncomment if you want to enable RLS
-- ===========================================================================

-- Enable RLS on tables
-- alter table test_runs enable row level security;
-- alter table detections enable row level security;
-- alter table performance_metrics enable row level security;

-- Policy: Allow all operations for authenticated users
-- create policy "Allow all for authenticated users" on test_runs
--     for all using (auth.role() = 'authenticated');

-- create policy "Allow all for authenticated users" on detections
--     for all using (auth.role() = 'authenticated');

-- create policy "Allow all for authenticated users" on performance_metrics
--     for all using (auth.role() = 'authenticated');

-- ===========================================================================
-- Helpful Functions
-- ===========================================================================

-- Function: Get test run statistics
create or replace function get_test_run_stats(run_id uuid)
returns json as $$
declare
    stats json;
begin
    select json_build_object(
        'test_run_id', tr.id,
        'video_name', tr.video_name,
        'total_frames', tr.total_frames,
        'detection_method', tr.detection_method,
        'processing_time', extract(epoch from (tr.end_time - tr.start_time)),
        'unique_vehicles', count(distinct d.vehicle_id),
        'total_detections', count(d.id),
        'unique_plates', count(distinct d.plate_text),
        'avg_confidence', avg(d.confidence),
        'detection_rate', count(d.id)::float / nullif(tr.total_frames, 0)
    ) into stats
    from test_runs tr
    left join detections d on tr.id = d.test_run_id
    where tr.id = run_id
    group by tr.id, tr.video_name, tr.total_frames, tr.detection_method, tr.start_time, tr.end_time;
    
    return stats;
end;
$$ language plpgsql;

comment on function get_test_run_stats is 'Get comprehensive statistics for a test run';

-- ===========================================================================
-- Sample Queries
-- ===========================================================================

-- Get all test runs ordered by date
-- SELECT * FROM test_run_summary ORDER BY start_time DESC;

-- Get detections for a specific vehicle
-- SELECT * FROM detections WHERE test_run_id = 'your-run-id' AND vehicle_id = 1;

-- Get most common license plates across all runs
-- SELECT plate_text, COUNT(*) as occurrences 
-- FROM detections 
-- GROUP BY plate_text 
-- ORDER BY occurrences DESC;

-- Get average confidence by detection method
-- SELECT detection_method, AVG(avg_confidence) as avg_conf
-- FROM test_run_summary
-- GROUP BY detection_method;

-- Get test runs with low confidence detections
-- SELECT tr.video_name, AVG(d.confidence) as avg_conf
-- FROM test_runs tr
-- JOIN detections d ON tr.id = d.test_run_id
-- GROUP BY tr.id, tr.video_name
-- HAVING AVG(d.confidence) < 0.7;

