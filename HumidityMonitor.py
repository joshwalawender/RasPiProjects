#!/usr/env/python

from __future__ import division, print_function

## Import General Tools
import sys
import os
import argparse
import logging
import time
import numpy as np

import Adafruit_DHT
# import DHT22
# import DS18B20
# import urllib2
# import Carriots
import humiditycalc

# import astropy.io.ascii as ascii
# import astropy.table as table

threshold_humid = 55
threshold_wet = 75

##-------------------------------------------------------------------------
## Main Program
##-------------------------------------------------------------------------
def measure(verbose=False):
    ##-------------------------------------------------------------------------
    ## Create logger object
    ##-------------------------------------------------------------------------
    logger = logging.getLogger('MyLogger')
    logger.setLevel(logging.DEBUG)
    ## Set up console output
    LogConsoleHandler = logging.StreamHandler()
    if verbose:
        LogConsoleHandler.setLevel(logging.DEBUG)
    else:
        LogConsoleHandler.setLevel(logging.INFO)
    LogFormat = logging.Formatter('%(asctime)23s %(levelname)8s: %(message)s')
    LogConsoleHandler.setFormatter(LogFormat)
    logger.addHandler(LogConsoleHandler)
    ## Set up file output
    LogFileName = os.path.join('/', 'home', 'joshw', 'logs', time.strftime('HumidityLog_%Y%m%d.txt', time.localtime()))
    LogFileHandler = logging.FileHandler(LogFileName)
    LogFileHandler.setLevel(logging.DEBUG)
    LogFileHandler.setFormatter(LogFormat)
    logger.addHandler(LogFileHandler)

    ##-------------------------------------------------------------------------
    ## Get Temperature and Humidity Values
    ##-------------------------------------------------------------------------
    logger.info('#### Reading Temperature and Humidity Sensors ####')
    logger.info('Reading DHT22')
    sensor = Adafruit_DHT.AM2302
    pin = 4
    DHT_humidity, DHT_temperature_C = Adafruit_DHT.read_retry(sensor, pin)
    if not DHT_humidity or not DHT_temperature_C:
        DHT_humidity, DHT_temperature_C = Adafruit_DHT.read_retry(sensor, pin)
    if not DHT_humidity or not DHT_temperature_C:
        print('Read failed a second time.')
        sys.exit(1)
    
    DHT_temperature_F = 32. + 9./5.*DHT_temperature_C

    logger.info('  Temperature = {:.3f} F, Humidity = {:.1f} %'.format(DHT_temperature_F, DHT_humidity))
    AH = humiditycalc.relative_to_absolute_humidity(DHT_temperature_C, DHT_humidity)
    logger.info('  Absolute Humidity = {:.2f} g/m^3'.format(AH))


    ##-------------------------------------------------------------------------
    ## Determine Status Using Humidity
    ##-------------------------------------------------------------------------
    if (DHT_humidity < threshold_humid):
        status = 'OK'
    elif (DHT_humidity > threshold_humid) and (DHT_humidity < threshold_wet):
        status = 'HUMID'
    else:
        status = 'WET'
    logger.info('Status: {}'.format(status))


    ##-------------------------------------------------------------------------
    ## Determine Status and Alarm Using History
    ##-------------------------------------------------------------------------
    datestring = time.strftime('%Y%m%d_log.txt', time.localtime())
    timestring = time.strftime('%Y/%m/%d %H:%M:%S HST', time.localtime())
    datafile = os.path.join('/', 'home', 'joshw', 'logs', datestring)
    logger.debug("Reading history data from file: {0}".format(datafile))
    dataFO = open(datafile, 'a+')
    lines = dataFO.readlines()

    if len(lines) == 0:
        dataFO = open(datafile, 'a')
        dataFO.write('# {},{},{},{},{},{}\n'.format(
                     'date',\
                     'time',\
                     'temperature (F)',\
                     'humidity (%)',\
                     'absolute humidity (g/m^3)',\
                     'status'))
        data = []
    else:
        data = []
        for line in lines:
            if line[0] != '#':
                data.append(line.strip('\n').split(','))
            

    translation = {'OK':0, 'HUMID':1, 'WET':2, 'ALARM':2}
    if len(data) > 6:
        recent_status_vals = [translation[line[5]] for line in data][-6:]
        recent_status = np.mean(recent_status_vals)
    if len(data) > 23:
        recent_status_vals = [translation[line[5]] for line in data][-23:]
        recent_alarm = 2 in recent_status_vals
        logger.debug('  Recent Status = {:.2f}, Current Status = {}, Recent alarm: {}'.format(recent_status, status, recent_alarm))
        if (recent_status > 0.5) and not status == 'OK' and not recent_alarm:
            status = 'ALARM'


    ##-------------------------------------------------------------------------
    ## Record Values to Table
    ##-------------------------------------------------------------------------
    dataFO.write('{},{},{:.1f},{:.1f},{:.2f},{}\n'.format(
                 timestring[0:10],\
                 timestring[11:23],\
                 DHT_temperature_F,\
                 DHT_humidity,\
                 AH,\
                 status))


    ## Log to Carriots
#     logger.info('Sending Data to Carriots')
#     logger.debug('  Creating Device object')
#     Device = Carriots.Client(device_id="Shed@joshwalawender")
#     logger.debug('  Reading api key')
#     Device.read_api_key_from_file(file=os.path.join(os.path.expanduser('~joshw'), '.carriots_api'))
#     data_dict = {'Temperature1': sensor.temperatures_F[0], \
#                  'Temperature2': sensor.temperatures_F[1], \
#                  'Temperature3': DHT.temperature_F, \
#                  'Humidity': DHT.humidity, \
#                  'Absolute Humidity': AH, \
#                  'Status': status
#                  }
#     logger.debug(data_dict)
#     logger.debug('  Uploading data')
#     try:
#         Device.upload(data_dict)
#     except urllib2.HTTPError as e:
#         logger.critical('  Upload failed')
#         logger.critical('  {}'.format(e.code))
#         logger.critical('  {}'.format(e.reason))
#     except:
#         logger.critical('  Upload failed')
#         logger.critical('  Unexpected error: {}'.format(sys.exc_info()[0]))
#     logger.info('Done')



##-------------------------------------------------------------------------
## Make Plot
##-------------------------------------------------------------------------
def plot(verbose=False):

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as pyplot
    pyplot.ioff()

    ##-------------------------------------------------------------------------
    ## Create logger object
    ##-------------------------------------------------------------------------
    logger = logging.getLogger('MyLogger')
    logger.setLevel(logging.DEBUG)
    ## Set up console output
    LogConsoleHandler = logging.StreamHandler()
    if verbose:
        LogConsoleHandler.setLevel(logging.DEBUG)
    else:
        LogConsoleHandler.setLevel(logging.INFO)
    LogFormat = logging.Formatter('%(asctime)23s %(levelname)8s: %(message)s')
    LogConsoleHandler.setFormatter(LogFormat)
    logger.addHandler(LogConsoleHandler)
    ## Set up file output
    LogFileName = os.path.join('/', 'home', 'joshw', 'logs', 'PlotLog.txt')
    LogFileHandler = logging.FileHandler(LogFileName)
    LogFileHandler.setLevel(logging.DEBUG)
    LogFileHandler.setFormatter(LogFormat)
    logger.addHandler(LogFileHandler)

    ##-------------------------------------------------------------------------
    ## Read Log File
    ##-------------------------------------------------------------------------
    datestring = time.strftime('%Y%m%d_log.txt', time.localtime())
    datafile = os.path.join('/', 'home', 'joshw', 'logs', datestring)
    logger.info("Reading Data File: "+datafile)

    dataFO = open(datafile, 'a+')
    lines = dataFO.readlines()
    data = []
    for line in lines:
        if line[0] != '#':
            data.append(line.strip('\n').split(','))

    dates = [val[0] for val in data]
    time_strings = [val[1] for val in data]
    times = [(time.strptime(val[1], '%H:%M:%S HST').tm_hour +\
              time.strptime(val[1], '%H:%M:%S HST').tm_min/60.)\
             for val in data ]
    temperature = [float(val[2]) for val in data]
    humidity = [float(val[3]) for val in data]
    AH = [float(val[4]) for val in data]
    status = [val[5] for val in data]


    ##-------------------------------------------------------------------------
    ## Plot
    ##-------------------------------------------------------------------------
#     PlotFileName = time.strftime('%Y%m%d.png', time.localtime())
    PlotFileName = 'latest.png'
    PlotFile = os.path.join('/', 'home', 'joshw', 'logs', PlotFileName)
    logger.info("Writing Output File: "+PlotFile)
    dpi=72
    Figure = pyplot.figure(figsize=(16,10), dpi=dpi)

    HumidityAxes = pyplot.axes([0.10, 0.43, 0.9, 0.40])
    title_string = '{:10s} at {:12s}:\n'.format(dates[-1], time_strings[-1])
    title_string += 'Temperature = {:.1f} F, '.format(temperature[-1])
    title_string += 'Humidity = {:.0f} %'.format(humidity[-1])
    pyplot.title(title_string)
    pyplot.plot(times, humidity, 'ko', label="Humidity", mew=0, ms=3)
    pyplot.plot([0, 24], [threshold_humid, threshold_humid],\
                'y-', label='threshold humidity', linewidth=3, alpha=0.8)
    pyplot.plot([0, 24], [threshold_wet, threshold_wet],\
                'r-', label='threshold humidity', linewidth=3, alpha=0.8)
    pyplot.yticks(range(10,100,10))
    pyplot.ylim(25,95)
    pyplot.ylabel("Humidity (%)")

    pyplot.xticks([])
    pyplot.xlim(0,24)
    pyplot.grid()

    AbsHumidityAxes = HumidityAxes.twinx()
    AbsHumidityAxes.set_ylabel('Abs. Hum. (g/m^3)', color='b')
    pyplot.plot(times, AH, 'bo', label="Abs. Hum.", mew=0, ms=3)
    pyplot.yticks(range(00,45,5))
    pyplot.ylim(7.5,22.5)

    pyplot.xticks(range(0,25,1))
    pyplot.xlim(0,24)
    pyplot.xlabel('Hours (HST)')


    TemperatureAxes = pyplot.axes([0.10, 0.05, 0.9, 0.35])
    pyplot.plot(times, temperature, 'go', label="Termperature", mew=0, ms=3)
    pyplot.xticks(range(0,25,1))
    pyplot.yticks(range(50,110,5))
    pyplot.xlim(0,24)
    pyplot.ylim(70,100)
    pyplot.xlabel('Hours (HST)')
    pyplot.ylabel("Temperature (F)")
    pyplot.grid()

    pyplot.savefig(PlotFile, dpi=dpi, bbox_inches='tight', pad_inches=0.10)
    logger.info("Done")


    ##-------------------------------------------------------------------------
    ## Create Daily Symlink if Not Already
    ##-------------------------------------------------------------------------
    LinkFileName = 'latest.png'
    LinkFile = os.path.join('/', 'home', 'joshw', 'logs', LinkFileName)
    if not os.path.exists(LinkFile):
        logger.info('Making {} symlink to {}'.format(LinkFile, PlotFile))
        os.symlink(PlotFile, LinkFile)
        logger.info("Done")



def main():
    ##-------------------------------------------------------------------------
    ## Parse Command Line Arguments
    ##-------------------------------------------------------------------------
    ## create a parser object for understanding command-line arguments
    parser = argparse.ArgumentParser(
             description="Program description.")
    ## add flags
    parser.add_argument("-v", "--verbose",
        action="store_true", dest="verbose",
        default=False, help="Be verbose! (default = False)")
    parser.add_argument("-p", "--plot",
        action="store_true", dest="plot",
        default=False, help="Make plot.")
    args = parser.parse_args()

    if not args.plot:
        measure(verbose=args.verbose)
    else:
        plot(verbose=args.verbose)


if __name__ == '__main__':
    main()
