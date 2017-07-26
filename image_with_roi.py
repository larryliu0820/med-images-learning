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
    boundary_pts = None
    pts_coor_set = None
    pts_coor_list = None
    ref_pt = None
    is_ref = False
    image_file = None
    image_obj = None
    max_x = 0
    min_x = 0
    max_y = 0
    min_y = 0
    pts_angle_list = None
    pts_in_roi = None
    roi_val_list = None
    roi_val_mean = None

    def __init__(self, row, image_file):
        self.data = dict()
        self.boundary_pts = list()
        self.row = row
        self.image_file = image_file
        self.image_obj = dicom.read_file(self.image_file.decode('utf-8'))
        self.pts_coor_set = set()
        self.pts_coor_list = list()
        self.pts_in_roi = set()
        self.pts_angle_list = list()
        self.roi_val_list = list()

        for i, field in enumerate(self.FIELDS):
            self.data[field] = self.row[i]
        assert "RoiMean" in self.data
        self.roi_val_mean = self.data["RoiMean"]
        if "RoiType" in self.data and self.data["RoiType"] == "6":
            self.is_ref = True
        self.get_boundary_pts_from_csv()
        self.find_roi_pts()

    def get_boundary_pts_from_csv(self):
        for idx in range(23, len(self.row), 5):
            if self.row[idx] != "" and self.row[idx] != "":
                pxX = int(round(float(self.row[idx])))
                pxY = int(round(float(self.row[idx + 1])))
                self.max_x = max(self.max_x, pxX)
                self.max_y = max(self.max_y, pxY)
                self.min_x = min(self.min_x, pxX)
                self.min_y = min(self.min_y, pxY)
                if (pxX, pxY) not in self.pts_coor_set:
                    self.boundary_pts.append(pt.Point(pxX, pxY))
                    self.pts_coor_set.add((pxX, pxY))
                    self.pts_coor_list.append([pxX, pxY])

    def find_roi_pts(self):
        boundary_path = path.Path(numpy.array(self.pts_coor_list))
        for x in range(int(self.min_x), int(self.max_x)):
            for y in range(int(self.min_y), int(self.max_y)):
                curr_pt = pt.Point(x, y, self.ref_pt)
                if self.point_in_roi(boundary_path, curr_pt):
                    self.roi_val_list.append(self.get_roi_pt_val(curr_pt))
                    self.pts_in_roi.add(copy.deepcopy(curr_pt))

    def plot_roi(self):
        assert len(self.pts_in_roi) is not 0
        assert len(self.boundary_pts) is not 0
        # TODO: plot roi
        plt.scatter([p.xcor for p in self.boundary_pts], [p.ycor for p in self.boundary_pts], color='blue')
        plt.scatter([p.xcor for p in self.pts_in_roi], [p.ycor for p in self.pts_in_roi], color='red')

    def get_roi_pt_val(self, p):
        p.val_in_image = self.image_obj.pixel_array[p.ycor][p.xcor]
        return p.val_in_image

    def point_in_roi(self, boundary_path, point):
        coor = (point.xcor, point.ycor)
        return coor not in self.pts_coor_set and boundary_path.contains_point(coor)

    def plot_histogram(self):
        plt.hist(self.roi_val_list)
