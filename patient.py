import os
import sys
import csv
import numpy
import zipfile
import codecs
import image_with_roi as image
import matplotlib.pyplot as plt

DATA_DIR = "/Volumes/imaging/strokeplaque/"


class Patient:
    name = None
    images = None
    csv = None

    patient_zip = None
    patient_dir = None
    images_dir = None

    csv_reader = None

    norm_all_roi_value = None
    ref_roi_mean = None
    histogram = None
    bins = None

    output_csv = None

    def __init__(self, csv_name):
        self.csv = DATA_DIR + csv_name.replace('/', ':')
        self.name = self.csv.split('/')[-1].split('-')[0].replace(',', '')
        self.norm_all_roi_value = list()
        self.patient_dir = DATA_DIR + "%s/" % self.name.replace(' ', '_')
        assert os.path.isdir(self.patient_dir), "No image directory of patient: %s" % self.name
        # if not os.path.isdir(self.patient_dir):
        #     self.patient_zip = DATA_DIR + "%s.zip" % self.name.replace(' ', '_')
        #     assert os.path.isfile(self.patient_zip)
        #     zip_ref = zipfile.ZipFile(self.patient_zip, 'r')
        #     zip_ref.extractall(DATA_DIR)
        dir_gen = os.walk(self.patient_dir+"study")
        dir_gen.next()
        self.images_dir = dir_gen.next()[0] + "/"
        with codecs.open(self.csv, 'r', 'utf-8') as f:
            self.images = list()
            self.csv_reader = csv.reader(f)
            self.csv_reader.next()
            try:
                for row in self.csv_reader:
                    if int(row[0])+1 < 10:
                        name = "IM-0001-000%d.dcm"
                    else:
                        name = "IM-0001-00%d.dcm"
                    image_file = self.images_dir + name % (int(row[0]) + 1)
                    assert os.path.isfile(image_file)
                    self.images.append(image.ImageWithRoi(row, image_file))
            except csv.Error as e:
                sys.exit('file %s, line %d: %s' % (self.csv, self.csv_reader.line_num, e))

    def get_all_roi_val(self):
        ref_mean = [i.roi_val_mean for i in self.images if i.is_ref]
        assert len(ref_mean) != 0, "No reference image found."
        assert len(ref_mean) == 1, "More than 1 reference images found."
        self.ref_roi_mean = ref_mean[0]
        roi_val_lists = [i.roi_val_list for i in self.images if not i.is_ref]
        self.norm_all_roi_value = [v / float(self.ref_roi_mean) for l in roi_val_lists for v in l]
        # default bins
        self.bins=numpy.arange(round(min(self.norm_all_roi_value), 1), round(max(self.norm_all_roi_value), 1), 0.1)

    def get_histogram(self):
        assert len(self.norm_all_roi_value) > 0 and len(self.bins) > 0, "Please call self.get_all_roi_val first!"
        self.histogram,_ = numpy.histogram(self.norm_all_roi_value, self.bins)

    def write_histogram_to_csv(self):
        if not self.output_csv:
            self.output_csv = DATA_DIR + 'output.csv'
        with open(self.output_csv, 'a') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow([self.name] + list(self.histogram))