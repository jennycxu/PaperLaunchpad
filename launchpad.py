import cv2
import numpy as np 


class Launchpad():

	def __init__(self):
		self.cap = cv2.VideoCapture(0)

	def has_changed(self, i, j, past_frame, tolerance):
		for x in range (i - tolerance, i + tolerance):
			for y in range (j - tolerance, j + tolerance):
				if past_frame[x][j] > 0:
					return False
		return True

	def find_lowest_i(self, edges):
		max_i = 0
		for i in range(400,720):
			for j in range(200,1000):
				if not edges[i][j] == 0:
					if i > max_i:
						max_i = i 
		print(max_i)

	def find_lowest_j(self, edges):
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
				total += kernel[x][y]*image[x_start + x][y_start + y]

		return total


	# Box is given as a list of coordinates ((x1, y1), (x1, y2) ,(x2, y1) ,(x2, y2))
	# determines a touch by applying a certain kernel (probably a long rectangle) 
	def find_touch(self, kernel, frames, box):
		# x and y are num rows and num columns of the kernel
		x, y = len(kernel), len(kernel[0])
		left, top = box[0]
		right, bot = box[-1]

		frame, past_frames = frames[0], frames[1:]

		# formula is right_bound - length of kernel + 1, so we add 2 because it's a range
		for i in range(left, right - x + 2):
			for j in range(top, bot - y + 2):
				apply_kernel(kernel, frame, (i,j))

	def main(self):
		past_frame = np.zeros((720,1080))

		while True:
			ret, frame = self.cap.read()
			# print(type(frame))
			# print(frame.shape)
			# gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			# laplacian = cv2.Laplacian(gray, cv2.CV_64F)
			# edges = cv2.Canny(gray, 100, 200)
			# print(frame.shape)

			edges = cv2.Canny(frame, 100, 200)/255
			current_frame = edges

			hard_code = [(300, 520), (300, 670), (400, 520) ,(400, 670)]
			for i, j in hard_code:
				for x in range(-5, 6):
					for y in range(-5, 6):
						edges[i + x][j+ y] = 100

			

			possible_changes = []
			for i in range(hard_code[0][0], hard_code[-1][0]):
				for j in range(hard_code[0][1], hard_code[-1][1]):
					p = current_frame[i][j]
					if p > 0 and self.has_changed(i, j, past_frame, 5):
						possible_changes.append((i,j))

			if possible_changes:
				tip = max(possible_changes, key=lambda z: z[0])

				print("button press! At: " + str(tip))



			# find_lowest_i(edges)
			# find_lowest_j(edges)

			# print(edges/255)
			# print(gray)
			# print(type(edges))
			# print(edges.shape)

			# cv2.imshow("frame", gray)
			# cv2.imshow("laplacian", laplacian)
			
			cv2.imshow('edges', edges)

			if cv2.waitKey(1) & 0xFF == ord('q'):
				break

			past_frame = current_frame

		self.cap.release()
		cv2.destroyAllWindows()

L = Launchpad()

# #  Kernel testing
# image = [[0, 0, 1, 1, 0], [0 , 0, 1, 1, 0], [0, 0, 0, 0, 0]]
# kernel = [[1,1],[1,1]]
# print(L.apply_kernel(kernel, image, (0, 1)))

L.main()