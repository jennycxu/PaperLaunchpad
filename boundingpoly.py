import numpy as np
class BoundingPoly :
    def __init__(self, points):
       self.points = points 
    def get_area(self):
        x = []
        y = []
        for point in self.points:
            x.append(point[0])
            y.append(point[1])
        return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))
    def is_valid_size(self):
        if self.get_area() > 2000:
            return True
        return False