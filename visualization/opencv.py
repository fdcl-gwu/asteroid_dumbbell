"""Module to test image processing of simulated imagery

OpenCV 3.2.0 Examples

Follows the documentation 

.. [1] http://docs.opencv.org/3.2.0/d6/d00/tutorial_py_root.html
"""

import cv2
import numpy as np
import sys
import pdb

import matplotlib.pyplot as plt
import matplotlib.image as mpimage

import os

# get all image files in the directory
image_path = 'blender'
image_files = [f for f in os.listdir('./visualization/blender') if
               os.path.isfile(os.path.join('./visualization/blender', f))]
image_files = sorted(image_files, key=lambda x:int(x.split('.')[0][-2:]))
image_files = [os.path.join('./visualization/blender/', f) for f in image_files]
index = 19
def harris_corner_detector(filename=image_files[index], plot=False):
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray, 2, 3, 0.04)

    # result is dilated for marking the corners
    dst = cv2.dilate(dst, None)

    # threshold for an optimal value
    corner_test = dst > 0.01 * dst.max()
    corners = np.asarray(np.where(corner_test)).T
    
    if plot:
        img[corner_test] = [0, 0, 255]
        imgplot = plt.imshow(img)
        plt.show()
    
    return np.vstack((corners[:,1], corners[:,0])).T


def refined_harris_corner_detector(filename=image_files[index], plot=False):
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # find the Harris corners
    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray, 2, 3, 0.04)
    dst = cv2.dilate(dst, None)
    ret, dst = cv2.threshold(dst, 0.01 * dst.max(), 255, 0)
    dst = np.uint8(dst)

    # find the centroids
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)

    # define the criteria to stop and refine the corners
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    corners = cv2.cornerSubPix(gray, np.float32(centroids), (5, 5), (-1, -1), criteria)

    # now draw everything to a plot
    res = np.hstack((centroids, corners))
    res = np.int0(res)
    img[res[:, 1], res[:, 0]] = [0, 0, 255]
    img[res[:, 3], res[:, 2]] = [0, 255, 0]

    if plot:
        plt.imshow(img)
        plt.show()

    return corners

def shi_tomasi_corner_detector(filename=image_files[index], num_features=25, plot=False):
    """
    Output :
        corners - pixel locations of 'good' features to track
    """

    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    corners = cv2.goodFeaturesToTrack(gray, num_features, 0.01, 10)
    corners = np.int0(corners)

    if plot:
        for i in corners:
            x, y = i.ravel()
            cv2.circle(img, (x,y), 3, 255, -1)

        plt.imshow(img)
        plt.show()

    return np.squeeze(corners)

def sift(filename=image_files[index], plot=False):
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    sift = cv2.xfeatures2d.SIFT_create()
    kp, des = sift.detectAndCompute(gray, None)

    if plot:
        img = cv2.drawKeypoints(gray, kp, img, flags=0)
        plt.imshow(img)
        plt.show()
    
    corners = []
    for point in kp:
        x, y = point.pt
        corners.append([x, y])

    return kp, des, np.array(corners)

def surf(filename=image_files[index], plot=False):
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    surf = cv2.xfeatures2d.SURF_create(400)
    
    kp, des = surf.detectAndCompute(gray, None)

    corners = []
    for point in kp:
        x, y = point.pt
        corners.append([x, y])

    return np.array(corners)

def orb(filename=image_files[index], plot=False):
    img = cv2.imread(filename)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    orb = cv2.ORB_create()
    kp, des = orb.detectAndCompute(gray, None)
   
    if plot:
        img2 = img
        img = cv2.drawKeypoints(gray, kp, img, color=(0, 255, 0), flags=0)
        plt.figure()
        plt.imshow(img2)
        plt.show()

    corners = []
    for point in kp:
        x, y = point.pt
        corners.append([x, y])

    return kp, des, np.array(corners)

def fast(filename=image_files[index], plot=False):
    """FAST feature detector
    """

    img = cv2.imread(filename)

    fast = cv2.FastFeatureDetector_create()

    kp = fast.detect(img, None)

    if plot:
        img2 = cv2.drawKeypoints(img, kp, None, color=(255, 0, 0))

        plt.figure()
        plt.imshow(img2)
        plt.show()

    corners = []
    for point in kp:
        x, y = point.pt
        corners.append([x, y])

    return np.array(corners)

def brief(filename=image_files[index]):
    """Get feature descriptors faster 
    """

    img = cv2.imread(filename)

    star = cv2.xfeatures2d.StarDetector_create()

    brief = cv2.xfeatures2d.BriefDescriptorExtractor_create()

    kp = star.detect(img, None)

    kp, des = brief.compute(img, kp)

    corners = []
    for point in kp:
        x, y = point.pt
        corners.append([x, y])

    return np.array(corners)

def compare_feature_detection(filename=image_files[index]):
    corners_harris = harris_corner_detector(filename)
    corners_harris_refined = refined_harris_corner_detector(filename)
    corners_shi = shi_tomasi_corner_detector(filename)
    _, _, corners_orb = orb(filename)
    _, _, corners_sift = sift(filename)
    corners_fast = fast(filename)
    corners_surf = surf(filename)

    corners = (corners_harris,
               corners_harris_refined,
               corners_shi,
               corners_orb,
               corners_sift,
               corners_surf,
               corners_fast)

    labels = ('Harris Corners',
              'Harris Refined',
              'Shi-Tomasi',
              'Orb',
              'SIFT',
              'SURF',
              'FAST')

    img = mpimage.imread(filename)
    
    cmap = plt.get_cmap('gnuplot')
    colors = [cmap(i) for i in np.linspace(0, 1, len(corners))]

    fig, ax = plt.subplots()
    ax.imshow(img)
    
    for corner, label in zip(corners, labels):
        ax.plot(corner[:,0], corner[:, 1], '.', label=label)

    plt.legend(loc='best')
    plt.show()

def orb_brute_force_matching(filename1=image_files[index],filename2=image_files[index+1], plot=False):
    """Use Brute Force matching between Orb features in two images
    """

    img1 = cv2.imread(filename1) # query image
    img2 = cv2.imread(filename2) # train image

    # orb detector, keypoint and descriptors
    kp1, des1, _ = orb(filename1)
    kp2, des2, _ = orb(filename2)

    # get keypoints and descriptors for both images with ORB
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # find matches
    matches = bf.match(des1, des2)
    matches = sorted(matches, key = lambda x:x.distance)  # best matches are earlier
   
    if plot:
        img3 = cv2.drawMatches(img1, kp1, img2, kp2, matches[:10], None, flags=2)
        plt.imshow(img3)
        plt.show()

    return matches

def sift_ratio_test_matching(filename1=image_files[index],filename2=image_files[index+1], plot=False):
    img1 = cv2.imread(filename1)
    img2 = cv2.imread(filename2)

    kp1, des1, _ = sift(filename1)
    kp2, des2, _ = sift(filename2)

    # Brute force matching
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    # apply ratio test
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append([m])

    # cv2.drawMatches expects lists of lists as matches
    if plot:
        img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good, None, flags=2)
        plt.imshow(img3)
        plt.show()

    return good 

def sift_flann_matching(filename1=image_files[index], filename2=image_files[index+1], plot=False): 
    img1 = cv2.imread(filename1)
    img2 = cv2.imread(filename2)

    kp1, des1, _ = sift(filename1)
    kp2, des2, _ = sift(filename2)

    # FLANN parameters
    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=50)  # or empty dictionary

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    matches = flann.knnMatch(des1, des2, k=2)

    # draw only good matches by creating a mask
    matchesMask = [[0, 0] for i in range(len(matches))]

    # ratio test 
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.7 * n.distance:
            matchesMask[i] = [1, 0]

    if plot:
        draw_params = dict(matchColor = (0, 255, 0),
                        singlePointColor = (255, 0, 0),
                        matchesMask = matchesMask,
                        flags = 0)

        img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, matches, None, **draw_params)

        plt.imshow(img3)
        plt.show()

    return matches
    
def orb_flann_matching(filename1=image_files[index], filename2=image_files[index+1], plot=False): 
    img1 = cv2.imread(filename1)
    img2 = cv2.imread(filename2)

    kp1, des1, _ = orb(filename1)
    kp2, des2, _ = orb(filename2)

    # FLANN parameters
    FLANN_INDEX_LSH = 6
    index_params = dict(algorithm = FLANN_INDEX_LSH,
                        table_number = 6,  # 12
                        key_size = 12,  # 20
                        multi_probe_level = 1)  # 2
    search_params = dict(checks=50)  # or empty dictionary

    flann = cv2.FlannBasedMatcher(index_params, search_params)
    
    matches = flann.knnMatch(des1, des2, k=2)

    # draw only good matches by creating a mask
    matchesMask = [[0, 0] for i in range(len(matches))]

    # ratio test 
    for i, (m, n) in enumerate(matches):
        if m.distance < 0.7 * n.distance:
            matchesMask[i] = [1, 0]

    if plot:
        draw_params = dict(matchColor = (0, 255, 0),
                        singlePointColor = (255, 0, 0),
                        matchesMask = matchesMask,
                        flags = 0)

        img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, matches, None, **draw_params)

        plt.imshow(img3)
        plt.show()

    return matches

def sift_feature_homography(filename1=image_files[index], filename2=image_files[index+1]):
    MIN_MATCH_COUNT = 10

    img1 = cv2.imread(filename1)
    img2 = cv2.imread(filename2)

    # sift keypoints
    kp1, des1, _ = sift(filename1)
    kp2, des2, _ = sift(filename2)

    FLANN_INDEX_KDTREE = 0
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, tree = 5)
    search_params = dict(checks = 50)

    flann = cv2.FlannBasedMatcher(index_params, search_params)

    matches = flann.knnMatch(des1, des2, k=2)

    # store the good matches using a ratio test
    good = []
    for m,n in matches:
        if m.distance < 0.7 * n.distance:
            good.append(m)

    if len(good) > MIN_MATCH_COUNT:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1, 1, 2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matchesMask = mask.ravel().tolist()

        h, w, d = img1.shape
        pts = np.float32([ [0,0], [0, h-1], [w-1, h-1], [w-1, 0] ]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        img2 = cv2.polylines(img2, [np.int32(dst)], True, 2255, 3, cv2.LINE_AA)

    else:
        print("Not enough matches are found - {0}/{1}".format(len(good), MIN_MATCH_COUNT))
        matchesMask = None

    draw_params = dict(matchColor = (0, 255, 0), # draw matches in green
                       singlePointColor = None, 
                       matchesMask = matchesMask, # draw only the inliers
                       flags = 2)

    img3 = cv2.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)
    plt.imshow(img3, 'gray')
    plt.show()

    print(M) 
