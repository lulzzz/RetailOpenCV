import cv2
import numpy as np

ql = 16
channels=[0,1,2]
#ranges=[0,256]
ranges=[0,256, 0,256, 0,256]
histSize = [ql for i in range(0,3)];


disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))

crossing_img = cv2.imread("crossing_img.png")
crossing_mask = cv2.cvtColor(cv2.imread("crossing_mask.png"), cv2.COLOR_BGR2GRAY)

alone_img =  cv2.imread("alone_img.png")
alone_mask_mk =  cv2.cvtColor(cv2.imread("mk_mask.png"), cv2.COLOR_BGR2GRAY)
alone_mask_os =  cv2.cvtColor(cv2.imread("os_mask.png"), cv2.COLOR_BGR2GRAY)
alone_mask =  cv2.cvtColor(cv2.imread("alone_mask.png"), cv2.COLOR_BGR2GRAY)

alone0_img =  cv2.imread("alone0_img.png")
alone0_mask_mk =  cv2.cvtColor(cv2.imread("alone0_mk_mask.png"), cv2.COLOR_BGR2GRAY)
alone0_mask_os =  cv2.cvtColor(cv2.imread("alone0_os_mask.png"), cv2.COLOR_BGR2GRAY)
alone0_mask =  cv2.cvtColor(cv2.imread("alone0_mask.png"), cv2.COLOR_BGR2GRAY)

alone1_img =  cv2.imread("alone1_img.png")
alone1_mask_mk =  cv2.cvtColor(cv2.imread("alone1_mk_mask.png"), cv2.COLOR_BGR2GRAY)
alone1_mask_os =  cv2.cvtColor(cv2.imread("alone1_os_mask.png"), cv2.COLOR_BGR2GRAY)
alone1_mask =  cv2.cvtColor(cv2.imread("alone1_mask.png"), cv2.COLOR_BGR2GRAY)

cv2.imshow('crossing_img', crossing_img)
cv2.imshow('crossing_mask',crossing_mask)

cv2.imshow('alone_img', alone_img)
cv2.imshow('alone_mask_mk',alone_mask_mk)
cv2.imshow('alone_mask_os',alone_mask_os)

alone_split = cv2.split(alone_img)

# calculating roi object histogram
os_hist = cv2.calcHist(alone_split, channels, alone_mask_os, histSize, ranges)
mk_hist = cv2.calcHist(alone_split, channels, alone_mask_mk, histSize, ranges)

#cv2.imshow('alone_mask_mk', cv2.bitwise_and(alone_img, alone_img ,mask = alone_img))

# normalize histogram and apply backprojection
#cv2.normalize(os_hist,os_hist,0,255,cv2.NORM_MINMAX)
#cv2.normalize(mk_hist,mk_hist,0,255,cv2.NORM_MINMAX)
#dst = cv2.calcBackProject(bgr_split, channels, roihist, ranges, scale =1)

#Count pixel in each person
Am = cv2.countNonZero(alone_mask_mk)
Ao = cv2.countNonZero(alone_mask_os)

#Prior probability that a pixel belongs to person i
Pm = float(Am)/(Am+Ao)
Po = float(Ao)/(Am+Ao)

#Get probability of color x knowing person  
Pxm= mk_hist/ Am
Pxo= os_hist/ Ao

#Posterior probability
# (probability taht the pixel of the group mask belong to person i knowing its color)
Pmx = Pxm*Pm/(Pxm*Pm + Pxo*Po)
Pox = Pxo*Po/(Pxm*Pm + Pxo*Po)

Pmx=np.uint8(Pmx*255)
Pox=np.uint8(Pox*255)

#target = crossing_img
#mask_target = crossing_mask

target = alone0_img
mask_target = alone0_mask

#Posterior backprojection

b,g,r=cv2.split(target/(256/ql))
B = np.uint8(Pxm[b.ravel(),g.ravel(), r.ravel()])
dst = B.reshape(target.shape[:2])
#dst = dst * (mask_target/255)
dst = cv2.bitwise_and(dst, dst ,mask = mask_target)
cv2.imshow("Posteriors mk ", dst)

b,g,r=cv2.split(target/(256/ql))
B = np.uint8(Pox[b.ravel(),g.ravel(), r.ravel()])
dst = B.reshape(target.shape[:2])
#dst = dst * (mask_target/255)
#dst = cv2.bitwise_and(dst, dst ,mask = mask_target)
cv2.imshow("Posteriors os ", dst)

#Scores

#scene alone 0
alone0_split = cv2.split(alone0_img)
os_hist0 = cv2.calcHist(alone0_split, channels, alone0_mask_os, histSize, ranges)
mk_hist0 = cv2.calcHist(alone0_split, channels, alone0_mask_mk, histSize, ranges)

s1 = np.sum(np.minimum(mk_hist0, mk_hist))/np.sum(mk_hist)
s2 = np.sum(np.minimum(mk_hist0, os_hist))/np.sum(os_hist)
s3 = np.sum(np.minimum(os_hist0, mk_hist))/np.sum(mk_hist)
s4 = np.sum(np.minimum(os_hist0, os_hist))/np.sum(os_hist)

print 'the person 0mk is mk : score=', s1
print 'the person 0mk is os : score=', s2
print 'the person 0os is mk : score=', s3
print 'the person 0os is os : score=', s4
print ''

#scene alone 1
alone1_split = cv2.split(alone1_img)
os_hist1 = cv2.calcHist(alone1_split, channels, alone1_mask_os, histSize, ranges)
mk_hist1 = cv2.calcHist(alone1_split, channels, alone0_mask_mk, histSize, ranges)

s1 = np.sum(np.minimum(mk_hist1, mk_hist))/np.sum(mk_hist)
s2 = np.sum(np.minimum(mk_hist1, os_hist))/np.sum(os_hist)
s3 = np.sum(np.minimum(os_hist1, mk_hist))/np.sum(mk_hist)
s4 = np.sum(np.minimum(os_hist1, os_hist))/np.sum(os_hist)

print 'the person 1mk is mk : score=', s1
print 'the person 1mk is os : score=', s2
print 'the person 1os is mk : score=', s3
print 'the person 1os is os : score=', s4


## backproj
target=alone_img

b,g,r=cv2.split(target/(256/ql))
B = np.uint8(np.round(mk_hist[b.ravel(),g.ravel(), r.ravel()]))
dst = B.reshape(target.shape[:2])
#dst = dst * (mask_target/255)
cv2.imshow("backproj mk ", dst)

#dst = cv2.bitwise_and(dst, dst ,mask = mask_target)
#cv2.imshow("backproj mk masqued", dst)

##cv2.imwrite('C:\\Users\\AdminGFI\\Documents\\Sample\\bp_test\\backproj.png',dst)

## Now convolute with circular disc
    
#cv2.filter2D(dst,-1,disc,dst)

## threshold and binary AND
#ret,thresh = cv2.threshold(dst,50,255,0)
#thresh = cv2.merge((thresh,thresh,thresh))
#res = cv2.bitwise_and(target,thresh)
##res = np.vstack((target,thresh,res))
#cv2.imshow('res.jpg',res)
##cv2.imwrite('C:\\Users\\AdminGFI\\Documents\\Sample\\bp_test\\res.png',res)

cv2.waitKey(0)

pass
