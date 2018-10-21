import cv2
import numpy as np 
from detect_shapes import ShapeDetector
import time

class Launchpad():

	def __init__(self):
		self.cap = cv2.VideoCapture(0)
		self.shape_detector = ShapeDetector(50, 1200, 100, 700)
		self.past1_frame = np.zeros((720,1080))
		self.past2_frame = np.zeros((720,1080))
		self.count = 0


	def has_changed(self, i, j, past_frame, tolerance):
		for x in range (i - tolerance, i + tolerance):
			for y in range (j - tolerance, j + tolerance):
				if past_frame[x][j] > 0:
					return False
		return True

	def print_lowest_i(self, edges):
		max_i = 0
		for i in range(400,720):
			for j in range(200,1000):
				if not edges[i][j] == 0:
					if i > max_i:
						max_i = i 
		print(max_i)

	def print_lowest_j(self, edges):
		max_j = 0
		for i in range(400,720):
			for j in range(200,1000):
				if not edges[i][j] == 0:
					if j > max_j:
						max_j = j 
		print(max_j)


	def apply_kernel(self, kernel, image, start_point):
		x_start, y_start = start_point
		total = 0
		for x in range(len(kernel)):
			for y in range(len(kernel[0])):
				# print(kernel[x][y])
				# print(image[x_start + x][y_start + y])

				# if image[x_start + x][y_start + y] > 0:
				# 	print('YOOO')

				total += kernel[x][y]*image[x_start + x][y_start + y]

		return total

	# Checks all the past frames to see if the fingertip was there before
	# If it was there for all past frames, then we return True
	def check_past_frames(self, kernel_group, past_frames, start):
		# left, right, top, bot = dims
		kernel, threshold = kernel_group
		x, y = len(kernel), len(kernel[0])

		# print(dims)
		# print(x, y)
		# print(past_frames)
		for frame in past_frames:
			# for i in range(top, bot - x + 2):
			# 	for j in range(left, right - y + 2):		
			kernel_val = self.apply_kernel(kernel, frame, start)

			if kernel_val < threshold:
				return False
		return True


	# Box is given as a list of coordinates ((x1, y1), (x1, y2) ,(x2, y1) ,(x2, y2))
	# determines a touch by applying a certain kernel (probably a long rectangle) 
	def find_touch(self, kernel_group, frames, box):

		kernel, threshold = kernel_group
		frame, past_frames = frames[0], frames[1:]

		# x and y are num rows and num columns of the kernel
		x, y = len(kernel), len(kernel[0])
		top, left = box[0]
		bot, right = box[-1]
		dims = (left, right, top, bot)
		# formula is (right_bound - length of kernel + 1) things to iterate (add 2 because it's a range)

		for i in range(top, bot - x + 2):
			for j in range(left, right - y + 2):	
				kernel_val = self.apply_kernel(kernel, frame, (i,j))
				# if kernel_val > 6:
				# 	print((i,j))
				# Indicates that we have a touch!
				if kernel_val > threshold and self.check_past_frames(kernel_group, past_frames, (i,j)):
					return (i,j)
		return None


	def draw_hard_code(self, box, current_frame):
		
		for i, j in box:
			for x in range(-5, 6):
				for y in range(-5, 6):
					current_frame[i + x][j+ y] = 1

		
	def draw_shape_detector_box(self,current_frame):
		for i in (self.shape_detector.top, self.shape_detector.bottom):
			for j in range(self.shape_detector.left, self.shape_detector.right):
				for x in range(-5, 6):
					for y in range(-5, 6):
						current_frame[i + x][j+ y] = 1

		for j in (self.shape_detector.left, self.shape_detector.right):
			for i in range(self.shape_detector.top, self.shape_detector.bottom):
				for x in range(-5, 6):
					for y in range(-5, 6):
						current_frame[i + x][j+ y] = 1

	def calibration_mode(self):
		while True:
			ret, frame = self.cap.read()
			frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			edges = cv2.Canny(frame, 100, 200)

	def main(self):
		# past_frame = np.zeros((720,1080))
		t = time.time()
		ret, frame = self.cap.read()
		print("checkpoint 1", str(time.time() - t))

		t = time.time()
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		print("checkpoint 2", str(time.time() - t))

		edges = cv2.Canny(frame, 100, 200)				
	
		boxes = self.shape_detector.find_bounding_boxes(edges)

		current_frame = edges/255

		box = [(330, 570), (370, 570), (330, 620),(370, 620)]
		self.draw_hard_code(box, current_frame)
		
		self.draw_shape_detector_box(current_frame)

		print("========= BOXeS ==========")
		for poly in boxes:
			print(poly)
			print("\n")
			for i, j in poly.points:
				for x in range(-5, 6):
					for y in range(-5, 6):
						current_frame[i + x][j+ y] = 1
		print("========== END BOXES =======")

		kernel = [[1 for x in range(10)] for y in range(2)]
		threshold = 6
		kernel_group = (kernel, threshold)
		frames = (current_frame, self.past1_frame, self.past2_frame)

		# val = self.find_touch(kernel_group, frames, box)
		# if val:
		# 	self.count += 1
		# 	print("self.count: " + str(self.count))
		# 	print(val)

		# print_lowest_i(edges)
		# print_lowest_j(edges)
		
		cv2.imshow('current frame', current_frame)

		
		self.past2_frame, self.past1_frame = self.past1_frame, current_frame


#L = Launchpad()


# Initial change detection code (only detects diference between current frame and previous frame)
#
# possible_changes = []
# for i in range(hard_code[0][0], hard_code[-1][0]):
# 	for j in range(hard_code[0][1], hard_code[-1][1]):
# 		p = current_frame[i][j]
# 		if p > 0 and self.has_changed(i, j, past_frame, 5):
# 			possible_changes.append((i,j))

# if possible_changes:
# 	tip = max(possible_changes, key=lambda z: z[0])

# 	print("button press! At: " + str(tip))

# #  Kernel testing
# image = [[0, 0, 1, 1, 0], [0 , 0, 1, 1, 0], [0, 0, 0, 0, 0]]
# kernel = [[1,1],[1,1]]
# print(L.apply_kernel(kernel, image, (0, 1)))

# # Find touch test
# vert = [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0]
# image = [vert]*2 + [[0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0], [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0], [0]*12]
# kernel = [[1 for x in range(10)] for y in range(2)]
# threshold = 6
# kernel_group = (kernel, threshold)
# box = [(0, 0), (4, 0), (0, 11), (4, 11)]
# copy_frames = [list(x) for x in image]
# frames = (image, copy_frames, copy_frames)
# frames2 = (image, copy_frames, [[0]*12]*5)

# print(L.find_touch(kernel_group, frames, box), L.find_touch(kernel_group, frames2, box))


#L.main()