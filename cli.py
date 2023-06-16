import logging
#logging.basicConfig(level=10)
import json
from requests_oauthlib import OAuth1Session
import time

with open('config.json') as config_file:
	config = json.load(config_file)

oauth_base_url = 'https://secure.smugmug.com'
request_token_url = oauth_base_url + '/services/oauth/1.0a/getRequestToken'
authorization_url = oauth_base_url + '/services/oauth/1.0a/authorize'
access_token_url = oauth_base_url + '/services/oauth/1.0a/getAccessToken'
callback_uri = 'oob'

api_base_url = 'https://api.smugmug.com'
current_user_profile = api_base_url + '/api/v2!authuser'

def existing_user_signin(user):
	if not (config.get(user) is None):
		user_ak = config[user]['access_token']
		user_sk = config[user]['access_secret']
		return user_ak, user_sk
	else:
		return False
	
user_at, user_st = existing_user_signin('conorpower')

user_session = OAuth1Session(config['oauth_access_token'],
			     client_secret=config['oauth_access_secret'],
			     resource_owner_key=user_at,
			     resource_owner_secret=user_st
				 )

def get_url(url):
	r_headers = {'Accept': 'application/json'}
	r = user_session.get(url, headers=r_headers)
	return r.json()

def post_url(url):
	r_headers = {'Accept': 'application/json'}
	r = user_session.post(url, headers=r_headers)
	return r.json()

#https://stackoverflow.com/a/16696317
def download_file(url, filename):
    # NOTE the stream=True parameter below
    with user_session.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return filename



albumlist = get_url('https://api.smugmug.com/api/v2/user/conorpower!albums?start=1&count=50')


for album in albumlist['Response']['Album']:
	#print(album['NiceName'])
	uri = api_base_url + album['Uris']['AlbumDownload']['Uri']
	#print(post_url(uri))

	
	uri_download_response = get_url(uri)
	download_url_list = uri_download_response['Response']['Download']
	for album_download in download_url_list:
		filename = album['NiceName'] + str(album_download['Part']) + '.zip'
		print(download_file(album_download['WebUri'], filename))


#print(albumlist['Response']['Pages'])


"""
Code to get oauth token
smugmug_session = OAuth1Session(config['oauth_access_token'],client_secret=config['oauth_access_secret'], callback_uri=callback_uri)

smugmug_session.fetch_request_token(request_token_url)
client_auth_url = smugmug_session.authorization_url(authorization_url)
print(client_auth_url)

# This doesn't work as you'd think since you need to append the access code into the overall URL string

redirect_response = input("Paste access code here\n")
print(redirect_response)
smugmug_session.parse_authorization_response(redirect_response)

smugmug_session.fetch_access_token(access_token_url)

print(smugmug_session)

r = smugmug_session.get(current_user_profile)
print(r.content)
"""
