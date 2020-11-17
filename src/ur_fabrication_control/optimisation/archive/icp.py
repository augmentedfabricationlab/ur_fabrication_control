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
from scipy.spatial.distance import cdist

def best_fit_transform(A, B):
    '''
    Calculates the least-squares best-fit transform between corresponding 3D points A->B
    Input:
      A: Nx3 numpy array of corresponding 3D points
      B: Nx3 numpy array of corresponding 3D points
    Returns:
      T: 4x4 homogeneous transformation matrix
      R: 3x3 rotation matrix
      t: 3x1 column vector
    '''

    assert len(A) == len(B)

    # translate points to their centroids
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    AA = A - centroid_A
    BB = B - centroid_B

    # rotation matrix
    H = np.dot(AA.T, BB)
    U, S, Vt = np.linalg.svd(H)
    R = np.dot(Vt.T, U.T)

    # special reflection case
    if np.linalg.det(R) < 0:
        Vt[2,:] *= -1
        R = np.dot(Vt.T, U.T)

    # translation
    t = centroid_B.T - np.dot(R,centroid_A.T)

    # homogeneous transformation
    T = np.identity(4)
    T[0:3, 0:3] = R
    T[0:3, 3] = t

    return T, R, t

def nearest_neighbor(src, dst):
    '''
    Find the nearest (Euclidean) neighbor in dst for each point in src
    Input:
        src: Nx3 array of points
        dst: Nx3 array of points
    Output:
        distances: Euclidean distances of the nearest neighbor
        indices: dst indices of the nearest neighbor
    '''

    all_dists = cdist(src, dst, 'euclidean')
    indices = all_dists.argmin(axis=1)
    distances = all_dists[np.arange(all_dists.shape[0]), indices]
    return distances, indices

def icp(A, B, init_guess=None, max_iterations=20, tolerance=0.001):
    '''
    The Iterative Closest Point method
    Input:
        A: Nx3 numpy array of source 3D points
        B: Nx3 numpy array of destination 3D point
        init_guess: 4x4 homogeneous transformation
        max_iterations: exit algorithm after max_iterations
        tolerance: convergence criteria
    Output:
        T: final homogeneous transformation
        distances: Euclidean distances (errors) of the nearest neighbor
        
    reference: https://github.com/ClayFlannigan/icp/blob/master/icp.py
    '''

    # make points homogeneous, copy them so as to maintain the originals
    src = np.ones((4,A.shape[0]))
    dst = np.ones((4,B.shape[0]))
    src[0:3,:] = np.copy(A.T)
    dst[0:3,:] = np.copy(B.T)

    # apply the initial pose estimation
    if init_guess is not None:
        src = np.dot(init_guess, src)

    prev_error = 0

    for i in range(max_iterations):
        # find the nearest neighbours between the current source and destination points
        distances, indices = nearest_neighbor(src[0:3,:].T, dst[0:3,:].T)

        # compute the transformation between the current source and nearest destination points
        T,_,_ = best_fit_transform(src[0:3,:].T, dst[0:3,indices].T)

        # update the current source
        src = np.dot(T, src)

        # check error
        mean_error = np.sum(distances) / distances.size
        if abs(prev_error-mean_error) < tolerance:
            break
        prev_error = mean_error

    # calculate final transformation
    T,_,_ = best_fit_transform(A, src[0:3,:].T)

    return T, distances


if __name__ == "__main__":
    
    #dataA =  [[-36.135, -1273.399, 8.321], [0.0, 0.0, 0.0], [49.187, -874.668, 8.534000000000001], [106.173, -468.376, 8.750999999999999], [133.328, -1251.509, 5.334], [217.033, -842.73, 5.553], [270.129, -420.269, 5.778], [499.999, -0.017999999999999999, 0.0040000000000000001]]
    #dataB =  [[1014.74, -590.91, -767.45], [1092.76, -743.6, -770.22], [1420.28, -537.33, -767.88], [1507.31, -685.55, -770.85], [1823.42, -454.48, -768.71], [1924.34, -593.59, -771.24], [2229.307, -198.723, -777.062], [2398.372, -669.331, -777.991]]

    dataB =  [[217.065, -842.72, 6.0], [133.375, -1251.501, 6.0], [33.678, -1648.955, 6.0], [-202.497, -1524.802, 9.0], [-133.45, -1250.583, 9.0], [-49.337, -857.741, 9.0]]
    dataA =  [[24.742, -1652.137, 0.443], [-211.224, -1529.061, 3.78], [-141.752, -1253.421, 3.667], [125.177, -1253.606, 0.60599999999999998], [209.802, -843.907, 1.881], [-57.661, -858.78, 4.697]]

    A = np.array(dataA)
    B = np.array(dataB)
    
    print A.shape
    print B.shape
    print
    
    init_guess = np.array([[0.4383711467890774, 0.89879404629916704, 0.0, 2026.0682179097259], [-0.89879404629916704, 0.4383711467890774, 0.0, 567.64015907666817], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    
    #Run the icp
    #T, distances = icp(A, B, init_guess, max_iterations=20)
    T, distances = icp(A, B)
    
    
    # for pasting into Rhino
    print "T = rg.Transform.Identity"
    for i in range(4):
        for j in range(4):
            print "T.M%i%i = %f" % (i,j,T[i,j])
        print
    
    
    print T
    print distances
    
