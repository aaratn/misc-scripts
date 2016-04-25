#!/usr/bin/python
import sys
try:
    from smb.SMBConnection import SMBConnection
except:
    print "You must install pysmb module in order to run this script"
import os
import socket
import argparse

# Create parser instance to accept arguements from user
parser = argparse.ArgumentParser(
    description="This script copies file from windows share to local system")
requiredNamed = parser.add_argument_group("Required")
requiredNamed.add_argument('-s', '--src', dest='spath',
                           help='Source Path', required=True)
requiredNamed.add_argument('-d', '--dest', dest='dpath',
                           help="Destination Path", required=True)
requiredNamed.add_argument('-u', '--user', dest='suser',
                           help='User Name to use to connect to Windows Machine', required=True)
requiredNamed.add_argument('-p', '--pass', dest='spass',
                           help="Password for your User Name", required=True)
parser.add_argument('--domain', dest='sdom',
                    help="Domain Name - If Using Active Directory", required=False)

# Print Help Message if no arguements specified
if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)


args = parser.parse_args()

# Save Args to Variable
fullpath = args.spath.encode('string-escape')

destpath = args.dpath
userID = args.suser
password = args.spass
dn = args.sdom

# Extract Server Name from the Given Source Path

server_name = fullpath.split('\\')[2]

# Extract Network Share Name from the Given Source Path

netshare = fullpath.split(r'\\')[2]

# Create File Name from the rest of the path

fn = fullpath.split(r'\\')[3:]
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

# Copy File from Source Server to Local FileSystem

try:
    with open(destpath, 'wb') as file_obj:
        conn.retrieveFile(netshare, str(fn), file_obj)
        conn.close()
except Exception as e:
    print e[0]
    print "Hint: Check FileName or Path Name"

# Delete the Local File if the copy was unsucessful

if os.stat(destpath).st_size == 0:
    os.remove(destpath)
