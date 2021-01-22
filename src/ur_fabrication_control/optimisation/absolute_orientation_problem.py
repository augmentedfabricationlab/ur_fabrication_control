'''
. . . . . . . . . . . . . . . . . . . . . 
.                                       .
.    <<      ><      ><       >< <<     .
.    < ><   ><<     ><<<    ><    ><<   .
.    << >< > ><    ><  ><     ><        .  
.    <<  ><  ><   ><<<<<><      ><      .
.    <<      >< ><<     ><< ><    ><<   .
.    <<      ><><<       ><<  >< <<     .
.                                       .
.             DFAB 2016/17              .
. . . . . . . . . . . . . . . . . . . . . 

Created on 22.03.2017

@author: rustr
'''

import numpy as np
from _ast import Num

def find_umeyama_transformation_matrix(A, B):
    
    """
    Rigid alignment of two sets of points (A, B) in k-dimensional Euclidean space.  
    Given two sets of points in correspondence, this function computes the 
    scaling, rotation, and translation that define the transform TR that 
    minimizes the sum of squared errors between TR(A) and its corresponding 
    points in B. This routine takes O(n k^3)-time.
    
    Inputs:
    A - a k x n matrix whose columns are points 
    B - a k x n matrix whose columns are points that correspond to the points in A
    Outputs: 
    c, R, t - the scaling, rotation matrix, and translation vector
              defining the linear map TR as 
    
                        TR(A) = c * R * A + t
    
              such that the average norm of TR(A(:, i) - B(:, i)) is minimized.
    
    References:
    https://gist.github.com/dboyliao/f7f862172ed811032ba7cc368701b1e8
    https://gist.github.com/CarloNicolini/7118015
    """
    
    assert len(A.shape) == 2, "A must be a m x n array"
    assert A.shape == B.shape, "A and B must have the same shape"
    
    N, m = A.shape
    
    meanA = A.mean(axis = 0)
    meanB = B.mean(axis = 0)
    
    deltaA = A - meanA # N x m
    deltaB = B - meanB # N x m
    
    sigmaA = (deltaA * deltaA).sum(axis = 1).mean()
    sigmaB = (deltaB * deltaB).sum(axis = 1).mean()
    
    print deltaA
    
    print deltaB
    
    cov_matrix = deltaB.T.dot(deltaA) / N
    
    U, d, V_t = np.linalg.svd(cov_matrix, full_matrices = True)
    cov_rank = np.linalg.matrix_rank(cov_matrix)
    S = np.eye(m)
    
    if cov_rank >= m - 1 and np.linalg.det(cov_matrix) < 0:
        S[m-1, m-1] = -1
    elif cov_rank < m - 1:
        raise ValueError("colinearility detected in covariance matrix:\n{}".format(cov_matrix))
    
    R = U.dot(S).dot(V_t)
    #c = (d * S.diagonal()).sum() / sigmaA
    #print "c", c
    c = 1.
    t = meanB - c*R.dot(meanA)
    
    return c * R, t

if __name__ == "__main__":
    
    import time
    plot = True
    
    
    A = np.array([[24.96448305157195, 25.321704018013179, 0.0], [29.163647676054158, -0.77310471984056939, 0.0], [9.96746653556405, 20.522658732890655, 0.0], [19.265616775488947, -2.8726870320816715, 0.0], [-5.02954998044385, 14.523852126487494, 0.0], [9.667526205243895, -6.47197099592357, 0.0]])
    B = np.array([[46.607292702992794, 74.701059681089433, 0.0], [70.357980476758385, 58.442199594350569, 0.0], [58.721737473504106, 87.453106807943442, 0.0], [78.328009931042146, 65.137024335948922, 0.0], [74.024194025728917, 96.538940385826919, 0.0], [84.877090839986721, 69.60456243092105, 0.0]])
        
    # --> working dataset 
    dataA = [[1017.121, -590.413, -766.926], [1094.404, -742.805, -770.112], [1421.433, -537.516, -767.355], [1507.644, -685.023, -770.548], [1823.396, -455.385, -767.762], [1923.546, -593.82, -770.965], [2229.307, -198.723, -777.062], [2396.457, -669.955, -777.555]]    
    dataB = [[1014.74, -590.91, -767.45], [1092.76, -743.6, -770.22], [1420.28, -537.33, -767.88], [1507.31, -685.55, -770.85], [1823.42, -454.48, -768.71], [1924.34, -593.59, -771.24], [2229.307, -198.723, -777.062], [2398.372, -669.331, -777.991]]
    
    # --> not working dataset 
    dataA =  [[-36.135, -1273.399, 8.321], [0.0, 0.0, 0.0], [49.187, -874.668, 8.534000000000001], [106.173, -468.376, 8.750999999999999], [133.328, -1251.509, 5.334], [217.033, -842.73, 5.553], [270.129, -420.269, 5.778], [499.999, -0.017999999999999999, 0.0040000000000000001]]
    dataB =  [[1014.74, -590.91, -767.45], [1092.76, -743.6, -770.22], [1420.28, -537.33, -767.88], [1507.31, -685.55, -770.85], [1823.42, -454.48, -768.71], [1924.34, -593.59, -771.24], [2229.307, -198.723, -777.062], [2398.372, -669.331, -777.991]]

    
    A = np.array(dataA)
    B = np.array(dataB)
        
    t0 = time.time()
    R, t = find_umeyama_transformation_matrix(A,B)
    print "Calculation took %f seconds." % (time.time() - t0)
    print "Rotation matrix=\n", R
    print "Translation vector=", t
    print
    
    
    A2 = np.dot(R, A.T).T + t
        
    # Find the error
    err = A2 - B
    err = np.multiply(err, err)
    err = sum(err)
    rmse = np.sqrt(err/A.shape[0])
    print "RMSE:", rmse
    
    if plot:
            
        import matplotlib.pyplot as plt
        plt.title("Absolute orientation problem 3D")
    
        # the input
        plt.plot(A[:,0], A[:,1], "o", label = "A")
        plt.plot(B[:,0], B[:,1], "o", label = "B")
        
        # the result
        plt.plot(A2[:,0], A2[:,1], "o", c = "r" ,label = "R * A + t")
        
        plt.legend(loc=2)
        plt.show()
    
    
    
    

