from urllib.request import urlopen
import json

def get_openf1_session_keys(year, country_name, session_name):
    url = f'https://api.openf1.org/v1/sessions?year={year}&country_name={country_name}&session_name={session_name.replace(" ", "%20")}'
    response = urlopen(url)
    data = json.loads(response.read().decode('utf-8'))
    
    return {
        "session_key": data[0]["session_key"]  
    }

