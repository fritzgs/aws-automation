#!/usr/bin/python3

"""A tiny Python program to check that nginx is running.
Try running this program from the command line like this:
  python3 check_webserver.py
"""

import sys
import subprocess

def checknginx():
    checkCommand = 'ps -A | grep nginx | grep -v grep'

    (status, output) = subprocess.getstatusoutput(checkCommand)

    if status > 0:  
        print("Nginx Server IS NOT running")
        startCommand = 'sudo service nginx start'
        (status, output) = subprocess.getstatusoutput(startCommand)
        if status:
            print ("Error starting nginx!")
            sys.exit(2)
        print ("Nginx started successfully")
        sys.exit(0)

    else:
        print("Nginx server IS running")

# Define a main() function.
def main():
    checknginx()
      
# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
  main()

