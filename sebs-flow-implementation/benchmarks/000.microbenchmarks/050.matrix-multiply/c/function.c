#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 100  // 100x100 matrices

// Matrix multiplication: C = A * B
void matrix_multiply(double** A, double** B, double** C, int size) {
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            C[i][j] = 0.0;
            for (int k = 0; k < size; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

// Allocate 2D matrix
double** allocate_matrix(int size) {
    double** matrix = (double**)malloc(size * sizeof(double*));
    for (int i = 0; i < size; i++) {
        matrix[i] = (double*)malloc(size * sizeof(double));
    }
    return matrix;
}

// Free 2D matrix
void free_matrix(double** matrix, int size) {
    for (int i = 0; i < size; i++) {
        free(matrix[i]);
    }
    free(matrix);
}

// Initialize matrix with random values
void initialize_matrix(double** matrix, int size) {
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            matrix[i][j] = (double)(rand() % 100) / 10.0;
        }
    }
}

int handler(int matrix_size) {
    srand(time(NULL));
    
    // Use matrix_size from input or default to N
    int size = (matrix_size > 0 && matrix_size <= 1000) ? matrix_size : N;
    
    // Allocate matrices
    double** A = allocate_matrix(size);
    double** B = allocate_matrix(size);
    double** C = allocate_matrix(size);
    
    // Initialize matrices A and B
    initialize_matrix(A, size);
    initialize_matrix(B, size);
    
    // Perform multiplication
    clock_t start = clock();
    matrix_multiply(A, B, C, size);
    clock_t end = clock();
    
    double time_spent = (double)(end - start) / CLOCKS_PER_SEC;
    
    // Calculate checksum (simple validation)
    double checksum = 0.0;
    for (int i = 0; i < size; i++) {
        checksum += C[i][i];  // Sum diagonal elements
    }
    
    // Free memory
    free_matrix(A, size);
    free_matrix(B, size);
    free_matrix(C, size);
    
    // Print JSON result for serverless compatibility
    printf("{\"status\": \"success\", \"matrix_size\": %d, \"checksum\": %.6f, \"compute_time_ms\": %.2f}\n", 
           size, checksum, time_spent * 1000);
    
    return 0;
}

// Main entry point (for local testing)
int main() {
    return handler(N);
}
