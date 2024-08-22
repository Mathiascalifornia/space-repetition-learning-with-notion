import os 
from typing import Any

import requests 
import dotenv

class NotionAPIConnector:
    
    
    def __init__(self, 
                 api_key_name:str="api_workspace",
                 database_id_name:str="database_id"
                 ): 
        
        self.api_key_name = api_key_name
        self.database_id_name = database_id_name
        
    def main(self) -> dict:
        """ 
        Return the raw json response
        """
        api_key:str = NotionAPIConnector.load_env_key(key_to_load="api_workspace")
        database_id:str = NotionAPIConnector.load_env_key(key_to_load="database_id")
        headers = NotionAPIConnector.get_headers(notion_api_key=api_key)
        
        return NotionAPIConnector.get_raw_json_response_from_db_id_notion(headers=headers, database_id=database_id)
    
    @staticmethod
    def get_headers(notion_api_key:str,
                    notion_version:str="2022-06-28") -> dict:
        return {
            "Authorization": f"Bearer {notion_api_key}",
            "Content-Type": "application/json",
            "Notion-Version": notion_version
            }

    @staticmethod
    def load_env_key(key_to_load:str) -> Any:
        dotenv.load_dotenv()
        return os.getenv(key_to_load)


    @staticmethod
    def get_raw_json_response_from_db_id_notion(headers:dict,
                                                database_id:str) -> dict:
        
        
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        response = requests.post(url, headers=headers)
        status_code = response.status_code
        
        assert status_code == 200 , f"Bad response ; {status_code}\nresponse : {response.text}"
        
        return response.json()
    