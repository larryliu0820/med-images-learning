import os
import sys
import csv
import zipfile
import image_with_roi as image

DATA_DIR = "/Volumes/imaging/strokeplaque"


class Patient:
    name = None
    images = None
    csv = None

    patient_zip = None
    patient_dir = None
    images_dir = None

    csv_reader = None

    def __init__(self, csv_name):
        self.csv = csv_name
        self.name = self.csv.split('/')[-1].split('-')[0]
        self.patient_dir = DATA_DIR + "/%s/" % self.name.replace(' ', '_')
        if not os.path.isdir(self.patient_dir):
            self.patient_zip = DATA_DIR + "/%s.zip" % self.name.replace(' ', '_')
            assert os.path.isfile(self.patient_zip)
            zip_ref = zipfile.ZipFile(self.patient_zip, 'r')
            zip_ref.extractall(DATA_DIR + "/")
        self.images_dir = self.patient_dir + "/study/PLAQUE_T2_FRFSE/"
        with open(self.csv) as f:
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


