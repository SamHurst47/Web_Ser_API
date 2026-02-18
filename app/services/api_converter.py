from urllib.error import HTTPError, URLError
from typing import Optional, Dict
import json
from urllib.request import urlopen

def get_openf1_session_keys(
    year: int, 
    country_name: str, 
    session_name: str
) -> Optional[Dict[str, int]]:
    """
    Fetch session_key and meeting_key from OpenF1 API.
    Returns None if no session found or API error.
    """
    try:
        url = f"https://api.openf1.org/v1/sessions?year={year}&country_name={country_name}&session_name={session_name.replace(' ', '%20')}"
        response = urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
        
        if not data:  # Empty list → no session
            print(f"No session found for year={year}, country={country_name}, session={session_name}")
            return None
            
        session = data[0]  # Take first match
        return {
            "session_key": session["session_key"],
            "meeting_key": session.get("meeting_key")  # Optional field
        }
        
    except (HTTPError, URLError) as e:
        print(f"OpenF1 API error: {e}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"Invalid API response: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
