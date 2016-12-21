import getpass, os, imaplib, email
from OpenSSL.crypto import load_certificate, FILETYPE_PEM
import itertools
from os import listdir
from os.path import isfile, join

def file_creator(payload): #TO DO: Make a script to change file names to update
    onlyfiles = [f for f in listdir('PWD') if isfile(join('PWD', f))]
    onlyfiles.sort()
    version = 1;
    filename = 'Email_Trade_Alert1.txt'

    while True: 
        for name in onlyfiles:
            if name == filename:
                version += 1

                filename = list(filename)   #changed to list to ease text modifications
                filename[-5]='%d'%version
                filename = "".join(filename)
                
        with open(os.path.join('PWD', filename), 'w') as file1:
            file1.write(payload)
            file1.close()
        break

def main():
    conn = imaplib.IMAP4_SSL('imap.gmail.com')
    subject = 'New Trade Alert'
    conn.login('LOGINNAME@gmail.com', 'PASSWORD')

    conn.select('Inbox')
    typ, data = conn.search(None,'(SUBJECT "%s")' % subject) #gathers all the emails and presents them in numbers
    data1 = data[0].split()
    data2 = []
    for item in data1:
        data2.append(item)
    
    typ, data = conn.fetch(data2[1],'(RFC822)') #Opens the email from the email number provided above

    msg = email.message_from_string(data[0][1])
    print msg.get_payload()

    file_creator(msg.get_payload())

main()
