import requests
from bs4 import BeautifulSoup
import time
import logging
import os
logging.basicConfig(level=logging.INFO, filename='logs.log', filemode='a', format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d-%b-%y %I:%M:%S %p')
logger = logging.getLogger(__name__)

instance_url = os.environ.get('INSTANCE')
access_token = os.environ.get('ACCESS')
memos_url = os.environ.get('MEMOS_URL')
api = os.environ.get('API')

headers = {'Authorization': 'Bearer {}'.format(access_token)}
latest_status_id = ''
account_id = ''

def get_id(): #get account id
    url = '{}/api/v1/accounts/verify_credentials'.format(instance_url)
    r = requests.get(url, headers=headers)
    data = r.json()
    global account_id
    account_id = data.get('id')
    return account_id

def get_status(account_id):
    url = '{}/api/v1/accounts/{}/statuses'.format(instance_url,account_id)
    params = {'exclude_reblogs': True, 'since_id': '{}'.format(latest_status_id)}
    r = requests.get(url, headers=headers, params=params)
    data = r.json()
    return data

def clean_html(content):
    soup = BeautifulSoup(content, 'html.parser')
    clean_content = soup.get_text('\n')
    return clean_content

def check_latest_status_id(id):
    url = '{}/api/v1/accounts/{}/statuses'.format(instance_url,id)
    params = {'limit': 1 }
    r = requests.get(url, headers=headers, params=params)
    data = r.json()
    global latest_status_id
    latest_status_id = data[0].get('id')
    #return latest_status_id

def write_memos(content):
    url = '{}/api/v1/memo'.format(memos_url)
    params = {'openId': api}
    headers = {'Content-Type': 'application/json'}
    json = {'content': content}
    r = send_http_request(url, 'POST', headers=headers, json=json, params=params)
    return r.json().get('id') #return memos id

def create_bind_resource(memo_id, url):
    #setting default headers and parameters
    params = {'openId': api}
    headers = {'Content-Type': 'application/json'}

    # setting memos resource upload parameters
    upload_json = {'externalLink': url, 'downloadToLocal': True} # upload resource from external url, and download to local
    upload_url = '{}/api/v1/resource'.format(memos_url) # api request to upload resource
    resource_id = requests.post(upload_url, headers=headers, json=upload_json, params=params).json().get('id')

    # setting memos resource to post binding
    bind_url = '{}/api/v1/memo/{}/resource'.format(memos_url, memo_id) 
    bind_json = {'resourceId': resource_id}
    bind = requests.post(bind_url, headers=headers, params=params, json=bind_json) #api request to bind resource to post
    return bind.json()

def send_http_request(url, request_type, headers=None, data=None, params=None, json=None):
    if request_type == 'POST':
        r = requests.post(url, data=data, headers=headers, params=params, json=json)
    else:
        r = requests.get(url, headers=headers, data=data, params=params, json=json)
    return r

def check_if_mention(mentions):
    if not bool(mentions):
        #status no mentions
        return False
    else:
        #status have mentions
        return True

logging.info('Bot started')
print('Bot started')

#setting latest status id on initial run
check_latest_status_id(get_id())

while True:
    try:
        #get latest statuses
        statuses = get_status(account_id)

        #loop through each status
        for i in reversed(statuses):
            #check if status have mentions
            if check_if_mention(i.get('mentions')) is False:
                #get the content of the status as there are no mentions
                content = i.get('content') 
                clean_content = clean_html(content) #process it to return text content
                media_attachments = i.get('media_attachments')
                memo_id = write_memos(clean_content)
                print(clean_content)
                logging.info(clean_content)
                if media_attachments:
                    for media in media_attachments:
                        image_url = media.get('url')
                        create_bind_resource(memo_id, image_url)
                        print('Image uploaded')
                    logging.info('Image(s) uploaded')
                    print('Image(s) uploaded')
                latest_status_id = i.get('id') #set latest status id to current id
            else:
                print('Skipping mentions status - {}'.format(i.get('content')))
                logging.info('Skipping mentions status - {}'.format(i.get('content'))) 
        time.sleep(10)
    except requests.exceptions.SSLError:
        logging.error('SSL exception error')
        time.sleep(120)
        True
    except KeyboardInterrupt:
        print('Exit script due to keyboard interrupt')
        break
    except Exception as exception:
        logging.error('General exception error: {}'.format(exception))
        time.sleep(120)
        True