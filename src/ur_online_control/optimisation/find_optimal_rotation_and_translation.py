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

Created on 16.09.2016

@author: rustr
'''

import numpy as np

def find_optimal_rotation_and_translation(A, B):
    '''
    The original script was found on http://nghiaho.com/?page_id=671.
    The input are 2 data sets (Nx3 matrix of points), where the functions 
    returns the optimal rotation (R = 3x3 rotation matrix) and translation
    (t = 3x1 column vector) between the two.
    '''
    
    assert len(A) == len(B)

    num = A.shape[0] # number of points
    
    centroid_A = np.mean(A, axis=0)
    centroid_B = np.mean(B, axis=0)
    
    AA = A - np.tile(centroid_A, (num, 1))
    BB = B - np.tile(centroid_B, (num, 1))

    # dot is matrix multiplication for array
    H = np.transpose(AA) * BB

    U, S, Vt = np.linalg.svd(H)

    R = Vt.T * U.T

    # special reflection case
    if np.linalg.det(R) < 0:
        print "Reflection detected"
        Vt[2,:] *= -1
        R = Vt.T * U.T

    t = -R * centroid_A.T + centroid_B.T

    return R, t

if __name__ == "__main__":
    
    import matplotlib.pyplot as plt
    plt.title("Find optimal rotation R and translation t in 3D")

    
    #dataA = [[24.96448305157195, 25.321704018013179, 0.0], [29.163647676054158, -0.77310471984056939, 0.0], [9.96746653556405, 20.522658732890655, 0.0], [19.265616775488947, -2.8726870320816715, 0.0], [-5.02954998044385, 14.523852126487494, 0.0], [9.667526205243895, -6.47197099592357, 0.0]]
    #dataB = [[46.607292702992794, 74.701059681089433, 0.0], [70.357980476758385, 58.442199594350569, 0.0], [58.721737473504106, 87.453106807943442, 0.0], [78.328009931042146, 65.137024335948922, 0.0], [74.024194025728917, 96.538940385826919, 0.0], [84.877090839986721, 69.60456243092105, 0.0]]
    #dataA = CAD
    #dataB = mtip
    #dataA = [[270.129, -420.269, 5.778], [217.033, -842.73, 5.553], [133.328, -1251.509, 5.334], [-36.135, -1273.399, 8.321], [49.187, -874.668, 8.534], [106.173, -468.376, 8.751], [0.0, 0.0, 0.0], [499.999, -0.018, 0.004]]
    #dataA = [[-420.269, -270.129, 5.778], [-842.73, -217.033, 5.553], [-1251.509, -133.328, 5.334], [-1273.399, 36.135, 8.321], [-874.668, -49.187, 8.534000000000001], [-468.376, -106.173, 8.750999999999999], [0.0, 0.0, 0.0], [-0.017999999999999999, -499.999, 0.0040000000000000001]]
    
    
    # =====================================================================
    # two datasets, same points, points only in different order
    
    # =====================================================================
    # --> working dataset
    dataA = [[1017.121, -590.413, -766.926], [1094.404, -742.805, -770.112], [1421.433, -537.516, -767.355], [1507.644, -685.023, -770.548], [1823.396, -455.385, -767.762], [1923.546, -593.82, -770.965], [2229.307, -198.723, -777.062], [2396.457, -669.955, -777.555]]    
    dataB = [[1014.74, -590.91, -767.45], [1092.76, -743.6, -770.22], [1420.28, -537.33, -767.88], [1507.31, -685.55, -770.85], [1823.42, -454.48, -768.71], [1924.34, -593.59, -771.24], [2229.307, -198.723, -777.062], [2398.372, -669.331, -777.991]]
    
    # =====================================================================
    # --> not working dataset 
    #dataA =  [[-36.135, -1273.399, 8.321], [0.0, 0.0, 0.0], [49.187, -874.668, 8.534000000000001], [106.173, -468.376, 8.750999999999999], [133.328, -1251.509, 5.334], [217.033, -842.73, 5.553], [270.129, -420.269, 5.778], [499.999, -0.017999999999999999, 0.0040000000000000001]]
    #dataB =  [[1014.74, -590.91, -767.45], [1092.76, -743.6, -770.22], [1420.28, -537.33, -767.88], [1507.31, -685.55, -770.85], [1823.42, -454.48, -768.71], [1924.34, -593.59, -771.24], [2229.307, -198.723, -777.062], [2398.372, -669.331, -777.991]]
    
    num = len(dataA)
    
    A = np.matrix(dataA)
    B = np.matrix(dataB)

        
    R, t = find_optimal_rotation_and_translation(A, B)
    
    A2 = (np.dot(R, A.T) + np.tile(t, (1, num))).T
        
    # Find the error
    err = A2 - B
    
    err = np.multiply(err, err)
    err = sum(err)
    rmse = np.sqrt(err/num);
    
    print "Points A"
    print A
    print ""
    
    print "Points B"
    print B
    print ""
    
    print "Rotation"
    print R
    print ""
    
    print "Translation"
    print t
    print ""
    
    print "RMSE:", rmse
    print "If RMSE is near zero, the function is correct!"
    
    def matrix_column(M, i):
        return np.array(M[:,i].T)[0]
    

    # the input
    plt.plot(matrix_column(A, 0), matrix_column(A, 1), "o", label = "A")
    plt.plot(matrix_column(B, 0), matrix_column(B, 1), "o", label = "B")
    
    # the result
    plt.plot(matrix_column(A2, 0), matrix_column(A2, 1), "o", c = "r" ,label = "R * A + t")
    
    plt.legend(loc=2)
    plt.show()
    
    