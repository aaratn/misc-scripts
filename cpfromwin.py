#!/usr/bin/python
# Created by Aarat Nathwani - 27th April 2016
import sys
try:
    from smb.SMBConnection import SMBConnection
except:
    print "Error : You must install pysmb module in order to run this script"
    sys.exit(1)
import os
import socket
import argparse
import csv

# Create parser instance to accept arguements from user
parser = argparse.ArgumentParser(
    description="This script copies file from windows share to local system")
requiredNamed = parser.add_argument_group("Required")
requiredNamed.add_argument('-u', '--user', dest='suser',
                           help='User Name to use to connect to Windows Machine', required=True)
requiredNamed.add_argument('-p', '--pass', dest='spass',
                           help="Password for your User Name", required=True)
requiredNamed.add_argument('-c', '--csv', dest='csvfile',
                           help="CSV File", required=True)
parser.add_argument('--domain', dest='sdom',
                    help="Domain Name - If Using Active Directory", required=False)

# Print Help Message if no arguements specified
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()


def wincopy(spath, dpath, usr, paswd, dom):
    # Save Args to Variable
    fullpath = spath.encode('string-escape')
    destpath = dpath.lstrip(' ')
    userID = usr
    password = paswd
    dn = dom
    # Extract Server Name from the Given Source Path

    server_name = fullpath.split(r'\\')[2]

    # Extract Network Share Name from the Given Source Path

    netshare = fullpath.split(r'\\')[3]

    # Create File Name from the rest of the path

    fn = fullpath.split(r'\\')[4:]
    fn = '/' + '/'.join(fn)

    # Get The HostName of the Machine on which this script is running

    client_machine_name = socket.gethostname()

    # Get The IP of the Source Server
    try:
        server_ip = socket.gethostbyname(server_name)
    except Exception as e:
        print e
        sys.exit(1)

    # Create Connection for SMB

    if dn:
        conn = SMBConnection(userID, password, client_machine_name,
                             server_name, domain=dn, use_ntlm_v2=True)
    else:
        conn = SMBConnection(userID, password, client_machine_name,
                             server_name, use_ntlm_v2=True)

    try:
        conn.connect(server_ip, 139)
    except Exception as e:
        print e
        sys.exit(1)

    # Copy File from Source Server to Local FileSystem

    try:
        if not os.path.exists(os.path.dirname(destpath)):
            try:
                os.makedirs(os.path.dirname(destpath))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
        with open(destpath, 'wb') as file_obj:
            conn.retrieveFile(netshare, str(fn), file_obj)
            conn.close()
    except Exception as e:
        print e
        print "Hint: Check FileName, Path Name, or the account has permission to access the file"

    # Delete the Local File if the copy was unsucessful
    if os.stat(destpath).st_size == 0:
        os.remove(destpath)

try:
    csvfile = file(args.csvfile)
except Exception as e:
    print e
    sys.exit(1)
username = args.suser
password = args.spass
domain = args.sdom
reader = csv.reader(csvfile, delimiter=',', quotechar='"')
next(reader)
for row in reader:
    sourcefile = row[0]
    destfile = row[1]
    wincopy(sourcefile, destfile, username, password, domain)
