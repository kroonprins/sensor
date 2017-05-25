""" Utility function to retrieve information about the device
"""

def get_device_id():
    """ Get unique id for the device.
        It extracts the serial from the cpuinfo file
    """
    cpuinfo = open('/proc/cpuinfo', 'r')
    for line in cpuinfo:
        if line[0:6] == 'Serial':
            cpuserial = line[10:26]
    cpuinfo.close()
    return cpuserial
