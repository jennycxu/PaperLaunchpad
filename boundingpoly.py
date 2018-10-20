import numpy as np
class BoundingPoly :
    def __init__(self, points):
       self.points = points 
       self.valid_size = 2000
       self.similar_threshold = 50 
       
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
    def equals(self, other):
        points_similar = False
        for i in range(len(self.points)):
            x,y = self.points[i]
            x2,y2 = other.points[i]
            # if the points are close enough 
            if(abs(x-x2) + abs(y-y2) < self.similar_threshold):
                points_similar = True
            print(abs(x-x2) + abs(y-y2))

        if points_similar:
            return True
        return False