
size_generators = {
    'test': 100,
    'small': 200,
    'large': 500
}

def generate_input(data_dir, size, benchmarks_bucket, input_paths, output_paths, upload_func, nosql_func):
    input_config = {'matrix_size': size_generators[size]}
    return input_config
