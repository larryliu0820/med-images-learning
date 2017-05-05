import copy
import dicom
import numpy
import matplotlib.pyplot as plt
import matplotlib.path as path

import point as pt
import util

class ImageWithRoi:
    row = None
    data = None
    FIELDS = [
        'ImageNo', 'RoiNo', 'RoiMean',
        'RoiMin', 'RoiMax', 'RoiTotal',
        'RoiDev', 'RoiName', 'RoiCenterX',
        'RoiCenterY', 'RoiCenterZ', 'LengthCm',
        'LengthPix', 'AreaPix2', ' AreaCm2',
        'RoiType', 'SOPInstanceUID', 'SeriesInstanceUID',
        'StudyInstanceUID', 'NumOfPoints'
    ]
    pts = None
    pts_coor_set = None
    pts_coor_list = None
    ref_pt = None
    is_ref = False
    image_file = None
    image_obj = None
    max_x = None
    min_x = None
    max_y = None
    min_y = None
    pts_angle_list = None
    pts_in_roi = None

    def __init__(self, row, image_file):
        self.data = dict()
        self.pts = list()
        self.row = row
        self.image_file = image_file
        self.image_obj = dicom.read_file(self.image_file)
        self.pts_coor_set = set()
        self.pts_coor_list = list()
        self.pts_in_roi = set()
        self.pts_angle_list = list()
        for i, field in enumerate(self.FIELDS):
            self.data[field] = self.row[i]
        if "RoiName" in self.data and self.data["RoiName"] == "reference":
            self.is_ref = True
        self.get_boundary_pts()
        self.calc_pts_angle()
        self.find_roi_pts()

    def get_boundary_pts(self):
        idx = 23
        while idx < len(self.row):
            if self.row[idx] != "" and self.row[idx] != "":
                pxX = int(round(float(self.row[idx])))
                pxY = int(round(float(self.row[idx + 1])))
                if (pxX, pxY) not in self.pts_coor_set:
                    self.pts.append(pt.Point(pxX, pxY))
                    self.pts_coor_set.add((pxX, pxY))
                    self.pts_coor_list.append([pxX, pxY])
            idx += 5

    def calc_pts_angle(self):
        assert len(self.pts) is not 0
        self.max_x, self.min_x = self.pts[0].xcor, self.pts[0].xcor
        self.max_y, self.min_y = self.pts[0].ycor, self.pts[0].ycor
        self.ref_pt = self.pts[0]
        self.ref_pt.angle = 0
        for point in self.pts[1:]:
            point.ref_point = self.ref_pt
            point.calc_angle()
            self.max_x = max(self.max_x, point.xcor)
            self.min_x = min(self.min_x, point.xcor)
            self.max_y = max(self.max_y, point.ycor)
            self.min_y = min(self.min_y, point.ycor)
        self.pts.sort(key=lambda x: x.angle)
        self.pts_angle_list = [p.angle for p in self.pts]

    def find_roi_pts(self):
        for x in range(int(self.min_x), int(self.max_x)):
            for y in range(int(self.min_y), int(self.max_y)):
                curr_pt = pt.Point(x, y, self.ref_pt)
                if self.point_in_roi2(curr_pt):
                    self.get_roi_pt_val(curr_pt)
                    self.pts_in_roi.add(copy.deepcopy(curr_pt))

    def point_in_roi(self, point):
        if (point.xcor, point.ycor) in self.pts_coor_set:
            return False
        if point.angle > max(self.pts_angle_list) or point.angle < min(self.pts_angle_list):
            return False
        [low, high] = util.binary_search(self.pts_angle_list, point.angle)
        if low == high:
            if low == 0:
                low = 1
            return self.pts[low].dist_to_ref > point.dist_to_ref
        is_valid = util.point_in_triangle(point, self.pts[low], self.pts[high], self.ref_pt)
        return is_valid

    def plot_roi(self):
        assert len(self.pts_in_roi) is not 0
        assert len(self.pts) is not 0
        # TODO: plot roi
        plt.scatter([p.xcor for p in self.pts], [p.ycor for p in self.pts])
        plt.scatter([p.xcor for p in self.pts_in_roi], [p.ycor for p in self.pts_in_roi])

    def get_roi_pt_val(self, p):
        p.val_in_image = self.image_obj.pixel_array[p.ycor][p.xcor]

    def point_in_roi2(self, point):
        boundary_path = path.Path(numpy.array(self.pts_coor_list))
        coor = (point.xcor, point.ycor)
        return coor not in self.pts_coor_set and boundary_path.contains_point(coor)
