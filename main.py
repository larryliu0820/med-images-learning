import os
import sys
import csv
import glob
import math
import numpy
import getopt
import patient as p


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hd:")
    except getopt.GetoptError:
        print "wtf"
        sys.exit(2)
    directory = None
    for opt,arg in opts:
        if opt == '-h':
            print 'wtf'
            sys.exit()
        elif opt == '-d':
            directory = arg
    assert os.path.isdir(directory), "Please select a valid directory."
    print 'Using directory %s' % directory
    os.chdir(directory)
    csv_files = [f for f in glob.glob('*.csv')]
    patients = [p.Patient(cf) for cf in csv_files]
    boundary = list()
    for patient in patients:
        patient.get_all_roi_val()
        boundary += [max(patient.norm_all_roi_value), min(patient.norm_all_roi_value)]
    min_val, max_val = min(boundary), max(boundary)
    bins = numpy.arange(math.floor(min_val * 10) / 10, math.ceil(max_val * 10) / 10, 0.1)
    output_file = directory + "/output.csv"
    with open(output_file, 'a') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(["Name"] + list(bins))
    for patient in patients:
        patient.bins = bins
        patient.get_histogram()
        patient.output_csv = output_file
        patient.write_histogram_to_csv()
        print "Finish writing patient: %s" % patient.name

if __name__ == "__main__":
    main(sys.argv[1:])
