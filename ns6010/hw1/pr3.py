import requests as req
import json

URL_ROOT = 'http://127.0.0.1:5452'

def get_session(initialfile):
	with open(initialfile) as data_file:
		data = json.load(data_file)
	
	session = req.Session()
	session.auth = ('user','pass')
	login_response = session.post(URL_ROOT,data)
	login_response.raise_for_status()
	return session


def get_info(session):
	response = session.get(URL_ROOT)
	response.raise_for_status()
	return response.text



session = get_session("initialfile.json")
info = get_info(session)
print info


