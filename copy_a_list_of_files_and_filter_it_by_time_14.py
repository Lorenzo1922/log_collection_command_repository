"""script that will copy files from /log/ to /tmp/ , ask to user the time range, filter the files by time range and create other files filtered and named accordingly"""

#test firewall access id =   49c391b7-5a96-32ff-b9be-40026d64c2b3@eu2.apu.sophos.com    723470c7-393e-357f-ae3f-7b8ba05cec77@eu2.apu.sophos.com

######### xg used timestamps #########
#Sophos Firewall has 4 different timestamps
#2022-08-03 00:14:43    like tomcat.log has it
#2021-09-21 01:59:54Z   like charon.log has it - Z stands for UTC+0 timezone, without 0, it is firewall local timezone
#Aug 03 07:25:01Z      like garner.log has it
#Aug  2 15:17:09Z       like syslog.log has it

#let's create 4 different variables with the different timestamps
#start_date = 2022-08-03 08:33:54             let's say this is German time zone = UTC +2
#converted_start_date_1 = 2022-08-03 07:33:54Z
#converted_start_date_2 = Aug 03 07:33:54Z
#converted_start_date_3 = Aug 3 07:33:54Z

import shutil       #is the module
import os           #is the module
import time
import datetime
from datetime import datetime
from datetime import timedelta
import subprocess

######### variables that will be used to print the lines inside the log filename #########
start_date = input("enter the start date in this format 2022-07-27 05:33 German time zone: ")
end_date = input("enter the end date in this format 2022-07-27 05:33 German time zone: ")
case_number = input("enter the case number: ")
#start_date = "2022-08-23 11:33"
#end_date = "2022-08-23 11:45"
#case_number = "4567"
n = 2                                  #variable with number I need to subtract from the hour

######### create a directory with the name of the case number #########
path = os.getcwd()       #detect the current working directory and print it
path = '/tmp'
joined_path = os.path.join(path,case_number)        #will create a directory like /tmp/<case_number>
isExist = os.path.exists(joined_path) #check whether the specified path exists and if not create a new one
if not isExist:
  os.makedirs(joined_path)
  print("Created directory "+joined_path)

path = os.getcwd()       #detect the current working directory and print it
path = '/tmp'
joined_path_filtered = os.path.join(path,case_number+'_filtered_by_time_range')
isExist = os.path.exists(joined_path_filtered) #check whether the specified path exists and if not create a new one
if not isExist:
  os.makedirs(joined_path_filtered)
  print("Created directory "+joined_path_filtered)

######### start_date and end_date conversions functions #########
#create a function that will conver something like 2022-08-03 11:13 into this format 2022-08-03 10:13 
def from_date_format_0_to_1(date_value):     #I am creating a new function
    start_date_format = datetime.strptime(date_value, '%Y-%m-%d %H:%M')     # convert string to date
    utc_0_time = start_date_format - timedelta(hours=n) # Subtract 1 hours from datetime object 
    return utc_0_time
print(from_date_format_0_to_1(start_date))      #to user the created function and convert the start_date variable printing it
print(from_date_format_0_to_1(end_date))
converted_start_date_1 = from_date_format_0_to_1(start_date)
converted_start_date_1_string = converted_start_date_1.strftime("%Y-%m-%d %H:%M")
converted_end_date_1 = from_date_format_0_to_1(end_date)
converted_end_date_1_string = converted_end_date_1.strftime("%Y-%m-%d %H:%M")

#create a function that will conver something like 2022-08-03 11:13 into this format Aug 03 10:13 
def from_date_format_0_to_2(date_value):     #I am creating a new function
    start_date_format = datetime.strptime(date_value, '%Y-%m-%d %H:%M')     # convert string to date
    utc_0_time = start_date_format - timedelta(hours=n) # Subtract 1 hours from datetime object
    format_month_utc_start_date = utc_0_time.strftime("%Y,%b %d %H:%M")      # change format of date
    return format_month_utc_start_date.split(',')[1]           # return characters after comma ','  
print(from_date_format_0_to_2(start_date))      #to user the created function and convert the start_date variable printing it
print(from_date_format_0_to_2(end_date))
converted_start_date_2 = from_date_format_0_to_2(start_date)
converted_end_date_2 = from_date_format_0_to_2(end_date)

#create a function that will conver something like 2022-08-03 11:13 into this format Aug 3 10:13 
def from_date_format_0_to_3(date_value):     #I am creating a new function
    start_date_format = datetime.strptime(date_value, '%Y-%m-%d %H:%M')     # convert string to date
    utc_0_time = start_date_format - timedelta(hours=n) # Subtract 1 hours from datetime object
    format_month_utc_start_date = utc_0_time.strftime("%Y,%b %e %H:%M")      # change format of date
    return format_month_utc_start_date.split(',')[1]           # return characters after comma ','  
print(from_date_format_0_to_3(start_date))      #to user the created function and convert the start_date variable printing it
print(from_date_format_0_to_3(end_date))
converted_start_date_3 = from_date_format_0_to_3(start_date)
converted_end_date_3 = from_date_format_0_to_3(end_date)

######### create a function that will determine the line with first occurrence of start_date ######### 
def start_line_number(file_name, start_date):  #to create a function def <name_of_the_function>(arguments,arguments):
    line_number = 0   #create a variable called line_number and assign to it value 0
    with open(file_name, 'r') as read_obj: #with open function - open(file, mode)
        for line in read_obj:
            line_number += 1
            if start_date in line:    #if the date I did choose is in the line of the file
                return line_number    #keep not of the line of the fila and assign it to a variable

######### create a function that will determine the line behind last occurrence of end_date ######### 
def end_line_number(file_name, end_date):
    line_number = 0
    flag = 0
    with open(file_name, 'r') as read_obj:  
        for line in read_obj:
            line_number += 1
            if end_date in line:
                flag = line_number
    flag += 1        
    return (flag)              #flag should be the line number that contain the end date I did choose

######### create a function that will copy lines between first_line and last_line from src_file to dst_file
def copy_lines(src_file, dst_file, first_line, last_line):    
    with open(src_file, 'r') as read_obj:
        read = read_obj.readlines()[first_line:last_line]
    with open(dst_file,'a') as write_obj:
        for line in read:        
            write_obj.write(line)
    read_obj.close()
    write_obj.close()

######### create a function that will check free space of the partition,and if it is smaller than limit, stop the script ######### 
# reference, https://www.tutorialexample.com/a-simple-guide-to-python-get-disk-or-directory-total-space-used-space-and-free-space-python-tutorial/
def disk_space(partition, limit):
    usage = shutil.disk_usage(partition) # get usage details of the partition
    free = usage[2]   # get free space of the partition
    if int(free) < int(limit): # if free space is smaller than the limit
        print('Free space of ' + partition + ' is smaller than ' + str(limit) + ' bytes, quit the script now.')        # print error    
        exit()  # stop python

######### list of log file names #########
#date format 0 = 2022-08-03 08:33:54
logfiles_timestamp_type_0 = ['hbtrust.log','heartbeatd.log','red.log','reverseproxy.log','smtpd_main.log','tomcat.log']
#date format 1 = 2022-08-03 07:33:54Z
logfiles_timestamp_type_1 = ['awed.log','centralmanagement.log','charon.log','ips.log','msync.log','sophos-central.log','strongswan.log']
#date format 2 = Aug 03 07:33:54Z
logfiles_timestamp_type_2 = ['access_server.log','applog.log','csc.log','dgd.log','error_log.log','fwcm-eventd.log','fwcm-heartbeatd.log','fwcm-updaterd.log','networkd.log']
#date format 3 = Aug 3 07:33:54Z
logfiles_timestamp_type_3 = ['syslog.log']
#linux time format
logfiles_timestamp_type_4 = ['awarrenhttp.log']

######### copy log files from /log/ to /tmp/case_number/ directory with this for cycle #########
print("Copy the main log files from /log/ to /tmp/case_number")

for i in logfiles_timestamp_type_0:
    partition='/tmp'
    limit = 31744000                        #31744000 bytes equals to 250 MB
    disk_space(partition,limit)             #check /tmp partition making sure /tmp has more than 250MB free space
    src = '/log/'+i
#    dst =  '/tmp/'+i   
#    dst = '/tmp/456/'+i
    dst = '/tmp/'+case_number+'/'+i
    shutil.copyfile(src, dst)               #copy log files from /log to /tmp/ directory

#same for files in logfiles_timestamp_type_1
for i in logfiles_timestamp_type_1:
    partition='/tmp'
    limit = 31744000  # 31744000 bytes equals to 250 MB
    disk_space(partition,limit)  # check /tmp partition making sure /tmp has more than 250MB free space
    src = '/log/'+i
#    dst =  '/tmp/'+i   
#    dst = '/tmp/456/'+i 
    dst = '/tmp/'+case_number+'/'+i
    shutil.copyfile(src, dst) # copy log files from /log to /tmp/ directory

#same for files in logfiles_timestamp_type_2
for i in logfiles_timestamp_type_2:
    partition='/tmp'
    limit = 31744000  # 31744000 bytes equals to 250 MB
    disk_space(partition,limit)  # check /tmp partition making sure /tmp has more than 250MB free space
    src = '/log/'+i
#    dst =  '/tmp/'+i   
#    dst = '/tmp/456/'+i 
    dst = '/tmp/'+case_number+'/'+i
    shutil.copyfile(src, dst) # copy log files from /log to /tmp/ directory

######### check every file in /tmp/case_number.log, locate the first line of start_date and the line of end_date and then copy them to /tmp/case_number.log
for i in logfiles_timestamp_type_0:
    partition='/tmp'
#    partition = '/tmp/'+case_number+'_filtered_by_time_range/'
    limit = 262144000 # 262144000 bytes equals to 250 MB
    disk_space(partition,limit)  #check /tmp partition and make sure /tmp has more than 250MB free space
#    src_file =  '/tmp/'+i
    src_file = '/tmp/'+case_number+'/'+i
#    dst_file = '/tmp/'+i+'_'+str(int(time.time()))
#    dst_file = '/tmp/'+i+'_'+ case_number                  #name of the destination file    <<<<<<<<<
#    dst_file = '/tmp/'+case_number+'/'+i+'_'+ case_number+'_filtered_by_time_range'
    dst_file = '/tmp/'+case_number+'_filtered_by_time_range/'+i+'_'+ case_number+'_filtered_by_time_range'
    first_line = start_line_number(src_file, start_date)
    last_line = end_line_number(src_file, end_date)
    if first_line == None and last_line <= 1: 
        print('Don`t found in the date range ' + start_date + ' to '+ end_date + ' in file ' + src_file)
    else:
        print('Processing '+i)
        print('The first line of ' + start_date + ' is: ', first_line)
        print('The line behind last occurrence of ' + end_date + ' is: ', last_line)
        print('copy lines between ' + str(first_line) + ' and '+ str(last_line) + ' from ' + src_file + ' to ' + dst_file)
        copy_lines(src_file, dst_file, first_line, last_line)

#same for files in logfiles_timestamp_type_1
for i in logfiles_timestamp_type_1:
    partition='/tmp'
#    partition = '/tmp/'+case_number+'_filtered_by_time_range/'
    limit = 262144000 # 262144000 bytes equals to 250 MB
    disk_space(partition,limit)  #check /tmp partition and make sure /tmp has more than 250MB free space
#    src_file =  '/tmp/'+i
    src_file = '/tmp/'+case_number+'/'+i
#    dst_file = '/tmp/'+i+'_'+str(int(time.time()))
#    dst_file = '/tmp/'+i+'_'+ case_number
#    dst_file = '/tmp/'+case_number+'/'+i+'_'+ case_number+'_filtered_by_time_range'
    dst_file = '/tmp/'+case_number+'_filtered_by_time_range/'+i+'_'+ case_number+'_filtered_by_time_range'
    first_line = start_line_number(src_file, converted_start_date_1_string)
    last_line = end_line_number(src_file, converted_end_date_1_string)
    if first_line == None and last_line <= 1: 
        print('Don`t found in the date range ' + converted_start_date_1_string + ' to '+ converted_end_date_1_string + ' in file ' + src_file)
    else:
        print('Processing '+i)
        print('The first line of ' + converted_start_date_1_string + ' is: ', first_line)
        print('The line behind last occurrence of ' + converted_end_date_1_string + ' is: ', last_line)
        print('copy lines between ' + str(first_line) + ' and '+ str(last_line) + ' from ' + src_file + ' to ' + dst_file)
        copy_lines(src_file, dst_file, first_line, last_line)

#same for files in logfiles_timestamp_type_2
for i in logfiles_timestamp_type_2:
    partition='/tmp'
    limit = 262144000 # 262144000 bytes equals to 250 MB
    disk_space(partition,limit)  #check /tmp partition and make sure /tmp has more than 250MB free space
#    src_file =  '/tmp/'+i
    src_file = '/tmp/'+case_number+'/'+i
#    dst_file = '/tmp/'+i+'_'+str(int(time.time()))
#    dst_file = '/tmp/'+i+'_'+ case_number
#    dst_file = '/tmp/'+case_number+'/'+i+'_'+ case_number+'_filtered_by_time_range'
    dst_file = '/tmp/'+case_number+'_filtered_by_time_range/'+i+'_'+ case_number+'_filtered_by_time_range'
    first_line = start_line_number(src_file, converted_start_date_2)
    last_line = end_line_number(src_file, converted_end_date_2)
    if first_line == None and last_line <= 1: 
        print('Don`t found in the date range ' + converted_start_date_2 + ' to '+ converted_end_date_2 + ' in file ' + src_file)
    else:
        print('Processing '+i)
        print('The first line of ' + converted_start_date_2 + ' is: ', first_line)
        print('The line behind last occurrence of ' + converted_end_date_2 + ' is: ', last_line)
        print('copy lines between ' + str(first_line) + ' and '+ str(last_line) + ' from ' + src_file + ' to ' + dst_file)
        copy_lines(src_file, dst_file, first_line, last_line)

######### compress the log bundle of the filtered files #########
subprocess.run (["tar", "-czvf", "logbundle_"+case_number+"_filtered_by_time_range.tar.gz", case_number+"_filtered_by_time_range"])

######### commands to clean the firewall: ######### 
#mount -o remount, rw /
#rm -rf /tmp/ *case_number*
#mount -o remount, ro /





   
    





