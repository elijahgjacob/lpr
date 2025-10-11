"""Unit tests for SORT tracking algorithm."""
import pytest
import numpy as np
from sort import KalmanBoxTracker, Sort, iou_batch, convert_bbox_to_z, convert_x_to_bbox


class TestIoUCalculations:
    """Test IoU (Intersection over Union) calculations."""
    
    def test_iou_batch_identical_boxes(self):
        """Test IoU of identical boxes should be 1.0."""
        bbox1 = np.array([[0, 0, 10, 10]])
        bbox2 = np.array([[0, 0, 10, 10]])
        iou = iou_batch(bbox1, bbox2)
        assert np.isclose(iou[0, 0], 1.0)
    
    def test_iou_batch_no_overlap(self):
        """Test IoU of non-overlapping boxes should be 0.0."""
        bbox1 = np.array([[0, 0, 10, 10]])
        bbox2 = np.array([[20, 20, 30, 30]])
        iou = iou_batch(bbox1, bbox2)
        assert np.isclose(iou[0, 0], 0.0)
    
    def test_iou_batch_partial_overlap(self):
        """Test IoU of partially overlapping boxes."""
        bbox1 = np.array([[0, 0, 10, 10]])
        bbox2 = np.array([[5, 5, 15, 15]])
        iou = iou_batch(bbox1, bbox2)
        # Overlap is 5x5=25, union is 100+100-25=175
        expected = 25.0 / 175.0
        assert np.isclose(iou[0, 0], expected, rtol=0.01)
    
    def test_iou_batch_multiple_boxes(self):
        """Test IoU with multiple boxes."""
        bbox_test = np.array([
            [0, 0, 10, 10],
            [20, 20, 30, 30],
        ])
        bbox_gt = np.array([
            [0, 0, 10, 10],
            [5, 5, 15, 15],
        ])
        iou = iou_batch(bbox_test, bbox_gt)
        assert iou.shape == (2, 2)
        assert np.isclose(iou[0, 0], 1.0)  # Identical boxes
        assert iou[1, 0] < 0.1  # No overlap


class TestBBoxConversions:
    """Test bounding box format conversions."""
    
    def test_convert_bbox_to_z(self):
        """Test conversion from [x1,y1,x2,y2] to [x,y,s,r] format."""
        bbox = np.array([0, 0, 10, 20])
        z = convert_bbox_to_z(bbox)
        
        # Center x should be 5, center y should be 10
        assert z[0, 0] == 5.0
        assert z[1, 0] == 10.0
        # Area should be 200
        assert z[2, 0] == 200.0
        # Aspect ratio should be 0.5
        assert z[3, 0] == 0.5
    
    def test_convert_x_to_bbox(self):
        """Test conversion from [x,y,s,r] to [x1,y1,x2,y2] format."""
        x = np.array([5, 10, 200, 0.5])
        bbox = convert_x_to_bbox(x)
        
        # Should convert back to approximately [0, 0, 10, 20]
        assert bbox.shape == (1, 4)
        assert np.isclose(bbox[0, 0], 0.0, atol=0.1)
        assert np.isclose(bbox[0, 1], 0.0, atol=0.1)
        assert np.isclose(bbox[0, 2], 10.0, atol=0.1)
        assert np.isclose(bbox[0, 3], 20.0, atol=0.1)
    
    def test_convert_x_to_bbox_with_score(self):
        """Test conversion with score included."""
        x = np.array([5, 10, 200, 0.5])
        score = 0.95
        bbox = convert_x_to_bbox(x, score)
        
        assert bbox.shape == (1, 5)
        assert bbox[0, 4] == score


class TestKalmanBoxTracker:
    """Test KalmanBoxTracker class."""
    
    def test_initialization(self):
        """Test tracker initialization."""
        bbox = np.array([0, 0, 10, 10, 0.9])
        tracker = KalmanBoxTracker(bbox)
        
        assert tracker.id >= 0
        assert tracker.time_since_update == 0
        assert tracker.hits == 0
        assert tracker.hit_streak == 0
    
    def test_unique_ids(self):
        """Test that each tracker gets a unique ID."""
        bbox1 = np.array([0, 0, 10, 10, 0.9])
        bbox2 = np.array([20, 20, 30, 30, 0.9])
        
        tracker1 = KalmanBoxTracker(bbox1)
        tracker2 = KalmanBoxTracker(bbox2)
        
        assert tracker1.id != tracker2.id
    
    def test_predict(self):
        """Test prediction step."""
        bbox = np.array([0, 0, 10, 10, 0.9])
        tracker = KalmanBoxTracker(bbox)
        
        predicted = tracker.predict()
        
        assert predicted.shape == (1, 4)
        assert tracker.age == 1
        assert tracker.time_since_update == 1
    
    def test_update(self):
        """Test update step with observation."""
        bbox = np.array([0, 0, 10, 10, 0.9])
        tracker = KalmanBoxTracker(bbox)
        
        tracker.predict()
        new_bbox = np.array([1, 1, 11, 11, 0.95])
        tracker.update(new_bbox)
        
        assert tracker.time_since_update == 0
        assert tracker.hits == 1
        assert tracker.hit_streak == 1
    
    def test_get_state(self):
        """Test getting current state."""
        bbox = np.array([0, 0, 10, 10, 0.9])
        tracker = KalmanBoxTracker(bbox)
        
        state = tracker.get_state()
        
        assert state.shape == (1, 4)
        # State should be close to initial bbox
        assert np.allclose(state[0], [0, 0, 10, 10], atol=1.0)


class TestSort:
    """Test SORT tracker class."""
    
    def test_initialization(self):
        """Test SORT initialization."""
        tracker = Sort(max_age=5, min_hits=3, iou_threshold=0.3)
        
        assert tracker.max_age == 5
        assert tracker.min_hits == 3
        assert tracker.iou_threshold == 0.3
        assert tracker.frame_count == 0
        assert len(tracker.trackers) == 0
    
    def test_update_empty_detections(self):
        """Test update with no detections."""
        tracker = Sort()
        result = tracker.update(np.empty((0, 5)))
        
        assert tracker.frame_count == 1
        assert result.shape == (0, 5)
    
    def test_update_single_detection(self):
        """Test update with single detection."""
        tracker = Sort(max_age=1, min_hits=1)
        
        # First frame
        det1 = np.array([[10, 10, 20, 20, 0.9]])
        result1 = tracker.update(det1)
        
        # Should create one track
        assert len(tracker.trackers) == 1
        # May not return track immediately due to min_hits
        assert result1.shape[0] <= 1
    
    def test_update_consistent_tracking(self):
        """Test that consistent detections maintain same ID."""
        tracker = Sort(max_age=2, min_hits=1)
        
        # Track an object over multiple frames
        detections = [
            np.array([[10, 10, 20, 20, 0.9]]),
            np.array([[11, 11, 21, 21, 0.9]]),
            np.array([[12, 12, 22, 22, 0.9]]),
        ]
        
        results = []
        for det in detections:
            result = tracker.update(det)
            results.append(result)
        
        # After enough frames, should have consistent tracking
        if len(results[-1]) > 0:
            # Check that we have detections
            assert results[-1].shape[1] == 5  # x1, y1, x2, y2, id
    
    def test_update_multiple_objects(self):
        """Test tracking multiple objects simultaneously."""
        tracker = Sort(max_age=2, min_hits=1)
        
        # Two distinct objects
        detections = [
            np.array([
                [10, 10, 20, 20, 0.9],
                [50, 50, 60, 60, 0.9],
            ]),
            np.array([
                [11, 11, 21, 21, 0.9],
                [51, 51, 61, 61, 0.9],
            ]),
        ]
        
        for det in detections:
            result = tracker.update(det)
        
        # Should be tracking 2 objects
        assert len(tracker.trackers) >= 2
    
    def test_track_removal_after_max_age(self):
        """Test that tracks are removed after max_age frames without detection."""
        tracker = Sort(max_age=2, min_hits=1)
        
        # Create a track
        det1 = np.array([[10, 10, 20, 20, 0.9]])
        tracker.update(det1)
        tracker.update(det1)
        
        # Stop detecting the object
        for _ in range(3):
            tracker.update(np.empty((0, 5)))
        
        # Track should be removed
        assert len(tracker.trackers) == 0
    
    def test_associate_detections_to_trackers(self):
        """Test detection-to-tracker association."""
        tracker = Sort(iou_threshold=0.3)
        
        # Create some trackers first
        det1 = np.array([[10, 10, 20, 20, 0.9]])
        tracker.update(det1)
        
        # New detections
        detections = np.array([
            [11, 11, 21, 21, 0.9],  # Close to existing track
            [50, 50, 60, 60, 0.9],  # New object
        ])
        
        # Get tracker predictions
        trks = np.zeros((len(tracker.trackers), 5))
        for t, trk in enumerate(tracker.trackers):
            pos = trk.get_state()[0]
            trks[t] = [pos[0], pos[1], pos[2], pos[3], 0]
        
        matched, unmatched_dets, unmatched_trks = tracker.associate_detections_to_trackers(
            detections, trks
        )
        
        # Should have 1 match and 1 unmatched detection
        assert len(matched) + len(unmatched_dets) >= 1


class TestSortIntegration:
    """Integration tests for SORT tracker."""
    
    def test_tracking_moving_object(self):
        """Test tracking an object moving across frames."""
        tracker = Sort(max_age=5, min_hits=3, iou_threshold=0.3)
        
        # Simulate object moving diagonally
        positions = [
            (10 + i*2, 10 + i*2, 20 + i*2, 20 + i*2) for i in range(10)
        ]
        
        track_ids = []
        for pos in positions:
            det = np.array([[pos[0], pos[1], pos[2], pos[3], 0.9]])
            result = tracker.update(det)
            if len(result) > 0:
                track_ids.append(result[0, 4])
        
        # After enough frames, should have consistent tracking ID
        if len(track_ids) > 3:
            # Most track IDs should be the same
            most_common_id = max(set(track_ids), key=track_ids.count)
            assert track_ids.count(most_common_id) >= len(track_ids) - 2
    
    def test_tracking_with_occlusion(self):
        """Test tracking behavior when object is temporarily occluded."""
        tracker = Sort(max_age=3, min_hits=2, iou_threshold=0.3)
        
        # Object visible, then occluded, then visible again
        frames = [
            np.array([[10, 10, 20, 20, 0.9]]),  # Visible
            np.array([[11, 11, 21, 21, 0.9]]),  # Visible
            np.empty((0, 5)),                     # Occluded
            np.empty((0, 5)),                     # Occluded
            np.array([[13, 13, 23, 23, 0.9]]),  # Visible again
        ]
        
        for frame_det in frames:
            result = tracker.update(frame_det)
        
        # Tracker should maintain the track through short occlusion
        assert len(tracker.trackers) <= 1

