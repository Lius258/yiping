def gausslu(A, b, n):
    for i in range(n-1,0,-1):
        a = A[i][i]
        for k in range(i):
            c = A[k][i]/a
            A[k][i] = c
            for j in range(i):
                A[k][j] -= c*A[i][j]

    z = [None]*n
    for i in range(n-1, -1, -1):
        #dtmp = b[i]
        sum = 0.
        for k in range(i+1, n):
            sum += A[i][k] * z[k]
        z[i] = b[i]-sum 

    x = [None]*n
    for i in range(n):
        dtmp = z[i]
        for j in range(i):
            dtmp -= A[i][j] * x[j]

        x[i] = dtmp/A[i][i]



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
