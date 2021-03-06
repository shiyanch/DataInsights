from __future__ import print_function

import sys
from csv import reader
from operator import add
from pyspark import SparkContext
from datetime import datetime

def format_date(row):
    crime_date = datetime.strptime(row[0], '%Y-%m-%d %H:%M')
    temperature = 0 if row[1][0] == '' else int(row[1][0])
    humidity = 0 if row[1][1] == '' else int(row[1][1])
    wind_speed = 0 if row[1][2] == '' else int(row[1][2])
    return crime_date.strftime('%Y%m%d'), (temperature, humidity, wind_speed, row[1][3])

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: spark_weather_average.py <file>", file=sys.stderr)
        exit(-1)
    sc = SparkContext()
    lines = sc.textFile(sys.argv[1], 1)
    lines = lines.mapPartitions(lambda x : reader(x)).map(lambda row: (row[5], (row[10], row[16], row[17], 1)))
    counts = lines.map(format_date).reduceByKey(lambda x,y: (x[0]+y[0], x[1]+y[1], x[2]+y[2], x[3]+y[3]))
    counts = counts.map(lambda row : row[0]+", "+"%.2f, %.2f, %.2f" % (row[1][0]/row[1][3], row[1][1]/row[1][3], row[1][2]/row[1][3]))
    counts.saveAsTextFile("weather_average_by_day.out")
    sc.stop()
