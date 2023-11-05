def gausslu(A, b, n):
    for i in range(n):
        for j in range(i, n):
            dtmp = A[i][j]
            for k in range(i):
                dtmp -= A[i][k] * A[k][j]
            A[i][j] = dtmp

        for r in range(i+1, n):
            dtmp = A[r][i]
            for k in range(i):
                dtmp -= A[r][k] * A[k][i]
            A[r][i] = dtmp / A[i][i]

    z = [None]*n
    for i in range(n):
        dtmp = b[i]
        for j in range(i):
            dtmp -= A[i][j] * z[j]

        z[i] = dtmp

    x = [None]*n
    for j in range(n-1, -1, -1):
        dtmp = z[j]
        for k in range(j+1, n):
            dtmp -= A[j][k] * x[k]
        x[j] = dtmp / A[j][j]

    print ("The solution vector is [", end="")
    for i in range(n):
        if i != (n - 1):
            print(x[i], ",", end="")
        else:
            print(x[i], "].")

if __name__ == '__main__':
    matrix0 = [[3.0, -13.0, 9.0, 3.0], [-6.0, 4.0, 1.0, -18.0], [6.0, -2.0, 2.0, 4.0], [12.0, -8.0, 6.0, 10.0]]
    vector0 = [-19.0, -34.0, 16.0, 26.0]

    matrix1 = [[3.0, 2.0, -5.0], [2.0, -3.0, 1.0], [1.0, 4.0, -1.0]]
    vector1 = [0.0, 0.0, 4.0]

    gausslu(matrix0, vector0, 4)
    gausslu(matrix1, vector1, 3)
