import getpass, os, imaplib, email
from OpenSSL.crypto import load_certificate, FILETYPE_PEM
import itertools
from os import listdir
from os.path import isfile, join
import imaplib, getpass, re
from time import sleep
import sys
pattern_uid = re.compile('\d+ \(UID (?P<uid>\d+)\)')

conn = imaplib.IMAP4_SSL('imap.gmail.com')

def disconnect(imap):
    imap.logout()

def parse_uid(data):
    match = pattern_uid.match(data)
    return match.group('uid')

def move_email(email_ids):
    latest_email_id = email_ids[-1] # Assuming that you are moving the latest email.
    resp, data = conn.fetch(latest_email_id, "(UID)")
    print("Found email: ", resp)
    msg_uid = parse_uid(data[0])
    result = conn.uid('COPY', msg_uid, 'stocks')#To be modified so emails are moved correctly
    print(result)
    sleep(2)
    if result[0] == 'OK':
        mov, data = conn.uid('STORE', msg_uid , '+FLAGS', '(\Deleted)')
        conn.expunge()

def get_payload(data):
    global conn
    typ, data = conn.fetch(data[0],'(RFC822)')
    msg = email.message_from_string(data[0][1])
    print msg.get_payload()

def main():
    global conn
    #subject = 'A Friend'
    conn.login('michal.gnat@gmail.com', 'aqjejrhozjeimzzc')

    conn.select('Inbox', readonly = False)
    while True:
        print("Hello")
        try:
            typ, data = conn.search(None,'(Subject "Trade Alert")') #gathers all the emails and presents them in numbers
            if typ == 'OK':
                email_ids = data[0].split()
                get_payload(email_ids)
                #move_email(email_ids)
                sleep(4)
        except KeyboardInterrupt:
            sys.exit(0)
        except:
            sleep(2)
            print("No more emails")
            pass
main()
