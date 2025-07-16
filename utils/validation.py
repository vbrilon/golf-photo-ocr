"""
Validation utilities for configuration and bounding boxes.
"""

from typing import List, Dict, Any


def validate_bbox(bbox: List, metric_name: str) -> None:
    """
    Validate bounding box coordinates
    
    Args:
        bbox: Bounding box in format [x, y, width, height]
        metric_name: Name of the metric for error reporting
        
    Raises:
        ValueError: If bounding box is invalid
    """
    # Check format
    if not isinstance(bbox, list):
        raise ValueError(f"Invalid bbox for {metric_name}: must be a list, got {type(bbox).__name__}")
    
    if len(bbox) != 4:
        raise ValueError(f"Invalid bbox format for {metric_name}: must be [x, y, width, height], got {len(bbox)} elements")
    
    # Check all elements are numbers
    for i, coord in enumerate(bbox):
        if not isinstance(coord, (int, float)):
            coord_names = ["x", "y", "width", "height"]
            raise ValueError(f"Invalid bbox for {metric_name}: {coord_names[i]} must be a number, got {type(coord).__name__}")
    
    x, y, width, height = bbox
    
    # Check non-negative coordinates
    if x < 0:
        raise ValueError(f"Invalid bbox for {metric_name}: x coordinate cannot be negative, got {x}")
    if y < 0:
        raise ValueError(f"Invalid bbox for {metric_name}: y coordinate cannot be negative, got {y}")
    
    # Check positive dimensions
    if width <= 0:
        raise ValueError(f"Invalid bbox for {metric_name}: width must be positive, got {width}")
    if height <= 0:
        raise ValueError(f"Invalid bbox for {metric_name}: height must be positive, got {height}")
    
    # Check reasonable maximum values (golf app screenshots are typically ~2048x1536 or similar)
    max_dimension = 10000  # Generous upper bound
    if x > max_dimension:
        raise ValueError(f"Invalid bbox for {metric_name}: x coordinate too large ({x} > {max_dimension})")
    if y > max_dimension:
        raise ValueError(f"Invalid bbox for {metric_name}: y coordinate too large ({y} > {max_dimension})")
    if width > max_dimension:
        raise ValueError(f"Invalid bbox for {metric_name}: width too large ({width} > {max_dimension})")
    if height > max_dimension:
        raise ValueError(f"Invalid bbox for {metric_name}: height too large ({height} > {max_dimension})")
    
    # Check that bounding box doesn't extend beyond reasonable image bounds
    if x + width > max_dimension:
        raise ValueError(f"Invalid bbox for {metric_name}: bounding box extends beyond reasonable image width (x + width = {x + width} > {max_dimension})")
    if y + height > max_dimension:
        raise ValueError(f"Invalid bbox for {metric_name}: bounding box extends beyond reasonable image height (y + height = {y + height} > {max_dimension})")


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration structure and content
    
    Args:
        config: Loaded configuration dictionary
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate required sections
    if "metrics" not in config:
        raise ValueError("Configuration file must contain 'metrics' section")
    
    metrics = config["metrics"]
    if not isinstance(metrics, dict):
        raise ValueError("Configuration 'metrics' section must be a dictionary")
    
    # Define required metrics for core functionality
    required_metrics = ["DISTANCE_TO_PIN", "CARRY", "FROM_PIN", "STROKES_GAINED"]
    
    # Validate required metrics exist and have proper structure
    for metric in required_metrics:
        if metric not in metrics:
            raise ValueError(f"Missing required metric in configuration: {metric}")
        if not isinstance(metrics[metric], dict):
            raise ValueError(f"Metric '{metric}' must be a dictionary")
        if "bbox" not in metrics[metric]:
            raise ValueError(f"Missing 'bbox' for metric: {metric}")
        
        # Validate bounding box coordinates
        validate_bbox(metrics[metric]["bbox"], metric)
    
    # Validate all metrics (including optional ones) have valid bounding boxes
    for metric_name, metric_config in metrics.items():
        if not isinstance(metric_config, dict):
            raise ValueError(f"Metric '{metric_name}' must be a dictionary")
        if "bbox" in metric_config:
            validate_bbox(metric_config["bbox"], metric_name)