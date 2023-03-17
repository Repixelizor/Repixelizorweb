import requests
import json
import cv2
import numpy as np
# import pytorch library
import torch
# check for GPU
from urllib.parse import urlencode
if not torch.cuda.is_available():
    print('GPU not available.')
# necessary imports
import fastai
from deoldify.visualize import *
import warnings
warnings.filterwarnings("ignore", 
                        category=UserWarning, message=".*?Your .*? set is empty.*?")

import numpy as np
import urllib.request
# METHOD #1: OpenCV, NumPy, and urllib

def url_to_image(url):
	# download the image, convert it to a NumPy array, and then read
	# it into OpenCV format
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
	# return the image
    return image

def AI_enhance(fileurl):
	url = "https://ai-face-enhance.p.rapidapi.com/run"

	payload = {"image": fileurl}
	headers = {
		"content-type": "application/json",
		"X-RapidAPI-Key": "fabda2f015mshd538e9d8cdcd1c6p156c4bjsn797dd9675576",
		"X-RapidAPI-Host": "ai-face-enhance.p.rapidapi.com"
	}

	response = requests.request("POST", url, json=payload, headers=headers)
	response=json.loads(response.text)
	print(response["output_url"])
	return response["output_url"]



# load image
# 
# img="https://storage.googleapis.com/repixelizor-380005.appspot.com/105067464298105617131/upload/2023-03/IMG_1307.JPG"
# bsharpurl="105067464298105617131/upload/2023-03//bshap.jpg"
# sharpurl="105067464298105617131/upload/2023-03//shap.jpg"
def sharp_scratch(img1,bsharpurl,sharpurl):
    img = cv2.imread(img1)
    # kernel = np.array([[0, -1, 0],
    #                 [-1, 5,-1],
    #                 [0, -1, 0]])
    # image_sharp = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)
    ycrcb_img = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)

    # equalize the histogram of the Y channel
    ycrcb_img[:, :, 0] = cv2.equalizeHist(ycrcb_img[:, :, 0])

    # convert back to RGB color-space from YCrCb
    equalized_img = cv2.cvtColor(ycrcb_img, cv2.COLOR_YCrCb2BGR)
    # convert to grayscale
    gray = cv2.cvtColor(equalized_img, cv2.COLOR_BGR2GRAY)

    # adaptive threshold 
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, -35)

    # apply morphology
    kernel = np.ones((3,30),np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    kernel = np.ones((3,35),np.uint8)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)

    # get hough line segments
    threshold = 25
    minLineLength = 10
    maxLineGap = 20
    lines = cv2.HoughLinesP(morph, 1, 30*np.pi/360, threshold, minLineLength, maxLineGap)

    # draw lines
    linear1 = np.zeros_like(thresh)
    linear2 = img.copy()
    for [line] in lines:
        x1 = line[0]
        y1 = line[1]
        x2 = line[2]
        y2 = line[3]
        cv2.line(linear1, (x1,y1), (x2,y2), 255, 1)
        cv2.line(linear2, (x1,y1), (x2,y2), (0,0,255), 1)

    print('number of lines:',len(lines))

    # save resulting masked image
    cv2.imwrite('scratches_thresh.jpg', thresh)
    # cv2.imwrite('scratches_morph.jpg', morph)
    # cv2.imwrite('scratches_lines1.jpg', linear1)
    # cv2.imwrite('scratches_lines2.jpg', linear2)

    # display result
    # cv2.imshow("thresh", thresh)
    # cv2.imshow("morph", morph)
    # cv2.imshow("lines1", linear1)
    # cv2.imshow("lines2", linear2)
    mask1 = cv2.imread('scratches_thresh.jpg', cv2.IMREAD_GRAYSCALE)
    # mask2 = cv2.imread('scratches_morph.jpg', cv2.IMREAD_GRAYSCALE)
    # mask3 = cv2.imread('scratches_lines1.jpg', cv2.IMREAD_GRAYSCALE)
    # mask4 = cv2.imread('scratches_lines2.jpg', cv2.IMREAD_GRAYSCALE)
    dst = cv2.inpaint(img,mask1,3,cv2.INPAINT_NS)
    # dst = cv2.inpaint(dst,mask2,3,cv2.INPAINT_NS)
    # dst = cv2.inpaint(dst,mask3,3,cv2.INPAINT_TELEA)
    # dst = cv2.inpaint(dst,mask4,3,cv2.INPAINT_TELEA)
    # convert from RGB color-space to YCrCb


    # cv2.imshow('equalized_img', equalized_img)
    # cv2.imshow('dst',dst)
    kernel = np.array([[0, -1, 0],
                    [-1, 5,-1],
                    [0, -1, 0]])
    image_sharp = cv2.filter2D(src=dst, ddepth=-1, kernel=kernel)
    cv2.imwrite(bsharpurl, dst)
    cv2.imwrite(sharpurl, image_sharp)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return "Done"


def deoldify(sourceurl):  
	# use the get image colorizer function with artistic model
	colorizer = get_image_colorizer(artistic=True) #@param {type:"string"}
	
	# Here, we provide the parameters such as source URL, render factor etc.
	source_url = sourceurl

	render_factor = 39  #@param {type: "slider", min: 7, max: 40}
	watermarked = False #@param {type:"boolean"}
	
	if source_url is not None and source_url !='':
		image_path = colorizer.plot_transformed_image_from_url(url=source_url, 
			render_factor=render_factor, compare=True, watermarked=watermarked)
		return image_path
		# show_image_in_notebook(image_path)
	else:
		return 'Provide the valid image URL.'



def cartoonize(imgpath, k,toonurl,type):
    if type==1:
        path=deoldify(imgpath)
        print(path)
    else:
        path=imgpath
        # imgpath=url_to_image(path)
    img=cv2.imread(str(path))    
    
    # Defining input data for clustering
    data = np.float32(img).reshape((-1, 3))
    
    # Defining criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    # Applying cv2.kmeans function
    _, label, center = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    # print(center)
# Reshape the output data to the size of input image
    result = center[label.flatten()]
    result = result.reshape(img.shape)
    # Convert the input image to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Perform adaptive threshold
    edges  = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 9, 8)
    cv2.imshow('edges', edges)
    # Smooth the result
    blurred = cv2.medianBlur(result, 3)
    # Combine the result and edges to get final cartoon effect
    cartoon = cv2.bitwise_and(blurred, blurred, mask=edges)
    cv2.imwrite(toonurl,cartoon)
    return toonurl

