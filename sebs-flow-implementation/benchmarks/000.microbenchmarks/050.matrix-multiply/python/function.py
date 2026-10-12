import numpy as np
import time
import json

def matrix_multiply(size=100):
    """
    High-performance matrix multiplication using NumPy.
    Simulates O(N³) computation similar to C implementation.
    """
    # Initialize matrices with random values
    A = np.random.rand(size, size) * 10.0
    B = np.random.rand(size, size) * 10.0
    
    # Perform multiplication and measure time
    start_time = time.time()
    C = np.matmul(A, B)
    end_time = time.time()
    
    compute_time = (end_time - start_time) * 1000  # Convert to ms
    
    # Calculate checksum (sum of diagonal elements)
    checksum = np.trace(C)
    
    return {
        'status': 'success',
        'matrix_size': size,
        'checksum': float(checksum),
        'compute_time_ms': compute_time
    }

def handler(event):
    """
    Serverless function handler.
    Accepts matrix_size from event, performs multiplication.
    """
    matrix_size = event.get('matrix_size', 100)
    
    # Validate input
    if matrix_size <= 0 or matrix_size > 1000:
        return {
            'result': {
                'status': 'error',
                'message': 'matrix_size must be between 1 and 1000'
            }
        }
    
    result = matrix_multiply(matrix_size)
    return {'result': result}
