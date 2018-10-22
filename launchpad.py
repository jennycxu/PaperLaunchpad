import cv2
import numpy as np 
from scipy import ndimage

from collections import defaultdict
import time
from detect_shapes import ShapeDetector


class Launchpad():

	def __init__(self, audio):
		self.cap = cv2.VideoCapture(0)

		# self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
		# self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
		self.shape_detector = ShapeDetector(0, 1200, 0, 700)
		self.past1_frame = np.zeros((720,1080))
		self.past2_frame = np.zeros((720,1080))
		self.count = 0
		self.audio = audio

		# number of frames from the last press
		self.press_threshold = 20

		# Is given during calibration step, will tell you dimensions of the current launchpad
		self.dimensions = None
		self.sections = None
		self.section_mappings = {}
		self.box_to_section = {}

		self.boxes = []

		# Tells you if a box is currently pressed or off
		self.box_state = {}
		self.box_generators = defaultdict(str)
		self.is_calibrating = True

		self.button_gen_mappings = []

		self.shelter_mapping = ["shelter","drop","drop2","drop3","drop4","drop5","high A","high G"]
		# self.unforgettable_mapping = ["high A","high G", "Ab","Gb","Db","Eb","entire","drop"]
		self.unforgettable_mapping = ["high A","high G", "entire"]

		self.gucci_mapping = ['oo', 'yeuh', 'goochi', 'blurp', 'lulpump', 'gchgang']
		self.daft_mapping = ["workit","doit", "harder","stronger","again","getup","getdown","build"]
		self.overtime_mapping = ["getdown","getup", "getdownbuild","overtime","again","drop","drop2","drop3","drop4","drop5"]
		self.song_mappings = {"g": [(2, 3), [2], self.gucci_mapping], "s":[(2,4),[1,2],self.shelter_mapping],"u":[(1,3),[1],self.unforgettable_mapping],"d":[(4,2),[0],self.daft_mapping],"o":[(2,5),[1,2],self.overtime_mapping]}

	
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

	# def check_past_frames_vectorized(self, kernel_group, past_frames, actual_box, dims):
	# 	# left, right, top, bot = dims
	# 	kernel, threshold = kernel_group
	# 	x, y = len(kernel), len(kernel[0])
	# 	left, right, top, bot = dims

	# 	# print(dims)
	# 	# print(x, y)
	# 	# print(past_frames)
	# 	for frame in past_frames:
	
	# 		values =  np.where((ndimage.convolve(actual_box, kernel, mode='constant'))< threshold)
	# 	return True


	# Box is given as a list of coordinates ((x1, y1), (x1, y2) ,(x2, y1) ,(x2, y2))
	# determines a touch by applying a certain kernel (probably a long rectangle) 
	def find_touch(self, kernel_group, frames, box):

		kernel, threshold = kernel_group
		frame, past_frames = frames[0], frames[1:]

		# x and y are num rows and num columns of the kernel
		x, y = len(kernel), len(kernel[0])
		top, left = box[0]
		bot, right = box[-1]

		# formula is (right_bound - length of kernel + 1) things to iterate (add 2 because it's a range)
		for i in range(top, bot - x + 2):
			for j in range(left, right - y + 2):	
				kernel_val = self.apply_kernel(kernel, frame, (i,j))

				# Indicates that we have a touch!
				if kernel_val > threshold and self.check_past_frames(kernel_group, past_frames, (i,j)):
					return (i,j)
		return None

	def find_touch_vectorized(self, kernel_group, frames, box):

		kernel, threshold = kernel_group
		frame, past_frames = frames[0], frames[1:]

		# x and y are num rows and num columns of the kernel
		x, y = len(kernel), len(kernel[0])
		top, left = box[0]
		bot, right = box[-1]
		dims = (left, right, top, bot)

		actual_box = frame[top:bot+1, left:right+1]
		convolution = ndimage.convolve(actual_box, kernel, mode='constant')

		values =  np.where(convolution > threshold)

		if values[0].size > 0:
			# print(box)
			# print(top + values[0][0], left + values[1][0])
			if self.check_past_frames(kernel_group, past_frames, (top + values[0][0], left + values[1][0])):
				return top + values[0][0], left + values[1][0]
			else:
				print("Ephemeral kind of finger")
		
		return None

	def draw_hard_code(self, box, current_frame, reverse=False):
		for i, j in box:
			for x in range(-5, 6):
				for y in range(-5, 6):
					if not reverse:
						current_frame[i + x][j+ y] = 1
					else:
						current_frame[i + x][j+ y] = 0
		
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
		self.is_calibrating = True

		ret, frame = self.cap.read()
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		edges = cv2.Canny(frame, 100, 200)

		boxes = self.shape_detector.find_bounding_boxes(edges)

		current_frame = edges/255

		past_current_frame = np.copy(current_frame)
		# print("========= BOXeS ==========")
		for poly in boxes:
			# print(poly)
			# print("\n")
			for i, j in poly.points:
				for x in range(-5, 6):
					for y in range(-5, 6):
						current_frame[i + x][j+ y] = 1
			for i, j in poly.get_valid_shape():
				for x in range(-5, 6):
					for y in range(-5, 6):
						current_frame[i + x][j+ y] = 1

		cv2.imshow('current frame', current_frame)
		current_frame = past_current_frame
		print("Is the configuration you want?")
		keypress = cv2.waitKey(1) & 0xFF
		while keypress not in [ord('y'), ord('n')]:
			keypress = cv2.waitKey(1) & 0xFF
		if keypress == ord('y'):

			# boxes = sorted()

			
			self.boxes = boxes 
			

			for box in self.boxes:
				self.box_state[box] = 0

			# for i in range(8):
			# 	self.box_generators[self.boxes[i]] = ['shelter', 'doit', 'workit', 'harder', 'stronger', 'drop', 'drop2', 'drop3'][i]
			# self.box_generators[self.boxes[0]] = 'doit'
			# self.box_generators[self.boxes[1]] = 'workit'

			self.is_calibrating = False

			self.audio.reset()

			# Find a song
			print("Choose a song: s - Shelter, u - Unforgettable, d - Daft Punk, o - Overtime, g - Gucci Gang m = Manual Input")
			keypress = cv2.waitKey(1) & 0xFF
			while keypress not in [ord('s'), ord('u'), ord('d'), ord('o'), ord('g'), ord('m')]:
				keypress = cv2.waitKey(1) & 0xFF

			if keypress in [ord('s'), ord('u'), ord('d'), ord('o'), ord('g')]:
				song = chr(keypress)

				self.sections = self.song_mappings[song][1]
				self.dimensions = self.song_mappings[song][0]
				self.button_gen_mappings = self.song_mappings[song][2]

				print(self.song_mappings[song])

				sort_y = lambda y: min([x[1] for x in y])
				self.boxes = sorted(self.boxes, key=lambda x: sort_y(x.get_valid_shape()))

				y_sections = []

				left_border = 0
				for right in self.sections:
					y_sections.append(self.boxes[left_border: (right + 1)*self.dimensions[0]])
					left_border = (right + 1)*self.dimensions[0]

				y_sections.append(self.boxes[left_border:])

				# print(y_sections)
				for i in range(len(y_sections)):
					self.section_mappings[i] = y_sections[i]
					for box in y_sections[i]:
						self.box_to_section[box] = i

				# print("section mappings: " + str(self.box_to_section))

				sort_x = lambda y: min([x[0] for x in y])

				new_y_sections = []
				for i in range(self.dimensions[1]):
					eles = self.boxes[ i*self.dimensions[0] : (i+1)*self.dimensions[0]]
					col = sorted(eles, key = lambda x: sort_x(x.get_valid_shape()) )
					new_y_sections.extend(col)

				self.boxes = new_y_sections

				# print([box.get_valid_shape() for box in self.boxes])

				for i in range(len(self.boxes)):
					box = self.boxes[i]
					self.box_generators[box] = self.button_gen_mappings[i]

			else:
				for i in range(len(self.boxes)):
					box = self.boxes[i].get_valid_shape()
					self.draw_hard_code(box, current_frame)
					if i > 0:
						self.draw_hard_code(self.boxes[i-1].get_valid_shape(), current_frame)

					cv2.imshow('current frame', current_frame)
					print("Which sound for note " + str(i) + "?")

					keypress = cv2.waitKey(1) & 0xFF
					while keypress not in [ord(x) for x in 'zxcvbnm,./']:
						keypress = cv2.waitKey(1) & 0xFF
					if keypress == ord('z'):
						self.box_generators[self.boxes[i]] = 'oo'
					elif keypress == ord('x'):
						self.box_generators[self.boxes[i]] = 'blurp'
					elif keypress == ord('c'):
						self.box_generators[self.boxes[i]] = 'lulpump'
					elif keypress == ord('v'):
						self.box_generators[self.boxes[i]] = 'yeuh'

				print('reached end')

		elif keypress == ord('n'):
			self.calibration_mode()
		else:
			print("you should not be here!!")

		

	def main(self):

		self.count += 1

		# past_frame = np.zeros((720,1080))
		# t = time.time()
		ret, frame = self.cap.read()
		# print("checkpoint 1", str(time.time() - t))

		# t = time.time()
		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		# print("checkpoint 2", str(time.time() - t))

		# t = time.time()
		edges = cv2.Canny(frame, 100, 200)				
		# print("checkpoint 3", str(time.time() - t))

		# t = time.time()
		# boxes = self.shape_detector.find_bounding_boxes(edges)
		# print("checkpoint 4", str(time.time() - t))

		current_frame = edges/255

		# box = [(330, 570), (370, 570), (330, 620),(370, 620)]
		# self.draw_hard_code(box, current_frame)
		
		# self.draw_shape_detector_box(current_frame)

		np_kernel = np.ones((3,10))
		threshold = 6
		kernel_group = (np_kernel, threshold)
		# frames = (current_frame, self.past1_frame, self.past2_frame)
		frames = (current_frame, self.past1_frame)


		# print("========= BOXeS ==========")
		# for poly in self.boxes:
		# 	print(poly)
		# 	print("\n")
		# 	for i, j in poly.points:
		# 		for x in range(-5, 6):
		# 			for y in range(-5, 6):
		# 				current_frame[i + x][j+ y] = 1
		# 	for i, j in poly.get_valid_shape():
		# 		for x in range(-5, 6):
		# 			for y in range(-5, 6):
		# 				current_frame[i + x][j+ y] = 1
		# print("========== END BOXES =======")


		sections_being_played = defaultdict(list)

		for bounding_box in self.boxes:
			box = bounding_box.get_valid_shape()
			touch_down = self.find_touch_vectorized(kernel_group, frames, box)

			if touch_down:
				# print("count: " + str(self.count))
				# print(touch_down)
				# print('box: ' + str(box))

				if self.sections:
					sections_being_played[self.box_to_section[bounding_box]].append(bounding_box)
				else:
					sound = self.box_generators[bounding_box]
					state = self.box_state[bounding_box]
					if sound:
						if self.count - state < self.press_threshold:
							pass # do nothing
						else:
							# print("YEAH IM GETTING PRESSED")
							self.box_state[bounding_box] = self.count
							self.audio.play_audio(sound)


		for section in sections_being_played:
			sounds = sections_being_played[section]
			# print(sounds)
			if sounds:
				bounding_box = max(sounds, key=lambda x: x.get_valid_shape()[0][0])
				# print("this is the box: " + str(bounding_box))

				sound = self.box_generators[bounding_box]

				# Represents the last frame this box was touched
				state = self.box_state[bounding_box]

				# If its a touch down, need to see if it's still a residual from current press or a new press
				if sound:
					if self.count - state < self.press_threshold:
						pass # do nothing
					else:
						# print("YEAH IM GETTING PRESSED")
						self.box_state[bounding_box] = self.count
						self.audio.play_audio(sound)

			

		# t = time.time()
		# box = [(320, 777), (407, 777), (320, 874), (407, 874)]
		# val = self.find_touch_vectorized(kernel_group, frames, box)
		# # print(val)
		# if val:
		# 	self.count += 1
		# 	print("count: " + str(self.count))
		# 	print(val)
		# print(time.time() - t)

		# print_lowest_i(edges)
		# print_lowest_j(edges)
		
		# t = time.time()
		cv2.imshow('current frame', current_frame)
		# print("checkpoint 6", str(time.time() - t))
		
		self.past2_frame, self.past1_frame = self.past1_frame, current_frame
		# x = input()


# L = Launchpad(None)


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

# while True:
# 	L.main()