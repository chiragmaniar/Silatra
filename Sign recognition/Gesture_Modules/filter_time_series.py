'''
* This is the middle stage of the gesture recognition mechanism. 
* The entry function for this module is filterTS(ts) where ts is the timeseries obtained from gesture tracking module

* The timeseries generated by the tracker usually has some noise. 
* So as to minimize the loss of accuracy of recognizing the gesture, this noise is eliminated by this module
* This module also compresses this time series thus preventing the display of successive redundant states

* Version: 1.0
* Date: 20-2-2017
* Author: Kartik Shenoy
* Nickname: SK
'''

import nose
from nose import tools

maxNoiseThreshold = 3 # Must be odd!!
# maxNoOfSigns = 9

# Takes as input timeseries in the format:
# [("Thumbs_Up")]
def filterTS(ts):
    '''
    Returns the filtered and compressed time series from the long time series obtained at the input.

    Parameters
    ----------
    ts : list of tuples
        This represents the list of tuples as obtained as an output from the gestures tracker.
        The tuple will be (sign,direction)
        If this tuple represents a sign, sign field of this tuple will be None
        If this tuple represents a motion, direction field of this tuple will be None

    Returns
    -------
    list of tuples
        This represents the filtered and compressed time series

    '''
    signCount = 0
    motionCount = 0
    prevSegmentStart = 0
    prevSegmentEnd = 0

    segmentChangeFound = False

    sign_motion_category = "Unknown"

    filteredTS = []

    for i in range(len(ts)):
        if ts[i][0] == "None":
            motionCount = min(maxNoiseThreshold, motionCount + 1)
            if (signCount + motionCount) >= 3:
                signCount = max(0, signCount - 1)
        else:
            signCount = min(maxNoiseThreshold, signCount + 1)
            if (signCount + motionCount) >= 3:
                motionCount = max(0, motionCount - 1)
        
        # print((signCount,motionCount))

        if i == maxNoiseThreshold and (signCount == 3 or motionCount == 3):
            if signCount == 3:
                sign_motion_category = "sign"
            else:
                sign_motion_category = "motion"
        
        if (i > maxNoiseThreshold and ( (signCount == 3 and sign_motion_category == "motion") or (motionCount == 3 and sign_motion_category == "sign") )):
            segmentChangeFound = True
            prevSegmentEnd = i - 3           
        
        if segmentChangeFound:
            segmentChangeFound = False
            temp = findMode(ts[prevSegmentStart:prevSegmentEnd+1], sign_motion_category)
            if temp != None:
                filteredTS += [temp]
            prevSegmentEnd = prevSegmentStart = (prevSegmentEnd + 1)
            sign_motion_category = "sign" if signCount == 3 else "motion"
    temp = findMode(ts[prevSegmentStart:len(ts)], sign_motion_category)
    if temp != None:
        filteredTS += [temp]

    # print("\n\n--------------------The filtered Time Series is-----------------\n",filteredTS)

    return filteredTS



def findMode(segment,category):
    '''
    Returns the modal tuple that occurs at least half of the times in the current category i.e. "sign" or "motion"

    Segment is that part of the original time series that belongs to the same category
    If category is "sign", then out of this segment, the tuples that represent sign will be taken
    and the modal tuple amongst these will be returned (This tuple should occur at least half of the times).

    Parameters
    ----------
    segment : list of tuples
        This will be the segment from the original time series that has been recognized as belonging to the same category
    category : str
        This is a string that indicates the segment is recognized as "sign" or "motion"

    Returns
    -------
    tuple
        This tuple will be the modal tuple in the recognized segment

    '''
    # print("Segment under consideration:",segment,"\nCategory:",category)

    dict1 = {}
    noOfElems = 0

    for elem in segment:
        if (category == "sign" and elem[0] == "None") or (category == "motion" and elem[1] == "None"):
            continue

        if elem in dict1.keys():
            dict1[elem] += 1
        else:
            dict1[elem] = 1
        noOfElems += 1
    
    # print("Filtered Segment",dict1)

    minModality = int(noOfElems/2)

    modalElem = None

    for elem in dict1:
        if dict1[elem] > minModality:
            modalElem = elem
            minModality = dict1[elem]
    # print("Modal Tuple:",modalElem)

    return modalElem
        








# Cup_Closed, Cup_Open, Sorry_Fist, Sun_Up, ThumbsUp
# Apple_Finger, That_Is_Good_Circle, That_Is_Good_Point
# None

# Left, Right, Up, Down

def test_stable_series_of_Good_Afternoon():
    IP_Ts = [("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),
            ("None","Up"),("None","Up"),("None","Up"),("None","Up"),
            ("Cup_Open","None"),("Cup_Open","None"),("Cup_Open","None"),
            ("Cup_Open","None"),("Cup_Open","None"),("Cup_Open","None"),
            ("Cup_Open","None")]

    Expected_TS = [("ThumbsUp","None"), ("None","Up") ,("Cup_Open","None")]

    tools.eq_(filterTS(IP_Ts),Expected_TS)

def test_noisy1_series_of_Good_Afternoon():
    IP_Ts = [("ThumbsUp","None"),("Apple_Finger","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),
            ("None","Up"),("None","Up"),("None","Up"),("None","Up"),
            ("Cup_Open","None"),("Cup_Closed","None"),("Cup_Open","None"),
            ("Cup_Open","None"),("Cup_Open","None"),("Cup_Open","None"),
            ("Cup_Closed","None")]

    Expected_TS = [("ThumbsUp","None"), ("None","Up") ,("Cup_Open","None")]

    tools.eq_(filterTS(IP_Ts),Expected_TS)

def test_noisy2_series_of_Good_Afternoon():
    IP_Ts = [("ThumbsUp","None"),("None","Up"),("Apple_Finger","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),
            ("None","Up"),("None","Up"),("None","Up"),("None","Up"),
            ("Cup_Open","None"),("Cup_Closed","None"),("Cup_Open","None"),
            ("Cup_Open","None"),("Cup_Open","None"),("Cup_Open","None"),
            ("Cup_Closed","None")]

    Expected_TS = [("ThumbsUp","None"), ("None","Up") ,("Cup_Open","None")]

    tools.eq_(filterTS(IP_Ts),Expected_TS)

def test_noisy3_series_of_Good_Afternoon():
    IP_Ts = [("ThumbsUp","None"),("None","Up"),("Apple_Finger","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),
            ("None","Up"),("ThumbsUp","None"),("None","Left"),("None","Up"),("None","Up"),
            ("Cup_Open","None"),("Cup_Closed","None"),("Cup_Open","None"),
            ("Cup_Open","None"),("Cup_Open","None"),("Cup_Open","None"),
            ("Cup_Closed","None")]

    Expected_TS = [("ThumbsUp","None"), ("None","Up") ,("Cup_Open","None")]

    tools.eq_(filterTS(IP_Ts),Expected_TS)

def test_noisy4_series_of_Good_Afternoon():
    IP_Ts = [("ThumbsUp","None"),("None","Up"),("Apple_Finger","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),
            ("None","Up"),("ThumbsUp","None"),
            ("None","Up"),("None","Up"),("None","Up"),
            ("Cup_Open","None"),("Cup_Closed","None"),("Cup_Open","None"),
            ("Cup_Open","None"),("Cup_Open","None"),("Cup_Open","None"),
            ("Cup_Closed","None")]

    Expected_TS = [("ThumbsUp","None"), ("None","Up") ,("Cup_Open","None")]

    tools.eq_(filterTS(IP_Ts),Expected_TS)

def test_stable_series_of_Good_Morning():
    IP_Ts = [("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),
            ("None","Down"),("None","Down"),("None","Down"),("None","Down"),
            ("Cup_Closed","None"),("Cup_Closed","None"),("Cup_Closed","None"),
            ("Cup_Closed","None"),("Cup_Closed","None"),("Cup_Closed","None"),
            ("Cup_Closed","None"),
            ("None","Up"),("None","Up"),("None","Up"),("None","Up"),("None","Up"),("None","Up"),
            ("Cup_Open","None"),("Cup_Closed","None"),("Cup_Open","None"),
            ("Cup_Open","None"),("Cup_Open","None"),("Cup_Open","None"),
            ("Cup_Open","None")]

    Expected_TS = [("ThumbsUp","None"), ("None","Down"), ("Cup_Closed","None"), ("None","Up"), ("Cup_Open","None")]

    tools.eq_(filterTS(IP_Ts),Expected_TS)

def test_noisy1_series_of_Good_Morning():
    IP_Ts = [("ThumbsUp","None"),("None","Up"),("Apple_Finger","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),
            ("None","Down"),("ThumbsUp","None"),
            ("None","Down"),("None","Down"),("None","Down"),("None","Down"),
            ("Cup_Closed","None"),("ThumbsUp","None"),("Cup_Closed","None"),
            ("Cup_Closed","None"),("ThumbsUp","None"),("Cup_Closed","None"),
            ("Cup_Closed","None"),
            ("None","Up"),("ThumbsUp","None"),
            ("None","Up"),("None","Up"),("None","Up"),("None","Up"),("None","Up"),
            ("Cup_Open","None"),("Cup_Closed","None"),("Cup_Open","None"),
            ("Cup_Open","None"),("Cup_Open","None"),("Cup_Open","None"),
            ("Cup_Closed","None")]

    Expected_TS = [("ThumbsUp","None"), ("None","Down"), ("Cup_Closed","None"), ("None","Up"), ("Cup_Open","None")]

    tools.eq_(filterTS(IP_Ts),Expected_TS)

def test_stable_series_of_Good_Night():
    IP_Ts = [("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),
            ("None","Up"),("None","Up"),("None","Up"),("None","Up"),("None","Up"),("None","Up"),
            ("Cup_Open","None"),("Cup_Closed","None"),("Cup_Open","None"),
            ("Cup_Open","None"),("Cup_Open","None"),("Cup_Open","None"),
            ("Cup_Open","None"),
            ("None","Down"),("None","Down"),("None","Down"),("None","Down"),
            ("Cup_Closed","None"),("Cup_Closed","None"),("Cup_Closed","None"),
            ("Cup_Closed","None"),("Cup_Closed","None"),("Cup_Closed","None"),
            ("Cup_Closed","None")]

    Expected_TS = [("ThumbsUp","None"), ("None","Up"), ("Cup_Open","None"), ("None","Down"), ("Cup_Closed","None")]

    tools.eq_(filterTS(IP_Ts),Expected_TS)

def test_noisy1_series_of_Good_Night():
    IP_Ts = [("ThumbsUp","None"),("None","Up"),("Apple_Finger","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),("ThumbsUp","None"),
            ("ThumbsUp","None"),("ThumbsUp","None"),
            ("None","Up"),("ThumbsUp","None"),
            ("None","Up"),("None","Up"),("None","Up"),("None","Up"),("None","Up"),
            ("Cup_Open","None"),("Cup_Closed","None"),("Cup_Open","None"),
            ("Cup_Open","None"),("Cup_Open","None"),("Cup_Open","None"),
            ("Cup_Closed","None"),
            ("None","Down"),("ThumbsUp","None"),
            ("None","Down"),("None","Down"),("None","Down"),("None","Down"),
            ("Cup_Closed","None"),("ThumbsUp","None"),("Cup_Closed","None"),
            ("Cup_Closed","None"),("ThumbsUp","None"),("Cup_Closed","None"),
            ("Cup_Closed","None")]

    Expected_TS = [("ThumbsUp","None"), ("None","Up"), ("Cup_Open","None"), ("None","Down"), ("Cup_Closed","None")]

    tools.eq_(filterTS(IP_Ts),Expected_TS)

# def test_complex_input():
# IP_Ts = [('None', 'Up'), ('None', 'Up'), 
#         ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('None', 'Up'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('None', 'Down'), ('None', 'Down'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('None', 'Down'), ('None', 'Down'), ('None', 'Down'), ('None', 'Down'), ('None', 'Down'), 
#         ('None', 'Down'), ('ThumbsUp', 'None'), ('That_is_Good_Point', 'None'), 
#         ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('ThumbsUp', 'None'), 
#         ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('That_is_Good_Point', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('That_is_Good_Point', 'None'), ('ThumbsUp', 'None'), ('ThumbsUp', 'None'), 
#         ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), 
#         ('None', 'Up'), ('None', 'Up'), ('None', 'Up'), ('None', 'Up'), ('None', 'Up'), 
#         ('None', 'Up'), ('None', 'Up'), ('None', 'Up'), ('None', 'Up'), ('None', 'Up'), 
#         ('None', 'Up'), ('None', 'Up'), ('None', 'Up'), ('None', 'Up'), ('None', 'Up'), 
#         ('None', 'Up'), ('None', 'Up'), 
#         ('Cup_Open', 'None'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), 
#         ('None', 'Up'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), 
#         ('Cup_Open', 'None'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), 
#         ('Cup_Open', 'None'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), 
#         ('Cup_Open', 'None'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), 
#         ('Cup_Open', 'None'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), ('Cup_Open', 'None'), 
#         ('Cup_Open', 'None'), 
#         ('None', 'Down'), ('None', 'Down'), ('None', 'Left'), ('None', 'Left'), 
#         ('None', 'Right'), ('None', 'Up'), ('None', 'Down'), ('None', 'Up'), ('None', 'Left')]
        
# Expected_TS = [("ThumbsUp","None"), ("None","Up"), ("Cup_Open","None"), ("None","Down"), ("Cup_Closed","None")]

# print(filterTS(IP_Ts))
# tools.eq_(filterTS(IP_Ts),Expected_TS)

# IP_Ts = [('None', 'Left'), ('Sorry_Fist', 'None'), ('Sorry_Fist', 'None'), ('Sorry_Fist', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('Sorry_Fist', 'None'), ('Sorry_Fist', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('Sorry_Fist', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('None', 'Up'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None'), ('That_is_Good_Point', 'None')]

# # Expected_TS = [("ThumbsUp","None"), ("None","Up") ,("Cup_Open","None")]

# print(filterTS(IP_Ts))