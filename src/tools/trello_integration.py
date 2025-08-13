import os
import requests
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('trello_integration.log')
    ]
)
logger = logging.getLogger(__name__)

# Load Trello API credentials from environment variables
API_KEY = os.getenv("API_KEY_TRELLO", "2be5067376c60f0f953e5057468f51e2")
API_TOKEN = os.getenv("API_TOKEN_TRELLO","6e2e7f6ff3469f5ba717e7396017d6962114064e80af3ecbdf5a022440bfcc7e")
BASE_URL = "https://api.trello.com/1"

class TrelloIntegration:
    def __init__(self, api_key: str, api_token: str):
        self.api_key = api_key
        self.api_token = api_token

    def create_board(self, board_name: str) -> Optional[str]:
        """
        Create a new Trello board.
        :param board_name: Name of the board to create
        :return: Board ID if successful, None otherwise
        """
        logger.info(f"Starting board creation - Board name: '{board_name}'")
        print(f"[TRELLO] Starting board creation - Board name: '{board_name}'")
        
        if not self.api_key or not self.api_token:
            error_msg = "Trello API credentials not provided in TrelloIntegration constructor"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None
        
        url = f"{BASE_URL}/boards/"
        params = {
            "name": board_name,
            "key": self.api_key,
            "token": self.api_token
        }
        
        try:
            logger.info(f"Making API request to create board: {url}")
            print(f"[TRELLO] Making API request to create board...")
            
            response = requests.post(url, params=params)
            
            logger.info(f"API response status: {response.status_code}")
            print(f"[TRELLO] API response status: {response.status_code}")
            
            if response.status_code == 200:
                board_data = response.json()
                board_id = board_data.get("id")
                board_url = board_data.get("url", "URL not available")
                
                success_msg = f"Board '{board_name}' created successfully! ID: {board_id}, URL: {board_url}"
                logger.info(success_msg)
                print(f"[TRELLO SUCCESS] {success_msg}")
                
                return board_id
            else:
                error_msg = f"Failed to create board: {response.status_code} - {response.text}"
                logger.error(error_msg)
                print(f"[TRELLO ERROR] {error_msg}")
                return None
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while creating board: {str(e)}"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Unexpected error while creating board: {str(e)}"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None

    def create_card(self, list_id: str, card_name: str, description: str = "") -> Optional[str]:
        """
        Create a new card in a specified list.
        :param list_id: ID of the list where the card will be created
        :param card_name: Name of the card
        :param description: Description of the card
        :return: Card ID if successful, None otherwise
        """
        logger.info(f"Starting card creation - Card name: '{card_name}', List ID: {list_id}")
        print(f"[TRELLO] Starting card creation - Card name: '{card_name}', List ID: {list_id}")
        
        if description:
            logger.info(f"Card description: {description[:100]}{'...' if len(description) > 100 else ''}")
            print(f"[TRELLO] Card description: {description[:100]}{'...' if len(description) > 100 else ''}")
        
        if not self.api_key or not self.api_token:
            error_msg = "Trello API credentials not provided in TrelloIntegration constructor"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None
        
        url = f"{BASE_URL}/cards"
        params = {
            "idList": list_id,
            "name": card_name,
            "desc": description,
            "key": self.api_key,
            "token": self.api_token
        }
        
        try:
            logger.info(f"Making API request to create card: {url}")
            print(f"[TRELLO] Making API request to create card...")
            
            response = requests.post(url, params=params)
            
            logger.info(f"API response status: {response.status_code}")
            print(f"[TRELLO] API response status: {response.status_code}")
            
            if response.status_code == 200:
                card_data = response.json()
                card_id = card_data.get("id")
                card_url = card_data.get("url", "URL not available")
                
                success_msg = f"Card '{card_name}' created successfully! ID: {card_id}, URL: {card_url}"
                logger.info(success_msg)
                print(f"[TRELLO SUCCESS] {success_msg}")
                
                return card_id
            else:
                error_msg = f"Failed to create card: {response.status_code} - {response.text}"
                logger.error(error_msg)
                print(f"[TRELLO ERROR] {error_msg}")
                return None
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while creating card: {str(e)}"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Unexpected error while creating card: {str(e)}"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None

    def create_list(self, board_id: str, list_name: str) -> Optional[str]:
        """
        Create a new list on a specified board.
        :param board_id: ID of the board to create the list on
        :param list_name: Name of the list to create
        :return: List ID if successful, None otherwise
        """
        logger.info(f"Creating list '{list_name}' on board {board_id}")
        print(f"[TRELLO] Creating list '{list_name}' on board {board_id}")
        
        if not self.api_key or not self.api_token:
            error_msg = "Trello API credentials not provided in TrelloIntegration constructor"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None
        
        # Remove emojis from list name to prevent Unicode encoding errors
        clean_list_name = ''.join(char for char in list_name if ord(char) < 128)
        if clean_list_name != list_name:
            logger.info(f"Cleaned list name from '{list_name}' to '{clean_list_name}' to prevent Unicode errors")
            print(f"[TRELLO] Cleaned list name from '{list_name}' to '{clean_list_name}' to prevent Unicode errors")
        
        url = f"{BASE_URL}/lists"
        data = {
            "name": clean_list_name,
            "idBoard": board_id,
            "key": self.api_key,
            "token": self.api_token
        }
        
        try:
            logger.info(f"Making API request to create list: {url}")
            print(f"[TRELLO] Making API request to create list...")
            
            response = requests.post(url, data=data)
            
            logger.info(f"API response status: {response.status_code}")
            print(f"[TRELLO] API response status: {response.status_code}")
            
            if response.status_code == 200:
                list_data = response.json()
                list_id = list_data.get("id")
                
                success_msg = f"List '{clean_list_name}' created successfully with ID: {list_id}"
                logger.info(success_msg)
                print(f"[TRELLO SUCCESS] {success_msg}")
                
                return list_id
            else:
                error_msg = f"Failed to create list: {response.status_code} - {response.text}"
                logger.error(error_msg)
                print(f"[TRELLO ERROR] {error_msg}")
                return None
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while creating list: {str(e)}"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Unexpected error while creating list: {str(e)}"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None

    def get_lists_on_board(self, board_id: str) -> Optional[list]:
        """
        Retrieve all lists on a specified board.
        :param board_id: ID of the board
        :return: List of lists if successful, None otherwise
        """
        logger.info(f"Retrieving lists for board ID: {board_id}")
        print(f"[TRELLO] Retrieving lists for board ID: {board_id}")
        
        if not self.api_key or not self.api_token:
            error_msg = "Trello API credentials not provided in TrelloIntegration constructor"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None
        
        url = f"{BASE_URL}/boards/{board_id}/lists"
        params = {
            "key": self.api_key,
            "token": self.api_token
        }
        
        try:
            logger.info(f"Making API request to get board lists: {url}")
            print(f"[TRELLO] Making API request to get board lists...")
            
            response = requests.get(url, params=params)
            
            logger.info(f"API response status: {response.status_code}")
            print(f"[TRELLO] API response status: {response.status_code}")
            
            if response.status_code == 200:
                lists_data = response.json()
                list_count = len(lists_data)
                
                success_msg = f"Retrieved {list_count} lists from board {board_id}"
                logger.info(success_msg)
                print(f"[TRELLO SUCCESS] {success_msg}")
                
                # Log list names for debugging
                for i, list_item in enumerate(lists_data):
                    list_name = list_item.get('name', 'Unknown')
                    list_id = list_item.get('id', 'Unknown')
                    logger.debug(f"List {i+1}: '{list_name}' (ID: {list_id})")
                    print(f"[TRELLO] List {i+1}: '{list_name}' (ID: {list_id})")
                
                return lists_data
            else:
                error_msg = f"Failed to retrieve lists: {response.status_code} - {response.text}"
                logger.error(error_msg)
                print(f"[TRELLO ERROR] {error_msg}")
                return None
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while retrieving lists: {str(e)}"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None
        except Exception as e:
            error_msg = f"Unexpected error while retrieving lists: {str(e)}"
            logger.error(error_msg)
            print(f"[TRELLO ERROR] {error_msg}")
            return None


# Example usage
if __name__ == "__main__":
    logger.info("Starting Trello Integration example")
    print("[TRELLO EXAMPLE] Starting Trello Integration example")
    
    if not API_KEY or not API_TOKEN:
        error_msg = "API_KEY_TRELLO and API_TOKEN_TRELLO environment variables must be set"
        logger.error(error_msg)
        print(f"[TRELLO ERROR] {error_msg}")
        exit(1)
    
    trello = TrelloIntegration(api_key=API_KEY, api_token=API_TOKEN)
    logger.info("TrelloIntegration instance created")
    print("[TRELLO EXAMPLE] TrelloIntegration instance created")

    # Create a new board
    logger.info("Creating test board...")
    print("[TRELLO EXAMPLE] Creating test board...")
    board_id = trello.create_board("Task Agent Board")

    if board_id:
        logger.info(f"Board created successfully, proceeding to get lists...")
        print("[TRELLO EXAMPLE] Board created successfully, proceeding to get lists...")
        
        # Get lists on the board
        lists = trello.get_lists_on_board(board_id)
        if lists:
            # Assuming the first list is where we want to add cards
            first_list_id = lists[0]["id"]
            first_list_name = lists[0]["name"]
            
            logger.info(f"Using first list '{first_list_name}' (ID: {first_list_id}) for card creation")
            print(f"[TRELLO EXAMPLE] Using first list '{first_list_name}' (ID: {first_list_id}) for card creation")

            # Create a new card in the first list
            card_id = trello.create_card(
                list_id=first_list_id, 
                card_name="Sample Task", 
                description="This is a sample task created by the Trello integration example."
            )
            
            if card_id:
                logger.info("Example completed successfully!")
                print("[TRELLO EXAMPLE] Example completed successfully!")
            else:
                logger.error("Failed to create sample card")
                print("[TRELLO ERROR] Failed to create sample card")
        else:
            logger.error("Failed to retrieve board lists")
            print("[TRELLO ERROR] Failed to retrieve board lists")
    else:
        logger.error("Failed to create board")
        print("[TRELLO ERROR] Failed to create board")