import numpy as np 
import cv2 
import pygame

cap = cv2.VideoCapture(0)


# GLOBAL INITIALIZATIONS
# --------------------------------------------------------------------
#range for blue
lower_blue = np.array([110, 50, 50])
upper_blue = np.array([130, 255, 255])

# range for yellow
lower_yellow = np.array([20, 100, 100])
upper_yellow = np.array([75, 255, 255])

# kernel for erosion
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))

# Variable to store the index of the largest contours
largest_contour_blue_pos = 0
largest_contour_yellow_pos = 0

# Variable to store maximum contour areas
largest_contour_blue_area = 0
largest_contour_yellow_area = 0

# Coordinates of the bounding rectange
xb = yb = wb = hb = -1
xy = yy = wy = hy = -1

# Coordinates of the centroid of blue and yellow
cent_bluex = cent_bluey = -1
cent_yellowx = cent_yellowy = -1

# largest contour of blue and yellow
cb = cy =[]

isOneMarker = False
colorChange = False

# Define some colors
BLACK = (   0,   0,   0)
WHITE = ( 255, 255, 255)
GREEN = (   0, 255,   0)
RED   = ( 255,   0,   0)
CIRCLE_COLORS   = [(231,75,100), (92,195,55), (32,69,191), (10,141,255), (255,215,10)]
BG = (240, 210, 175)

# current color
curr_color = 0



def draw_circle(screen, x, y):
    pygame.draw.circle(screen, CIRCLE_COLORS[curr_color], [int(x), int(y)], 10)



def distance_pts(x1,y1,x2,y2):
	return (((x2-x1)**2)+((y2-y1)**2))**0.5


# Setup
pygame.init()
   
# Set the width and height of the screen [width,height]
size = [800, 500]
screen = pygame.display.set_mode(size)
  
pygame.display.set_caption("Draw")

screen.fill(BG)




# OPENCV LOOP STARTS HERE
# ------------------------------------------------------------------------


while 1:

	_, frame = cap.read()

	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)



	mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)


	# Opening to remove noise. And then dilating
	bluethresh_open = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel)
	bluethresh_dilate = cv2.dilate(bluethresh_open, kernel, iterations = 1)

	yellowthresh_open = cv2.morphologyEx(mask_yellow, cv2.MORPH_OPEN, kernel)
	yellowthresh_dilate = cv2.dilate(yellowthresh_open, kernel, iterations = 1)

	# we make a copy of these for contours
	bluethresh_cont = bluethresh_dilate.copy()
	yellowthresh_cont = yellowthresh_dilate.copy()

	# Now we find the contours
	_, contours_blue, _ = cv2.findContours(bluethresh_cont, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	_, contours_yellow, _ = cv2.findContours(yellowthresh_cont, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

	# We find the largest contour by comparing areas
	largest_contour_blue_area = 0
	largest_contour_yellow_area = 0

	for i in xrange(len(contours_blue)):
		if cv2.contourArea(contours_blue[i])>largest_contour_blue_area:
			largest_contour_blue_area = cv2.contourArea(contours_blue[i])
			largest_contour_blue_pos = i 

	for i in xrange(len(contours_yellow)):
		if cv2.contourArea(contours_yellow[i])>largest_contour_yellow_area:
			largest_contour_yellow_area = cv2.contourArea(contours_yellow[i])
			largest_contour_yellow_pos = i



	# Condition to change the color
	




	# If there is atleast one contour and area > xxx to remove unwanted detection
	if len(contours_blue)!=0 and largest_contour_blue_area>500 :
		xb,yb,wb,hb = cv2.boundingRect(contours_blue[largest_contour_blue_pos])
		cb = contours_blue[largest_contour_blue_pos]

		# Finding moment to find centroid
		Mb = cv2.moments(cb)
		cent_bluex = int(Mb['m10']/Mb['m00'])
		cent_bluey = int(Mb['m01']/Mb['m00'])
		# cv2.circle(frame, (cent_bluex, cent_bluey), 5, (0,255,0),-1)

		isOneMarker = True
	else:
		isOneMarker = False
		xb=yb=wb=hb=-1
		cent_bluex = cent_bluey = -1
		cb = []
	

	# same for yellow
	if len(contours_yellow)!=0 and largest_contour_yellow_area>500:
		xy,yy,wy,hy = cv2.boundingRect(contours_yellow[largest_contour_yellow_pos])
		cy = contours_yellow[largest_contour_yellow_pos]

		# Moment to find centroid
		My = cv2.moments(cy)
		cent_yellowx = int(My['m10']/My['m00'])
		cent_yellowy = int(My['m01']/My['m00'])
		# cv2.circle(frame, (cent_yellowx, cent_yellowy), 5, (255,0,0), -1)

	else:
		xy=yy=wy=hy=-1
		cent_yellowx = cent_yellowy = -1
		cy = []


	# condition to change color
	# distance between the centroids
	if xy!=-1 and yy!=-1:
		dbc = distance_pts(cent_bluex, cent_bluey, cent_yellowx, cent_yellowy)
		print dbc

		if int(dbc)<=60:

			if not colorChange:
				curr_color = (curr_color+1)%5
				colorChange = True
		else:
			colorChange = False




		




	if isOneMarker:

		# We multiply by 1.5 so that it can cover the whole pygame window size
		# as the webcame res is 640*480 while the pygame res is 1000*700

		# Also the direction of motion of the webcam is inverted, so we apply
		# The necessary condition

		draw_circle(screen, 800-xb*1.5,yb*1.5-100)



	pygame.display.flip()
	# cv2.imshow("frame", frame)

	if cv2.waitKey(1) & 0xff == 27:
		pygame.quit()
		break

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			break


cap.release()



