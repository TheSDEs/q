import os
import time
import sys
import email
import getpass, imaplib
sys.path.append('../')
from mailagent.mail_transport import MailTransport

'''An agent that interacts by SMTP.'''

class Agent():

    def __init__(self, cfg=None, transport=None):
        self.cfg = cfg
        if not transport:
            transport = MailTransport(cfg)
        self.trans = transport
        self.imapSession = imaplib.IMAP4_SSL(self.trans.imap_cfg['server'])
        self.imapUsr = self.trans.imap_cfg['username']
        self.imapPwd = self.trans.imap_cfg['password']


    def process_message(self, msg):
        # sender_key, plaintext = self.decrypt(msg)
        # if plaintext:
        if msg:
            typ = msg.get_type()
            if typ == 'ping':
                self.handle_ping()
            else:
                raise Exception('Unkonwn message type %s' % typ)

    def fetch_message(self):
        # Put some code here that checks our inbox. If we have
        # something, return topmost (oldest) item. If not, return
        # None.
        try:
            typ, accountDetails = self.imapSession.login(self.imapUsr, self.imapPwd)
            if typ != 'OK':
                print
                'Not able to sign in!'
                raise

            # imapSession.select('[Gmail]/All Mail')
            self.imapSession.select('Inbox')
            # type, data = self.imapSession.select('Inbox')
            type, messages = self.imapSession.search(None, '(UNSEEN)')
            # for num in accountDetails[0].split():
            for num in messages[0].split():
                typ, data = self.imapSession.fetch(num, '(RFC822)')
                # typ1, data1 = self.imapSession.store(num, '-FLAGS', '\\Seen')
                # data = data.decode('utf-8')
                msg = email.message_from_string(data[0][1].decode('utf-8'))
                return msg

        except Exception as e:
            print(e)
            'Not able to download all attachments.'

    def run(self):
        while True:
            try:
                msg = self.fetch_message()
                if msg:
                    self.process_message(msg)
                else:
                    time.sleep(1000)
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                traceback.print_exc()

def get_cfg_from_cmdline():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--statefolder" ,default="~/.mailagent", help="folder where state is stored")
    parser.add_argument("-l", "--loglevel", default="WARN", help="min level of messages written to log")
    args = parser.parse_args()
    args.statefolder = os.path.expanduser(args.statefolder)
    return args

def get_config_from_file():
    import configparser
    cfg = configparser.ConfigParser()
    cfg_path = 'mailagent.cfg'
    if os.path.isfile(cfg_path):
        cfg.read(cfg_path)
    return cfg

def configure():
    args = get_cfg_from_cmdline()

    sf = args.statefolder
    if not os.path.exists(sf):
        os.makedirs(sf)
    os.chdir(sf)

    cfg = get_config_from_file()
    return cfg

if __name__ == '__main__':
    cfg = configure()
    agent = Agent(cfg)
    agent.run()
