"""Script that will collect basic info from the xg"""
print("This script will help you collecting logs from the xg")
print("Hit enter if you do not know the answer.")
print("Generated files are located in C:\sophos-tmp\<case number>")
print("Install the following pyton module to let it work: pip install ftplib getpass4 paramiko paramiko-expect getenv")

import sys
import paramiko
import time
import re
import os
import ftplib       #to import the files into sophos ftp server
import fileinput
import paramiko_expect
import getenv
import pysftp
from paramiko_expect import SSHClientInteraction
from getpass4 import getpass
from datetime import datetime

#test sophos ftp credentials 5003Z00001OW8bTQAT:b191022ec8
#test firewall access id = 4bd1bed7-ae50-353b-a7b0-8456a8420a90@eu2.apu.sophos.com

case_number = input("Enter the case number: ")

#data to interact with sophos ftp server
ftp_user = input("Enter the FTP username: ")
ftp_password = input("Enter the FTP password: ")
ftp_host = ("ftp.sophos.com")
ftp_port = 990

#data to ssh into the firewall
host = "eu2.apu.sophos.com"
port = 2222
username = input("Enter yourname.yourlastname,access id without @eu2.apu.sophos.com: ")
password = getpass("Enter your green password: ")

prompt = (".*_SFOS.*")

path = 'C:\sophos-tmp'
joined_path = os.path.join(path,case_number)

#check whether the specified path exists and if not create a new one
isExist = os.path.exists(joined_path)
if not isExist:
  os.makedirs(joined_path)
  print("Created directory "+joined_path)

#create and open a file  in write mode a file into the folder with the same name of the case id user enter before
external_file = open("C:/sophos-tmp/"+case_number+"/log_case_number_"+case_number+"_on_"+datetime.today().strftime('%Y%m%d')+".txt", "w")

#used for the absolute file path so we can later use it in ftplib with """with open(external_filepath_read, "rb") as file:"""
external_filepath_read = "C:/sophos-tmp/"+case_number+"/log_case_number_"+case_number+"_on_"+datetime.today().strftime('%Y%m%d')+".txt"
#external path of the case folder not used at the moment anywhere
external_path = "C:/sophos-tmp/"+case_number+"/"
#external filename so we can use the direct filename """log_case_number_123123123_on_20220616.txt""" in ftplib instead of the absolute path as that causes issues with the FTP itself
external_filename = "log_case_number_"+case_number+"_on_"+datetime.today().strftime('%Y%m%d')+".txt"

#Debug logs for paramiko / SSH connection issues are logged here
paramiko.util.log_to_file(external_path+"paramiko.log")

#ssh into the firewall 
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.connect(host, port, username, password)
print("success login")

#Creates logger so we can save the CLI output
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(external_path+"CLI.log", "a")
   
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
            #This flush method is needed for python 3 compatibility.
            #This handles the flush command by doing nothing.
            #You might want to specify some extra behavior here.
            pass    
sys.stdout = Logger()
    
#Creates the interact session
interact = SSHClientInteraction(ssh_client, timeout=999, display=True)
#Creates the SFTP session on our existing ssh connection so we can upload / download files from SFOS
sftp = ssh_client.open_sftp()

#commands to run into the ssh session
#interact = ssh_client.invoke_shell()

interact.send("5")              #press 5 to select device management when the firewall will promtp the first menu
time.sleep(1)                   #to  wait 1 sec for the firewall beign able to load the second prompt

interact.send("3")              #press 3 to select advanced shell when the firewall will prompt for the second menu
interact.expect(prompt)
time.sleep(2)   

interact.send("tar -czvf /tmp/tomcat.tar.gz /log/tomcat.log")
interact.expect(prompt)
time.sleep(20) 

interact.send("nvram get '#li.serial'")            #to retrieve the serial number of the firewall
interact.expect(prompt)
time.sleep(2) 
#cmd_output_nvram = interact.current_output_clean
#time.sleep(2)

interact.send("df -kh")           #to check disk space
interact.expect(prompt)
time.sleep(2)

interact.send("cish -c system diagnostics show version-info")              #to have main infos like firmware version
interact.expect(prompt)
time.sleep(5)
#cmd_output_cish = interact.current_output_clean

#interact.send("""opcode ctr -ds nosync -t json -b '{"problemdesc":"debugging purpose","logs":"1","systemsnap":"0"}'""")    #to generate a crt file
#interact.expect(prompt, timeout=None)
#cmd_output_ctr = interact.current_output_clean
#interact.send("ls -lahs /sdisk/ctrfinal/")           #to check if the ctr file has been generated
#interact.expect(prompt)

interact.send("ifconfig")                    #to have a list of configured interfaces
interact.expect(prompt)
time.sleep(3)

interact.send("cish -c system ha show details")
interact.expect(prompt)
time.sleep(15)

#interact.send("cd /log/")
#interact.expect(prompt)
#time.sleep(2)

#output = conn.recv(65535)
#print(output.decode())
#print(re.compile(r'\x1b[^m]*m').sub('', output.decode()))
        
#download file from xg to my pc
#command syntax is:     sftp.get('directory/file.csv', '/local/path/file.csv')
#sftp.get('/tmp/hello.txt', external_path+'hello.txt')
#sftp.get('tmp/tomcat.tar.gz', external_path+'tomcat.tar.gz')
#sftp.get('tmp/tomcat.log', external_path+'tomcat.log')
sftp.get('/tmp/sample_file.txt', external_path+"sample_file.txt")
sftp.get('/tmp/tomcat.tar.gz', external_path+"tomcat.tar.gz")


#files_list = sftp.listdir("/sdisk/ctrfinal/")
#for filename in files_list:
#    if re.match(".*CTR.*", filename):
#        sftp.get("/sdisk/ctrfinal/"+filename, external_path+filename)
ssh_client.close                 #Close ssh session as we wouldn't need it anymore

#upload files from laptop to our FTP server
ftp = ftplib.FTP_TLS()
ftp.connect(ftp_host, ftp_port)
ftp.login(ftp_user, ftp_password)


ftp.encoding = "utf-8"                                            #to force UTF-8 encoding
with open(external_filepath_read, "rb") as file:
    ftp.storbinary(f"STOR {external_filename}", file)             #FTP's STOR command to upload the file
    ftp.dir()                                                     #to get list of files
    ftp.quit()                                                    #to quit and close the connection

#filename_2 = external_path+"CLI.log"
#with open(filename_2, "rb") as file:
#    ftp.storbinary(f"STOR {filename_2}", file)             #FTP's STOR command to upload the file
#    ftp.dir()                                                     #to get list of files
#    ftp.quit()                                                    #to quit and close the connection