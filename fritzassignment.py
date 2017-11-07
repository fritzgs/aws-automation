'''
Fritz Gerald Santos - 20071968 Computer Forensics and Security Year 3 - WIT.

Assignment for DevOps/Network Management (31 October 2017)

'''

import boto3
import sys
import subprocess

instance_id = []
ec2 = boto3.resource('ec2')
s3 = boto3.resource('s3')

'''
This fucntion is the firs to run when the script is executed.
What this function does:

	1) Creates an instance
	2) Creates a bucket
	3) Copyies a file from the directory that this script is in to the bucket
	4) Copies a html file from the directory and adds it to a created directory tree in the linux instance.
		It then changes the default page of the Nginx web page to the html page.

'''
def initialise():
	
	print ("Running...")

	instance = ec2.create_instances(
		ImageId='ami-acd005d5',
		KeyName='fritzkey', 
		MinCount=1, 
		MaxCount=1, 
		InstanceType='t2.micro',
		SecurityGroupIds=['sg-e36f7a9b'], 
    	UserData='''#!/bin/bash 
                yum -y install nginx
                service nginx start
                chkconfig nginx on''')

	initInstance = instance[0]

	initInstance.wait_until_running()
	initInstance.load()

	print ("Instance Created")

	dnsname = initInstance.public_dns_name

	
	''''
	------
	S3 - Creates S3 bucket if it doesn't already exists.
	------
	'''
	if(s3.Bucket('fritz-bucket-for-assignment') in s3.buckets.all() == True):
		print ('Bucket Already Exists')
	else:
		bucket = s3.create_bucket(Bucket = 'fritz-bucket-for-assignment', CreateBucketConfiguration = {'LocationConstraint' : 'eu-west-1'})
		print ('Bucket Created')


	#Add image to bucket
	addFile = "aws s3 cp fritzassignment.png s3://fritz-bucket-for-assignment --acl public-read"
	(status, output) = subprocess.getstatusoutput(addFile)


	#Copy to instance
	copyScript = 'scp -i fritzkey.pem check_webserver.py ec2-user@%s:.' % (dnsname) 
	(status, output) = subprocess.getstatusoutput(copyScript)


	print ('Configuring Web Server...')

	'''
	This SSH into the instance and executes the command.
	The command contains:

	1) Checks Nginx server using the copied python script: check_webserver.py
	2) Starting the Nginx server
	'''
	checkServer = "ssh -t -i fritzkey.pem ec2-user@" + str(dnsname) + "'sudo chmod 700 check_webserver.py; python3 check_webserver.py; service nginx start'"
	(status, output) = subprocess.getstatusoutput(checkServer)

	#Creates the directories to add the html page in.
	makeDir = "ssh -t -i fritzkey.pem ec2-user@%s 'mkdir www; chmod -R 755 www; cd www; mkdir website; cd website'" % (dnsname) 
	(status, output) = subprocess.getstatusoutput(makeDir)

	#Copy the HTML page to the website directory created in the previous code.
	addPage = "scp -i fritzkey.pem index.html ec2-user@%s:/home/ec2-user/www/website ~/" % (dnsname)
	(status, output) = subprocess.getstatusoutput(addPage)

	''''
	- Configuring the default page of Nginx to be the index.html page
	- Changing the servername to the DNS of the ec2 instance.
	'''
	configure = "ssh -t -o StrictHostKeyChecking=yes -i fritzkey.pem ec2-user@" + str(dnsname) + """'cd /etc/nginx/sites-available; cp default website; echo 'server {
        listen 80;
        listen [::]:80;
        root /home/ec2-user/www/website;
        index index.html index.html;
 
        # Make site accessible from http://localhost/
        server_name *.""" + str(dnsname) + """;
 	
        location / {
 
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                try_files $uri $uri/ =404;
                # Uncomment to enable naxsi on this location
                # include /etc/nginx/naxsi.rules
        }
}' > mysite; cd ..; cd sites-enabled; ln -s /etc/nginx/sites-available/website mysite; service nginx restart' """
	(status, output) = subprocess.getstatusoutput(configure)


	print ("Completed")

	checkFiles = "ssh -i fritzkey.pem ec2-user@%s 'ls' " % (dnsname)
	(status, output) = subprocess.getstatusoutput(checkFiles)


#END OF INITIALISE FUCTION.


#Add all the instance ids to an array - used in other functions
for instId in ec2.instances.all():
	 	instance_id.append(instId.id)


#Terminate an Instance using its ID.
def terminate():
	listInstances()

	selectedId = str(input("Select an instance from the list to terminate (Type 'i-back' to go back to menu): "))
	
	#Check instance_id array if they contain "selected".
	if any(selectedId in s for s in instance_id):
		instance = ec2.Instance(selectedId)
		print (instance.terminate())
		print (instance.state)		

	#To exit out of this function
	elif selectedIs == 'i-back':
		menu()

	#If they don't then it prints this and runs the function again for retry.
	else:
		print ('Invalid instance ID... try again')
		terminate()

#END OF TERMINATEFUCTION.

#Print all instances on my EC2 - prints id, state
def listInstances():
	for instance in ec2.instances.all():
		print(instance.id, instance.state)



#List all the items in all buckets (there is only one bucket)
def listItemsInBucket():
	for bucket in s3.buckets.all():
		print (bucket.name)
		print ("---")
		for item in bucket.objects.all():
			print ("\t%s" % item.key)


'''
Add any file to a bucket - * must specify the path *
'''
def addToBucket():
	fileInput = input (str("Enter path of file (Type 'back' to go back to menu: "))
	if(fileInput == 'back'):
		menu()
	else:
		addFile = "aws s3 cp" + str(file) + "s3://fritz-bucket-for-assignment --acl public-read"
		(status, output) = subprocess.getstatusoutput(addFile)
		listItemsInBucket()


'''
This lets the user run a command on the instance.
It asks for: 
	- the ID of the instance the user wants to use.
	- the command the user wants to execute
	- if that command requires a yes or no input when executed.
'''
def useInstance():
	instId = str(input('Enter the ID of the Instance you want to use to (Type "i-back" to go return to menu): '))

	if instId == "i-back":
		menu()

	command = str(input('Enter the Linux Commmand you wish to perform (Type "i-back" to go return to menu): '))
	
	if instId == "i-back":
		menu()

	yesNo = str(input("Does this command require a 'Yes' or 'No' input?: "))

	hostkey = ""

	if(yesNo == "yes"):
		hostkey = "StrictHostKeyChecking=yes"
	elif (yesNo =="no"):
		hostkey = "StrictHostKeyChecking=no"
	else:
		print ("Invalid input! try again")
		useInstance();

	if any(instId in s for s in instance_id):
		execute = "ssh -t -o %s -i fritzkey.pem ec2-user@%s '%s' " % (hostkey, instId, command)
		(status, output) = subprocess.getstatusoutput(execute)
	else:
		print("Invalid Instance ID... try again")
		useInstance()

#END OF USE INSTANCE FUCTION.


def createInstance():
	instance = ec2.create_instances(
		ImageId='ami-acd005d5',
		KeyName='fritzkey', 
		MinCount=1, 
		MaxCount=1, 
		InstanceType='t2.micro',
		SecurityGroupIds=['sg-e36f7a9b'], 
    	UserData='''#!/bin/bash 
                yum -y install nginx
                service nginx start
                chkconfig nginx on''')

#Simple menu for UI.
def menu():
	ans = True
	while ans:
		print ("""
			1. Create Instance
			2. Use Instance
			3. List all Instances
			4. Terminate an Instance
			5. List Items in Bucket
			6. Add Item to Bucket
			7. Exit Program.
			""")

		ans = int(input("Pick: "))


		if ans == 1:
			createInstance()
			print("\n")
			menu()

		elif ans == 2:
			useInstance()
			print ("\n")
			menu()

		elif ans == 3:
			listInstances()
			print ("\n")
			menu()


		elif ans == 4:
			terminate()
			print ("\n")
			menu()


		elif ans == 5:
			listItemsInBucket()
			print ("\n")
			menu()

		elif ans == 6:
			addToBucket()
			print ("\n")
			menu()

		elif ans == 7:
			print ('Exiting...')
			sys.exit(0)

		else:
			print ("\n Invalid Integer Input")
			menu()


def main():
	initialise()
	menu()

if __name__ == '__main__':
	main()
