#include <stdio.h>
#include <stdlib.h>
#include <time.h>

/**
 * A simple CPU-intensive C function for benchmarking.
 * It multiplies two N x N matrices.
 * In a real SeBS deployment, this would be wrapped in a handler
 * that parses the input JSON event.
 */

#define N 100 // Matrix size (100x100)

void matrix_multiply() {
    int i, j, k;
    double sum = 0.0;

    // Allocate memory for matrices
    double *A = (double *)malloc(N * N * sizeof(double));
    double *B = (double *)malloc(N * N * sizeof(double));
    double *C = (double *)malloc(N * N * sizeof(double));

    // Initialize with dummy data
    for (i = 0; i < N * N; i++) {
        A[i] = 1.0;
        B[i] = 2.0;
    }

    // The O(N^3) Compute Heavy Task
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            sum = 0.0;
            for (k = 0; k < N; k++) {
                sum += A[i * N + k] * B[k * N + j];
            }
            C[i * N + j] = sum;
        }
    }

    printf("{ \"status\": \"success\", \"result\": %f }", C[0]);

    free(A);
    free(B);
    free(C);
}

int main() {
    // In AWS Lambda, this main function would be invoked by the runtime shim
    matrix_multiply();
    return 0;
}
