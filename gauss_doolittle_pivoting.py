def gausslu(A, b, n):
    l = [None]*n
    s = [None]*n
    for i in range(n):
        l[i] = i
        smax = 0.0
        for j in range(n):
            if abs(A[i][j]) > smax:
                smax = abs(A[i][j])
        s[i] = smax

    for i in range(n):
        if i<n-1:
            rmax = 0.0
            for j in range(i, n):
                ratio = abs(A[l[j]][i]) / s[l[j]]
                if ratio > rmax:
                    rmax = ratio
                    rindex = j
            tmp = l[i]
            l[i] = l[rindex]
            l[rindex] = tmp

        pi = l[i]
        for j in range(i, n):
            dtmp = A[pi][j]
            for k in range(i):
                dtmp -= A[pi][k] * A[l[k]][j]
            A[pi][j] = dtmp

        for r in range(i+1, n):
            pr = l[r]
            dtmp = A[pr][i]
            for k in range(i):
                dtmp -= A[pr][k] * A[l[k]][i]
            A[pr][i] = dtmp / A[pi][i]

    z = [None]*n
    for i in range(n):
        pi = l[i]
        dtmp = b[pi]
        for j in range(i):
            dtmp -= A[pi][j] * z[j]

        z[i] = dtmp

    x = [None]*n
    for j in range(n-1, -1, -1):
        dtmp = z[j]
        for k in range(j+1, n):
            dtmp -= A[l[j]][k] * x[k]
        x[j] = dtmp / A[l[j]][j]

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
