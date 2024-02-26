'''
Methods for RAM Management
'''

# Import libraries
import os


###########################################

def convert_bytes(number):
    '''Function to convert file size to known units'''
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if number < 1024.0:
            return "%3.1f %s" % (number, x)
        number /= 1024.0
    return

###########################################

def file_size(file):
    '''Function to calculate filesize'''
    if os.path.isfile(file):
        file_info = os.stat(file)
        return convert_bytes(file_info.st_size)
    return

###########################################

