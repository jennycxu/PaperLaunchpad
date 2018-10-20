import numpy as np
class BoundingPoly :
    def __init__(self, points):
       self.points = points 
       self.valid_size = 2000
       self.similar_threshold = 50 
       self.valid_area_shift = 20

    def get_area(self):
        x = []
        y = []
        for point in self.points:
            x.append(point[0])
            y.append(point[1])
        return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

    def is_valid_size(self):
        if self.get_area() > self.valid_size:
            return True
        return False

    # returns the smaller version of the polygon that should be allowed for thresholding
    # for now return a rectangle 
    def get_valid_shape(self):
        new_points = []
        min_x,min_y,max_y,max_x = [-1]*4

        for point in self.points:
            x = point[0]
            y = point[1]
            if x < min_x or min_x == -1:
                min_x = x
            if x > max_x or max_x == -1:
                max_x = x
            if y < min_y or min_y == -1:
                min_y = y
            if y > max_y or max_y == -1:
                max_y = y
        min_x += self.valid_area_shift
        max_x -= self.valid_area_shift
        min_y += self.valid_area_shift
        max_y -= self.valid_area_shift
        new_points.append((min_x,min_y))
        new_points.append((min_x,max_y))
        new_points.append((max_x,min_y))
        new_points.append((max_x,max_y))
        return new_points

    def equals(self, other):
        points_similar = False
        for i in range(len(self.points)):
            x,y = self.points[i]
            x2,y2 = other.points[i]
            # if the points are close enough 
            if(abs(x-x2) + abs(y-y2) < self.similar_threshold):
                points_similar = True
           # print(abs(x-x2) + abs(y-y2))

        if points_similar:
            return True
        return False