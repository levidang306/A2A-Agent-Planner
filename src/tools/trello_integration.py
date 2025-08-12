import os
import requests
from typing import Optional

# Load Trello API credentials from environment variables
API_KEY = os.getenv("API_KEY_TRELLO")
API_TOKEN = os.getenv("API_TOKEN_TRELLO")
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
        url = f"{BASE_URL}/boards/"
        params = {
            "name": board_name,
            "key": self.api_key,
            "token": self.api_token
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            board_id = response.json().get("id")
            print(f"Board '{board_name}' created successfully with ID: {board_id}")
            return board_id
        else:
            print(f"Failed to create board: {response.status_code} - {response.text}")
            return None

    def create_card(self, list_id: str, card_name: str, description: str = "") -> Optional[str]:
        """
        Create a new card in a specified list.
        :param list_id: ID of the list where the card will be created
        :param card_name: Name of the card
        :param description: Description of the card
        :return: Card ID if successful, None otherwise
        """
        url = f"{BASE_URL}/cards"
        params = {
            "idList": list_id,
            "name": card_name,
            "desc": description,
            "key": self.api_key,
            "token": self.api_token
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            card_id = response.json().get("id")
            print(f"Card '{card_name}' created successfully with ID: {card_id}")
            return card_id
        else:
            print(f"Failed to create card: {response.status_code} - {response.text}")
            return None

    def get_lists_on_board(self, board_id: str) -> Optional[list]:
        """
        Retrieve all lists on a specified board.
        :param board_id: ID of the board
        :return: List of lists if successful, None otherwise
        """
        url = f"{BASE_URL}/boards/{board_id}/lists"
        params = {
            "key": self.api_key,
            "token": self.api_token
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to retrieve lists: {response.status_code} - {response.text}")
            return None


# Example usage
if __name__ == "__main__":
    trello = TrelloIntegration(api_key=API_KEY, api_token=API_TOKEN)

    # Create a new board
    board_id = trello.create_board("Task Agent Board")

    if board_id:
        # Get lists on the board
        lists = trello.get_lists_on_board(board_id)
        if lists:
            # Assuming the first list is where we want to add cards
            first_list_id = lists[0]["id"]

            # Create a new card in the first list
            trello.create_card(list_id=first_list_id, card_name="Sample Task", description="This is a sample task.")