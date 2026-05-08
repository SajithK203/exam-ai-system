"""
Data Serializer - Convert numpy/pandas types to native Python types.
Ensures data can be safely serialized to JSON without type errors.
"""

import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def sanitize(obj):
    """
    Convert numpy and pandas types to native Python types.
    
    Recursively processes dictionaries and lists to ensure
    all numpy/pandas types are converted to JSON-serializable types.
    
    Args:
        obj: Object to sanitize (can be dict, list, or scalar)
        
    Returns:
        Sanitized object with native Python types
        
    Examples:
        >>> import numpy as np
        >>> data = {"count": np.int64(42), "ratio": np.float64(3.14)}
        >>> sanitized = sanitize(data)
        >>> type(sanitized["count"])
        <class 'int'>
    """
    # Handle numpy integer types
    if isinstance(obj, np.integer):
        return int(obj)
    
    # Handle numpy floating point types
    if isinstance(obj, np.floating):
        return float(obj)
    
    # Handle numpy bool
    if isinstance(obj, np.bool_):
        return bool(obj)
    
    # Handle pandas Series
    if isinstance(obj, pd.Series):
        return sanitize(obj.to_dict())
    
    # Handle pandas DataFrame
    if isinstance(obj, pd.DataFrame):
        return sanitize(obj.to_dict(orient='records'))
    
    # Handle dictionaries recursively
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    
    # Handle lists recursively
    if isinstance(obj, list):
        return [sanitize(i) for i in obj]
    
    # Handle tuples (convert to list)
    if isinstance(obj, tuple):
        return [sanitize(i) for i in obj]
    
    # Return as-is for native Python types (str, int, float, bool, None)
    return obj


def sanitize_for_json(obj):
    """
    Alias for sanitize() - makes intent clearer in JSON contexts.
    
    Args:
        obj: Object to prepare for JSON serialization
        
    Returns:
        Sanitized object ready for json.dumps()
    """
    return sanitize(obj)
