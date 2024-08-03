import time
import os
import json
import re
import pandas as pd
from tkinter import filedialog
from itertools import combinations
import matplotlib.pyplot as plt
import webbrowser
import asyncio
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import sys
from threading import Lock







CONFIG_FILE = 'config.json'

def resource_path(relative_path):
    """ Get the absolute path to a resource, works for both script and bundled executable. """
    try:
        # PyInstaller creates a temp folder and stores paths in sys._MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Running in a normal Python environment
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# class LogManager:
#     _shared_logger = None
#     _lock = Lock()

#     @classmethod
#     def get_logger(cls, log_file_path="logfile.log"):
#         """Creates the shared log file if it doesn't exist and returns the logger object
        
#         Arguments:
#             log_file_path {string} -- path to the log file
            
#         Returns:
#             logger -- logger object
#         """
#         if cls._shared_logger is None:
#             with cls._lock:
#                 if cls._shared_logger is None:  # Double-checked locking
#                     cls._shared_logger = logging.getLogger("shared_logger")
#                     cls._shared_logger.setLevel(logging.INFO)

#                     # Create a formatter
#                     formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#                     # Add a file handler if not present
#                     if not any(isinstance(handler, logging.FileHandler) for handler in cls._shared_logger.handlers):
#                         file_handler = logging.FileHandler(log_file_path)
#                         file_handler.setLevel(logging.INFO)
#                         file_handler.setFormatter(formatter)
#                         cls._shared_logger.addHandler(file_handler)

#                     # Always add a console handler
#                     console_handler = logging.StreamHandler()
#                     console_handler.setLevel(logging.INFO)
#                     console_handler.setFormatter(formatter)
#                     cls._shared_logger.addHandler(console_handler)

#         return cls._shared_logger

#     @classmethod
#     def close_logger(cls, delete_log_file=False):
#         if cls._shared_logger:
#             # Remove all handlers associated with the logger
#             for handler in cls._shared_logger.handlers:
#                 cls._shared_logger.removeHandler(handler)
#                 handler.close()

#             cls._shared_logger = None

#             # Optionally delete the log file
#             if delete_log_file:
#                 try:
#                     os.remove("logfile.log")
#                 except OSError as e:
#                     # print(f"Error deleting log file: {e}")
class BaseBot:
    """
    Base class for implementing bots.

    This class provides a basic structure for creating bots, including the setup
    of a logger for logging bot-related activities.

    Attributes:
        logger (logging.Logger): Logger instance for the bot.
    """

    def __init__(self, name = None):
        """
        Initialize the BaseBot.

        Args:
            name (str): The name of the bot.
            database_credentials (dict): A dictionary containing the database credentials.

        """
        if name is None:
            name = 'base_bot'
        self.current_user = os.getlogin()
        self.name = name
        #self.path_dict = self.get_paths() 
        self.cards_df = self.create_cards_dataframe()
        self.path_to_log = self.get_log_file_path()
        self.last_file_size = None
        
        #use the LogManager class to create a logger
        # self.logger = LogManager.get_logger()


       
    def create_cards_dataframe(self):
        """ 
        create a dataframe that imports the cards.csv file in the cards folder in assets. Get the new cards from 17lands public dataset when a new set comes out"""

        # cards_path = resource_path('assets\\cards\\cards.csv') #for running in console
        cards_path = resource_path('assets/cards/cards.csv')
        cards_df = pd.read_csv(cards_path)
        return cards_df
    # def create_decks_dict(self):
    #     """Create a dictionary of the decks assets.

    #     Returns:
    #         decks_dict (dict): A dictionary containing the decks assets. This is dynamic so as you add more assets to the decks folder, they will be added to the dictionary.

    #         EXAMPLE
    #         {'deck_black.PNG':, 'deck_blue.PNG':,'etc...}"""
        
    #     #append 'decks' to self.path_dict['assets']
    #     decks_path = os.path.join(self.path_dict['assets'], 'decks')
    #     #for file in decks_path, add it to a dictionary where the file name is the key and the path is the value
    #     decks_dict = {}
    #     for file in os.listdir(decks_path):
    #         decks_dict[file] = os.path.join(decks_path, file)
    #     return decks_dict
    def get_log_file_path(self):
        """This function gets the path to the game log.  This function will try to automatically produce the path to the game log unless you set it manually as path_to_log in config.py"""
        if not hasattr(self, 'path_to_log') or self.path_to_log is None:
            path_to_log = os.path.expanduser(f'~{self.current_user}\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\Player.log')
            return path_to_log
        else:
            return self.path_to_log
    def delete_log_file(self):
        """This function deletes the game log.  This function will try to automatically produce the path to the game log unless you set it manually as path_to_log in config.py"""
        #check if mtga is running
        
        try:
            # Check if the file is in use
            if self.is_file_in_use(self.path_to_log):
                #self.logger.warning(f"File {self.path_to_log} is in use and cannot be deleted.")
                pass
            else:
                # Attempt to delete the file
                os.remove(self.path_to_log)
                #self.logger.info(f"File {self.path_to_log} deleted successfully.")

        except FileNotFoundError:
            #self.logger.error(f"File {self.path_to_log} not found.")
            print(f"File {self.path_to_log} not found.")

        except Exception as e:
            #self.logger.error(f"An error occurred while deleting the file: {e}")
            print(f"An error occurred while deleting the file: {e}")

    def is_file_in_use(self, file_path):
        """Check if a file is currently in use by another process."""
        try:
            # Attempt to open the file in read-only mode
            with open(file_path, 'r'):
                return False  # File is not in use
        except IOError:
            return True  # File is in use
    def get_log_size(self):
        """
        Get the size of the log file in bytes.

        Returns:
            int: Size of the log file in bytes, or -1 if file not found.
        """
        try:
            # Check if the file exists
            if os.path.exists(self.path_to_log):
                # Get the size of the file in bytes
                file_size_bytes = os.path.getsize(self.path_to_log)
                return file_size_bytes
            else:
                # File not found
                return -1
        except Exception as e:
            # print("Error:", e)
            return -1
    def get_game_log(self, position=None, path = None):
        
        """This function gets the path to the game log.  This function will try to automatically produce the path to the game log unless you set it manually as path_to_log in config.py"""
        
        """
        Tracks the new content from the log file.

        Args:
        position (int, optional): The position to start reading from the log file.

        Returns:
        tuple: A tuple containing the new content and the new position.
               If the file is not found, it returns an error de.
        """
        if path is not None:
            self.path_to_log = path
        
        try:
            with open(self.path_to_log, 'r') as file:
                if position is not None:
                    file.seek(position)
                    
                    new_content = file.read()
                    #find the first instance of \n[UnityCrossThreadLogger], and drop all text before it
                    new_content = new_content[new_content.find('[UnityCrossThreadLogger]'):]

                else:
                    new_content = file.read()

            with open(self.path_to_log, 'r') as file:
                file.seek(0, 2)
                new_position = file.tell()
            file.close()
            #remove lines with No card art found for Assets/Core/CardArt/000000/000000_AIF in them
            new_content = re.sub(r'No card art found for Assets/Core/CardArt/000000/000000_AIF', '', new_content)
            return new_content, new_position
        except FileNotFoundError:
            return "File not found.", None
    def game_log_length(self):
        """
        This function will return the current length of the game log in bytes, 
        to be used as a starting position.
        """
        with open(self.path_to_log, 'rb') as file:
            file.seek(0, os.SEEK_END)  # Move the cursor to the end of the file
            length_in_bytes = file.tell()  # Get the current position of the cursor, which is the size of the file in bytes
        return length_in_bytes

    def phrase_in_log(self, search_string, position=None):
        """h
        Search the game log for a specific string.

        Args:
        search_string (str): The string to search for.
        position (int, optional): The position to start reading from the log file.

        Returns:
        tuple: A tuple containing the new content and the new position.
               If the file is not found, it returns an error message.
        """
        log = self.get_game_log(position)
        if log[0] is not None:
            if search_string in log[0]:
                return True
            else:
                return False
            
    def extract_json_service_from_logs(self,logs): 
        """
        takes in a log file (as a string ) and extracts the MatchServieMessageType from the logs 
    
        this includes the on-hover events"""
        pattern = r"\[UnityCrossThreadLogger\]\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M: \w+ to Match: ClientToGreuimessage\n([\s\S]*?)(?=\[UnityCrossThreadLogger\]|\Z)"
        #search for all matches
        matches = re.findall(pattern, logs, re.DOTALL)
        
        json_objects = []

        for match in matches:
            try:
                json_data = json.loads(match)
                json_objects.append(json_data)
            except json.JSONDecodeError:
                pass #invalid json object
        return json_objects

    def extract_json_general_from_logs(self, logs):
        """
        Takes the log file (as a string) and extracts the relevant JSON objects from it.
        It is looking for JSON objects after the UnityCrossThreadLogger statement.

        Args:
        logs (str): The log file as a string.

        Returns:
        list: A list of JSON objects extracted from the logs.
        """
        # Define the regex pattern to match the start of the JSON object after the logger statement
        # Define the pattern
        pattern = (
            r"\[UnityCrossThreadLogger\]\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M: "
            r"(Match to \w+: GreToClientEvent\n|"
            r"\w+ to Match: ClientToGreuimessage\n[\s\S]*?)"
        )


        # Search for all positions of the pattern in the logs
        matches = re.finditer(pattern, logs)
        # List to store extracted JSON objects
        json_objects = []

        # Iterate over the matches and extract JSON objects
        for match in matches:
            # Get the start position of the JSON object
            start_pos = match.end()
            # Find the end position by looking for a closing curly brace that matches the opening ones
            end_pos = start_pos
            brace_count = 0
            in_string = False
            escape = False
            while end_pos < len(logs):
                char = logs[end_pos]
                if char == '"' and not escape:
                    in_string = not in_string
                elif char == '{' and not in_string:
                    brace_count += 1
                elif char == '}' and not in_string:
                    brace_count -= 1
                    if brace_count == 0:
                        # Found the end of the JSON object
                        end_pos += 1
                        break
                escape = (char == '\\' and not escape)
                end_pos += 1

            json_str = logs[start_pos:end_pos]

            # Attempt to load the extracted string as JSON
            try:
                json_data = json.loads(json_str)
                json_objects.append(json_data)
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON objects

        # print('number of json objects:', len(json_objects))
        return json_objects
    def extract_json_from_logs(self, logs):
        """
        Takes the log file (as a string) and extracts the relevant JSON objects from it. 
        It is looking for json objects after the unity crossthread logger statement.

        Args:
        logs (str): The log file as a string.

        Returns:
        list: A list of JSON objects extracted from the logs.
        """
        # Define the regex pattern to match the start of the JSON object after the logger statement
        pattern = r"\[UnityCrossThreadLogger\]\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M: Match to \w+: GreToClientEvent\n"
        # Search for all positions of the pattern in the logs
        matches = re.finditer(pattern, logs)
        # List to store extracted JSON objects
        json_objects = []

        # Iterate over the matches and extract JSON objects
        for match in matches:
            # Get the start position of the JSON object
            start_pos = match.end()
            # Find the end position by looking for a closing curly brace that matches the opening ones
            end_pos = start_pos
            brace_count = 0
            in_string = False
            escape = False
            while end_pos < len(logs):
                char = logs[end_pos]
                if char == '"' and not escape:
                    in_string = not in_string
                elif char == '{' and not in_string:
                    brace_count += 1
                elif char == '}' and not in_string:
                    brace_count -= 1
                    if brace_count == 0:
                        # Found the end of the JSON object
                        end_pos += 1
                        break
                escape = (char == '\\' and not escape)
                end_pos += 1

            json_str = logs[start_pos:end_pos]
            
            # Attempt to load the extracted string as JSON
            try:
                json_data = json.loads(json_str)
                json_objects.append(json_data)
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON objects

        return json_objects
    def old_extract_json_from_logs(self, logs = None):
        if logs is None:
            logs = self.get_game_log()[0]
        """
        takes the log file (as a string) and extracts the relevant JSON objects from it. 
        It is looking for json objects after the unity crossthread logger statement:

        Args:
        logs (str): The log file as a string.

        Returns:
        list: A list of JSON objects extracted from the logs.
        """
        # Define the regex pattern to match the line with the specified pattern
        pattern = r"\[UnityCrossThreadLogger\]\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}:\d{2} [AP]M: Match to \w+: GreToClientEvent\n([\s\S]*?)(?=\[UnityCrossThreadLogger\]|AudioManager:|Timer WaitingForMatc|\Z)"
        # Search for all matches of the pattern in the logs
        matches = re.findall(pattern, logs)
        # List to store extracted JSON objects
        json_objects = []

        # Iterate over the matches and extract JSON objects
        for match in matches:
            # Attempt to load each match as JSON
            try:
                json_data = json.loads(match)
                json_objects.append(json_data)
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON objects

        return json_objects
   
    
    def extract_json_from_entry(self, log_entry):
        """
        Extract the JSON data from a log entry.
        """
        start_index = log_entry.find('{')
        
        # Extract the JSON substring
        json_string = log_entry[start_index:]
        
        # Parse the JSON string
        json_data = json.loads(json_string)
        
        return json_data

    def waiting_for_the_server(self):
        time.sleep(1)
        #self.logger.info("inside waiting_for_the_server method")
        waiting_for_server_path = self.nav_dict['waiting_for_the_server.PNG']
        #wait until waiting_for_the_server is gone
        while self.locate_image(waiting_for_server_path):
            #self.logger.info("Waiting for the server...")
            time.sleep(1)
        return True
    def extract_log_block(self, log_text, search_string):
        block_started = False
        block_lines = []

        for line in log_text.split('\n'):
            if search_string in line:
                block_started = True

            if block_started:
                block_lines.append(line)

            if block_started and line.strip() == '':
                break

        if block_started:
            return '\n'.join(block_lines)
        else:
            return None
    

class PlayerLog(BaseBot):
    def __init__(self, name):
        super().__init__('log_bot')
        
    def find_game_message(self,json_data, message = 'GREMessageType_GameStateMessage'):
        "generalized function to find the latest game state message in the json data and return it"
        latest_game_state = None
    
        def traverse(data):
            nonlocal latest_game_state
            if isinstance(data, dict):
                if 'type' in data and data['type'] == message:
                    latest_game_state = data
                for value in data.values():
                    traverse(value)
            elif isinstance(data, list):
                for item in data:
                    traverse(item)
        
        traverse(json_data)
        return latest_game_state
    def find_Req_message(self, json_data, messages=('Req', 'OptionalActionMessage')):
        """Specific version of find_game_message, finds the latest Req or OptionalActionMessage in the JSON data."""
        latest_game_state = None

        def traverse(data):
            nonlocal latest_game_state
            if isinstance(data, dict):
                if 'type' in data and any(msg in data['type'] for msg in messages):
                    latest_game_state = data
                for value in data.values():
                    traverse(value)
            elif isinstance(data, list):
                for item in data:
                    traverse(item)

        traverse(json_data)
        return latest_game_state


    def find_game_object(self, instanceId, json_data =None):
        """Function that searches json for key 'instanceId == instanceId' and returns the last matching object"""
        if json_data is None:
            logs = self.get_game_log()[0]
            json_data = self.extract_json_from_logs(logs)
        if instanceId in [1, 2]:
            #create a dictionary with a key 'instanceId' and a value of the instanceId
            last_object_found = {'instanceId': instanceId}
            return last_object_found
        def traverse(data):
            nonlocal last_object_found
            if isinstance(data, dict):
                if 'instanceId' in data and data['instanceId'] == instanceId and 'grpId' in data:
                    if 'actionType' in data:
                        #dont do anything
                        pass
                    else:
                        last_object_found = data
                for value in data.values():
                    traverse(value)
            elif isinstance(data, list):
                for item in data:
                    traverse(item)

        last_object_found = None
        traverse(json_data)
        return last_object_found
    def connect_to_game(self,logs = None, position = None): 
        connected = False
        systemSeatId = False
        connect_position = None
        if logs == None:
            logs = self.get_game_log(position= position)[0]
        json_logs = self.extract_json_from_logs(logs)
        connect_json = self.find_game_message(json_logs, message = "GREMessageType_ConnectResp")
        ## print(json_logs)
        if connect_json:
            
            connected = True
            for key in connect_json.keys():
                if key == 'systemSeatIds':
                    systemSeatId = connect_json[key][0]
            #self.logger.info('connected to game')
        return connected, systemSeatId, connect_position
    

    def find_game_results(self, logs = None, position = None):
        """
        Function to find the game results in the logs, returns the game over state, result, and winning team id
        args:
            logs (str): the log file (not path) to search through
            position (int): the position in the logs to  start at
        
        return:
            game_over_state = True/False
            result = (str) completed or draw
            winningTeamId = systemSeatId of winner

        """
        game_over_state = False
        winner = None
        result = None
        winningTeamId = None
        if logs == None:
            logs = self.get_game_log(position= position)[0]
        json_logs = self.extract_json_from_logs(logs)
        game_over_json = self.find_game_message(json_logs, message = "GREMessageType_IntermissionReq")
        if game_over_json:
            game_over_state = True
            for key in game_over_json.keys():
                
                if key == 'intermissionReq':
                    winner = game_over_json[key]['result']
                    result = winner['result']
                    winningTeamId = winner['winningTeamId']
                
            #self.logger.info('game over')
        return game_over_state, result, winningTeamId
    

    def find_mulligan(self, logs = None, position = None):
        mulligan_found = False
        if logs == None:
            logs = self.get_game_log(position= position)[0]
        json_logs = self.extract_json_from_logs(logs)
        mulligan_json = self.find_game_message(json_logs, message = "GREMessageType_MulliganReq")
        if mulligan_json:
            mulligan_found = True
            #self.logger.info('mulligan found in logs')
        return mulligan_found
    def find_systemSeatId(self, logs = None, position = None):
        systemSeatId = None
        if logs == None:
            logs = self.get_game_log(position= position)[0]
        json_logs = self.extract_json_from_logs(logs)
        mulligan_json = self.find_game_message(json_logs, message = "GREMessageType_MulliganReq")
        if mulligan_json:
            # get "systemSeatIds" from the json
            
            system_seat_ids = mulligan_json.get('systemSeatIds', [])
            #self.logger.info('systemSeatId found in logs, systemSeatId: %s', system_seat_ids)
        return system_seat_ids


    def get_current_game_state(self, logs = None , position = None):
        if logs == None:
            logs = self.get_game_log(position= position)[0]
        json_logs = self.extract_json_from_logs(logs)
        #self.game_state['json_logs'] = json_logs
        game_state = self.find_game_message(json_logs, message = "GREMessageType_GameStateMessage")
        return game_state
    
    
    
    def game_state_one_shot(self):
        "for testing. main game state updater is asynchrounous"
        current_game_state = self.get_current_game_state()
        
        gs ={}    
        gs['gameStateId'] = current_game_state.get('gameStateId', None)
        gs['msgId'] = current_game_state.get('msgId', None)

    
        try: 
            turnInfo = current_game_state['gameStateMessage']['turnInfo']
        except:
            turnInfo = None
        if turnInfo:
            gs['turnNumber'] = turnInfo['turnNumber']
            gs['phase'] = turnInfo['phase']
            try:
                gs['step'] = turnInfo['step']
            except:
                gs['step'] = None
            gs['activePlayer'] = turnInfo['activePlayer']
            gs['priorityPlayer'] = turnInfo['priorityPlayer']
        else:
            pass
            #self.logger.info('no turn info found')
            # print('no turn info found')
        return gs

    def get_current_game_state_diff(self, logs = None, position = None):
        if logs == None:
            logs = self.get_game_log(position= position)
        json_logs = self.extract_json_from_logs(logs)
        game_state_diff = self.find_game_message(json_logs, message = "GameStateType_Diff")
        return game_state_diff
    
    
    # def get_legal_attackers_and_target(self, gameStateId, json_logs = None, position = None):
    #     """
    #     part of the attack protocol, when given the correct attack step gameStateId, this function will return the legal attackers and targets from the json with
    #     "type": "GREMessageType_DeclareAttackersReq"

    #     """
    #     if json_logs == None:
    #         logs = self.get_game_log(position= position)[0]
    #         json_logs = self.extract_json_from_logs(logs)
    #     attack_json = self.find_game_message(json_logs, message = "GREMessageType_DeclareAttackersReq")
    #     if attack_json:
    #         attacker_instanceIds = []
    #         targets = []
    #         qualified_attackers =  attack_json['declareAttackersReq']['qualifiedAttackers']
    #         for i in qualified_attackers:
    #             attacker_instanceIds.append(i['attackerInstanceId'])
    #             targets.append(i['legalDamageRecipients'][0]['type'])

    #         #unique values of targets
    #         targets = list(set(targets))
    #         #targets are there, not returning them for now
    #         return attacker_instanceIds
        
    # def find_hovered_card(self, json_logs=None):

    #     """
    #     Looks at the action related json and finds the LAST hovered card
        
    #     returns:
    #         hovered card instanceId"""
    #     if json_logs is None:
    #         logs = self.get_game_log()[0]
    #         json_logs = self.extract_json_service_from_logs(logs)

    #     hovered_card_id = None

    #     # Find the last JSON object that matches the hovered card ID
    #     hovered_card_json = None
    #     for log in reversed(json_logs):
            
    #         if ('payload' in log) and ('uiMessage' in log['payload']) and ('objectId' in log['payload']['uiMessage']['onHover']):
    #             hovered_card_id = log['payload']['uiMessage']['onHover']['objectId']
    #             return hovered_card_id
    #     else :
    #         self.logger.info('No hovered card found')
    #         return None

class ManaBugApp(BaseBot):


    def __init__(self, gui ):
        super().__init__('player')  # Call the BaseBot constructor to set up the logger
        self.gui = gui
        self.game_state = {'gameStateId': None,'msgId':None, 'turnNumber': 0, 'phase': None, 'step': None, 'activePlayer': None, 'priorityPlayer': None, 'action_required': False, 'action_required_json': None}
        self.player_log = PlayerLog('log_bot')
        if self.player_log is not None:
            self.gui.update_text("log file found")
        else:
            self.gui.update_text('log file not found')
        self.game_id = None
        self.print = True
        #self.dataframe_pairs_list = self.load_dataframe_pairs()
        self.efficient_cards = None
        







    def check_for_actions(self, gameStateId = None, logs = None, position = None):
        """
        extracts UIMessage json objects from the logs and checks for action related messages
        returns the actions available message if found"""
        actions = None
        if logs == None:
            logs = self.player_log.get_game_log(position= position)[0]
        json_logs = self.player_log.extract_json_general_from_logs(logs)
        #actions_message = self.player_log.find_game_message(json_logs, message = "GREMessageType_ActionsAvailableReq")
        actions_message = self.player_log.find_Req_message(json_logs)
        if actions_message:
            gameStateId = actions_message.get('gameStateId')
            #check  that gameStateId is the same as the one passed in
            if gameStateId == self.game_state['gameStateId']:
                actions = actions_message
        return actions
    
    def get_targets(self):
        data = self.game_state['action_required_json']
        all_targets = []

        # Collect all targets with their highlight types
        for target_group in data['selectTargetsReq']['targets']:
            for target in target_group['targets']:
                target_info = {
                    'targetInstanceId': target['targetInstanceId'],
                    'highlight': target.get('highlight', 'No_Highlight')  # Use 'No_Highlight' if highlight is not present
                }
                all_targets.append(target_info)

        game_log = self.get_game_log()[0]
        object_search_json = self.extract_json_from_logs(game_log)
        target_df = self.target_object_df()

        # Get the game objects and add to the DataFrame along with highlight type
        for target in all_targets:
            target_object = self.player_log.find_game_object(json_data=object_search_json, instanceId=target['targetInstanceId'])
            target_object['highlight'] = target['highlight']
            target_df = self.add_object_to_df(target_df, target_object)
        #self.logger.info('target_df: \n %s ', target_df.to_string())
        # print('target_df: \n', target_df.to_string())
        #input('Press Enter to continue...')
        return target_df


 












#game object dataframe functions


    def game_object_df(self):
        "returns basic game_object_dataframe used in attacking and blocking"
        return pd.DataFrame(columns=['instanceId', 'grpId','card_types', 'zoneId','controllerSeatId', 'power', 'toughness', 'abilities', 'is_tapped', 'highlight'])
    
    def target_object_df(self):
        "returns basic target_object_dataframe used in selecting targets"
        return pd.DataFrame(columns=['instanceId', 'grpId','zoneId','controllerSeatId', 'card_types','power', 'toughness', 'abilities', 'is_tapped', 'highlight'])
    def add_object_to_df(self,df, obj):
        instance_id = obj.get('instanceId', None)
        grpId = obj.get('grpId', None)
        zoneId = obj.get('zoneId', None)
        controllerSeatId = obj.get('controllerSeatId', None)
        card_types = obj.get('card_types', None)
        power = obj.get('power', {}).get('value', 0) if isinstance(obj.get('power'), dict) else 0
        toughness = obj.get('toughness', {}).get('value', 0) if isinstance(obj.get('toughness'), dict) else 0
        abilities = obj.get('abilities', None)
        is_tapped = obj.get('isTapped', None)
        highlight = obj.get('highlight', None)
        new_row = {
            'instanceId': instance_id,
            'grpId': grpId,
            'zoneId': zoneId,
            'controllerSeatId': controllerSeatId,
            'card_types': card_types,
            'power': power,
            'toughness': toughness,
            'abilities': abilities,
            'is_tapped': is_tapped,
            'highlight': highlight
        }
        # Convert the new row to a DataFrame
        new_row_df = pd.DataFrame([new_row])
        #self.logger.info('new_row_df:', new_row_df)
        df = pd.concat([df, new_row_df], ignore_index=True)
        #self.logger.info('df after concat:', df)
        return df
    
    def create_card_dictionary(self, card_tuple, action_type=None, detail_mana_cost=None):
        """
        Creates a dictionary of card information from the card_tuple.

        Args:
            card_tuple (tuple): Tuple with the card id and instanceId.
            action_type (str, optional): Type of action, if applicable.
            detail_mana_cost (dict, optional): Additional mana cost details.

        Returns:
            dict: Dictionary with keys 'instanceId', 'grpId', 'name', 'mana_value', 'types', 'action_type', and any additional detail_mana_cost information.
        """
        # print('# printing card for card dict:', card_tuple)

        # Filter the DataFrame to find the row corresponding to the given card id
        card_row = self.cards_df[self.cards_df['id'] == card_tuple[0]]
        # print('Card row:', card_row)

        # Initialize the card dictionary with default values
        card_dict = {
            'instanceId': card_tuple[1],
            'grpId': card_tuple[0],
            'name': card_row['name'].iloc[0] if not card_row.empty else None,
            'mana_value': card_row['mana_value'].iloc[0] if not card_row.empty else None,
            'types': None,
            'action_type': action_type
        }

        # # print debugging information
        # if card_row.empty:
        #     # print(f"Warning: No data found for card_tuple: {card_tuple}")
        # else:
        #     # print('Card dict mana value:', card_dict['mana_value'])

        # Use a dictionary to map card types to their respective string values
        type_mapping = {
            'land': 'land',
            'creature': 'creature',
            'instant': 'instant',
            'sorcery': 'sorcery',
            'enchantment': 'enchantment'
        }

        # Check and set card types using regular expression matching
        for type_key, type_value in type_mapping.items():
            if card_row['types'].str.contains(type_key, flags=re.IGNORECASE).any():
                card_dict['types'] = type_value
                break  # Exit loop once a type is found

        # Include detailed mana cost information if provided
        if detail_mana_cost:
            card_dict.update(detail_mana_cost)

        return card_dict

    def create_target_dataframe(self, targets):
        """
        creates a DataFrame of the targets available to the player
        args:
            targets (list): list of targets available to the player, produced by the self.check_for_actions() function
        returns:
            target_df (DataFrame): DataFrame with columns 'instanceId', 'grpId', 'name', 'mana_value', and 'types'"""
        data = []
        for i in targets:
            card_tuple = (i.get('grpId'), i.get('instanceId'))
            """data.append(self.create_card_dictionary(card_tuple))
        target_df = pd.DataFrame(data)
        return target_df"""
    def process_game_object_manacost(self, mana_cost):
        # Define a mapping of mana colors to their corresponding keys
        # print('working on mana cost:', mana_cost)
        mana_mapping = {
            'ManaColor_Generic': 'a',
            'ManaColor_White': 'w',
            'ManaColor_Blue': 'u',
            'ManaColor_Black': 'b',
            'ManaColor_Red': 'r',
            'ManaColor_Green': 'g',
            "ManaColor_Colorless": 'c'
        }

        # Define all two-color combinations
        two_color_combinations = {
            ('ManaColor_White', 'ManaColor_Blue'): 'wu',
            ('ManaColor_White', 'ManaColor_Black'): 'wb',
            ('ManaColor_White', 'ManaColor_Red'): 'wr',
            ('ManaColor_White', 'ManaColor_Green'): 'wg',
            ('ManaColor_Blue', 'ManaColor_Black'): 'ub',
            ('ManaColor_Blue', 'ManaColor_Red'): 'ur',
            ('ManaColor_Blue', 'ManaColor_Green'): 'ug',
            ('ManaColor_Black', 'ManaColor_Red'): 'br',
            ('ManaColor_Black', 'ManaColor_Green'): 'bg',
            ('ManaColor_Red', 'ManaColor_Green'): 'rg',
            #('ManaColor_Black', 'ManaColor_White'): 'bw',
            ('ManaColor_Red', 'ManaColor_Blue'): 'ru',
            ('ManaColor_Green', 'ManaColor_White'): 'gw',
            ('ManaColor_Blue', 'ManaColor_Red'): 'ur',
            #('ManaColor_Black', 'ManaColor_Green'): 'gb',
        }

        # Initialize an empty dictionary to store the result
        mana_dict = {}

        # Iterate through the list and populate the dictionary
        for item in mana_cost:
            # print('working on mana item:', item)
            colors = item['color']
            count = item['count']
            if len(colors) == 1:
                color = colors[0]
                if color in mana_mapping:
                    mana_key = mana_mapping[color]
                    mana_dict[mana_key] = mana_dict.get(mana_key, 0) + count
            elif len(colors) == 2:
                # print('working on two color combination:', colors)
                color_pair = tuple(colors)
                # color_pair = tuple(sorted(colors))
                # print("color_pair_tupled:", color_pair)
                if color_pair in two_color_combinations:
                    mana_key = two_color_combinations[color_pair]
                    mana_dict[mana_key] = mana_dict.get(mana_key, 0) + count

        return mana_dict

    def create_action_dataframe(self, actions, activate_card = False):
        action_list = actions.get('actionsAvailableReq').get('actions')

        """placeholder function, only works for lands and creatures at the moment
        args:
            action_list (list): list of actions available to the player, produced by the self.check_for_actions() function
        returns:
            action_df (DataFrame): DataFrame with columns 'instanceId', 'grpId', 'name', 'mana_value', and 'types'
            available_mana (int): amount of available mana for the player to use
        """
        data = []
        available_mana = 0
        for i in action_list:
            if i.get('actionType') == 'ActionType_Activate_Mana':
                available_mana +=1
            if i.get('actionType') == 'ActionType_Play':
                action_type = 'play'
                card_tuple = (i.get('grpId'), i.get('instanceId'))
                data.append(self.create_card_dictionary(card_tuple, action_type))

            # spells
            if i.get('actionType') == 'ActionType_Cast':
                if i.get('autoTapSolution'):
                    action_type = 'cast'
                    #mana_cost = i.get('autoTapSolution').get('manaCost')
                    mana_cost = i.get('manaCost')
                    detail_mana_cost = self.process_game_object_manacost(mana_cost)
                    # print('detail_mana_cost: %s', str(detail_mana_cost))
                    # print('type: %s', type(detail_mana_cost))
                    card_tuple = (i.get('grpId'), i.get('instanceId'))
                    data.append(self.create_card_dictionary(card_tuple, action_type, detail_mana_cost))
            if i.get('actionType') == 'ActionType_CastLeft':
                if i.get('autoTapSolution'):
                    action_type = 'cast'
                    #mana_cost = i.get('autoTapSolution').get('manaCost')
                    mana_cost = i.get('manaCost')
                    detail_mana_cost = self.process_game_object_manacost(mana_cost)
                    # print('detail_mana_cost: %s', str(detail_mana_cost))
                    # print('type: %s', type(detail_mana_cost))
                    card_tuple = (i.get('grpId'), i.get('instanceId'))
                    data.append(self.create_card_dictionary(card_tuple, action_type, detail_mana_cost))

            if i.get('actionType') == 'ActionType_CastRight':
                if i.get('autoTapSolution'):
                    action_type = 'cast'
                    #mana_cost = i.get('autoTapSolution').get('manaCost')
                    mana_cost = i.get('manaCost')
                    detail_mana_cost = self.process_game_object_manacost(mana_cost)
                    # print('detail_mana_cost: %s', str(detail_mana_cost))
                    # print('type: %s', type(detail_mana_cost))
                    card_tuple = (i.get('grpId'), i.get('instanceId'))
                    data.append(self.create_card_dictionary(card_tuple, action_type, detail_mana_cost))


            if i.get('actionType') == "ActionType_CastAdventure":
                if i.get('autoTapSolution'):
                    action_type = 'cast'
                    #mana_cost = i.get('autoTapSolution').get('manaCost')
                    mana_cost = i.get('manaCost')
                    detail_mana_cost = self.process_game_object_manacost(mana_cost)
                    # print('detail_mana_cost: %s', str(detail_mana_cost))
                    # print('type: %s', type(detail_mana_cost))
                    card_tuple = (i.get('grpId'), i.get('instanceId'))
                    data.append(self.create_card_dictionary(card_tuple, action_type, detail_mana_cost))

            if i.get('actionType') == "ActionType_Special":
                if i.get('autoTapSolution'):
                    action_type = 'cast'
                    mana_cost = i.get('manaCost')
                    detail_mana_cost = self.process_game_object_manacost(mana_cost)
                    # print('detail_mana_cost: %s', str(detail_mana_cost))
                    # print('type: %s', type(detail_mana_cost))
                    card_tuple = (i.get('grpId'), i.get('instanceId'))
                    data.append(self.create_card_dictionary(card_tuple, action_type, detail_mana_cost))


            # actions
            if i.get('actionType') == 'ActionType_Activate':
                if i.get('autoTapSolution'):
                    action_type = 'activate'
                    card_tuple = (i.get('grpId'), i.get('instanceId'))
                    data.append(self.create_card_dictionary(card_tuple,  action_type))

        action_df = pd.DataFrame(data)
        
        #drop all rows where action_type == 'activate'
        try:
            action_df = action_df[action_df['action_type'] != 'activate']
        except KeyError:
            pass
        
        # self.logger.info('action_df: %s', action_df.to_string())
        return action_df, available_mana



    def extract_activate_mana_actions(self, data):
        actions = data.get('actionsAvailableReq', {}).get('actions', [])
        activate_mana_actions = [action for action in actions if action.get('actionType') == 'ActionType_Activate_Mana']
        return activate_mana_actions
    def create_mana_dataframe(self,data):
        def extract_mana_colors(mana_payment_options):
            # print('working on :', mana_payment_options)
            colors = {'w': 0, 'u': 0, 'b': 0, 'r': 0, 'g': 0,'c': 0}
            for option in mana_payment_options:
                for mana in option['mana']:
                    if mana['color'] == 'ManaColor_White':
                        colors['w'] += 1
                    elif mana['color'] == 'ManaColor_Blue':
                        colors['u'] += 1
                    elif mana['color'] == 'ManaColor_Black':
                        colors['b'] += 1
                    elif mana['color'] == 'ManaColor_Red':
                        colors['r'] += 1
                    elif mana['color'] == 'ManaColor_Green':
                        colors['g'] += 1
                    elif mana['color'] == 'ManaColor_Colorless':
                        colors['c'] += 1
            return colors

        rows = []
        for entry in data:
            # print('working on entry: ', entry)
            mana_colors = extract_mana_colors(entry.get('manaPaymentOptions', []))
            row = {
                'grpId': entry.get('grpId'),
                'instanceId': entry.get('instanceId'),
                'w': mana_colors['w'],
                'u': mana_colors['u'],
                'b': mana_colors['b'],
                'r': mana_colors['r'],
                'g': mana_colors['g'],
                'c': mana_colors['c'],
                'manaCost': entry.get('manaCost', []),
                'maxActivations': entry.get('maxActivations', 0)
            }
            # print('produced row: ', row)
            rows.append(row)

        df = pd.DataFrame(rows, columns=['grpId', 'instanceId', 'w', 'u', 'b', 'r', 'g','c', 'manaCost', 'maxActivations'])
        df = self.add_rigidity(df)
        df = df[df['rigidity'] > 0]
        return df
    






    ## stuff for mana optimizer
    def get_total_mana(self, mana):
        #drop any row where there is a duplicate in instanceId
        mana = mana.drop_duplicates(subset=['instanceId'])
        total_mana = mana.shape[0]
        return total_mana

    def card_cmc(self, card):
        col_index = card.index.get_loc('action_type')
        mana_cols = card.iloc[col_index + 1:]
        card_cmc_value = mana_cols.sum()
        return card_cmc_value

    def find_combos(self, cards_df, total_mana):
        # print('finding combos for total mana: ', total_mana)
        cards_df = cards_df[cards_df['types'] != 'land']
        # print('cards_df inside find_combos: ', cards_df)
        if cards_df.shape[0] == 0:
            return []
        cmc_values = cards_df['cmc'].values
        # print('cmc vals: ', cmc_values)
        indices = cards_df.index.values
        # print('indices: ', indices)
        combo_lengths = list(range(1, len(indices) + 1))
        output_dict = {}
        combo_lengths.reverse()
        combo_found = False
        while not combo_found and total_mana > 0:
            # print('looping for total mana: ', total_mana)
            for combo_length in combo_lengths:
                for combo in combinations(indices, combo_length):
                    cmc_sum = 0
                    combo_names = []
                    for index in combo:
                        cmc_sum += cards_df.loc[index, 'cmc']
                        combo_names.append(cards_df.loc[index, 'instanceId'])
                    if cmc_sum == total_mana:
                        # print('combo found: ', combo_names)
                        if total_mana in output_dict:
                            output_dict[total_mana].append(combo_names)
                        else:
                            output_dict[total_mana] = [combo_names]
                        combo_found = True
            total_mana -= 1
        return output_dict

    def get_max_efficiency(self, mana, cards, iter):   
        if mana.empty or cards.empty:
            return None
        total_mana = self.get_total_mana(mana)
        total_mana = total_mana - iter
        cmc_list = []
        for _, card in cards.iterrows():
            card_cmc_value = self.card_cmc(card)
            cmc_list.append(card_cmc_value)
        cards['cmc'] = cmc_list
        combos = self.find_combos(cards, total_mana)
        if not combos:
            return None
        return total_mana, combos

    def create_mana_cost_df(self, cards_df, combo_ids):
        cards_df = cards_df[cards_df['instanceId'].isin(combo_ids)]
        cols = cards_df.columns.tolist()
        start_index = cols.index('action_type') + 1
        end_index = cols.index('cmc')
        cards_df_selected = cards_df.iloc[:, start_index:end_index]
        cards_df_selected = cards_df_selected.sum().to_dict()
        return cards_df_selected

    def add_rigidity(self, mana_df):
        df = mana_df.copy()
        cols = df.columns.tolist()
        start_index = cols.index('instanceId') + 1
        end_index = cols.index('manaCost')
        mana_only = df.iloc[:, start_index:end_index]
        rigidity = mana_only.sum(axis=1)
        df.insert(end_index, 'rigidity', rigidity)
        return df

    def pay_mana(self, mana_df, color):
        # print('inside pay_mana')
        # print('color:', color)
        # print('mana_df:', mana_df)
        # Split the color into individual components
        color_components = list(color)

        # Filter rows where any of the color columns in color_components have values greater than zero
        color_df = mana_df[(mana_df[color_components] > 0).any(axis=1)]
        # print('color_df:', color_df)
        if color_df.empty:
            return False, None
        else:
            min_rigidity = color_df['rigidity'].min()
            min_rigid_rows = color_df[color_df['rigidity'] == min_rigidity]
            random_row = min_rigid_rows.sample(n=1)
            selected_index = random_row.index[0]
            popped_row = mana_df.loc[selected_index]
            mana_df = mana_df.drop(index=selected_index)
            return True, mana_df

    def pay_all_mana(self, mana_df, combo_costs):
        # print('inside pay_all_mana')
        # print('mana_df:', mana_df)
        # print('combo_costs:', combo_costs)
        if 'a' in combo_costs:
            del combo_costs['a']
        nonzero_dict = {k: v for k, v in combo_costs.items() if v != 0}
        # print('nonzero dict:', nonzero_dict)
        while nonzero_dict:
            color_with_lowest_val = min(nonzero_dict, key=nonzero_dict.get)
            paid, mana_df = self.pay_mana(mana_df, color_with_lowest_val)
            if paid:
                nonzero_dict[color_with_lowest_val] -= 1
                if nonzero_dict[color_with_lowest_val] <= 0:
                    del nonzero_dict[color_with_lowest_val]
            else:
                # print('unpayable cost')
                return False
        # print('cost paid')
        return True

    # process a single mana_df and card_df pair
    def process_single_cost(self, mana_df, card_df):
        # print('-----New Pair-----')
        playable_combos = []
        iter = 0
        while len(playable_combos) < 1:
            # print(f'iter is now: {iter}')
            max_efficiency = self.get_max_efficiency(mana_df, card_df, iter = iter)
            # print('mana_df:', mana_df, '\n')
            # print('card_df:', card_df, '\n')
            # print('max_efficiency:', max_efficiency)
            
            if max_efficiency is not None:
                combo_dict = max_efficiency[1]
                for key, val in combo_dict.items():
                    for combo in val:
                        # print('working on combo:', combo)
                        mana_costs = self.create_mana_cost_df(card_df, combo)
                        # print('mana_costs:', mana_costs)
                        mana_df_with_rigidity = mana_df
                        #remove rows where rigidity is 0
                        mana_df_with_rigidity = mana_df_with_rigidity[mana_df_with_rigidity['rigidity'] > 0]
                        # print('mana_df_with_rigidity:', mana_df_with_rigidity)
                        cost_paid = self.pay_all_mana(mana_df_with_rigidity, mana_costs)
                        if cost_paid:
                            combo_cards = card_df[card_df['instanceId'].isin(combo)]
                            #create a list of 'name' from combo_cards
                            combo_names = combo_cards['name'].values.tolist()
                            #append combo_cards['name'] to playable_combos
                            playable_combos.append(combo_names)
                #turn playable combos from an array into a list:
                else:
                    iter += 1
                    if iter>10:
                        return playable_combos, max_efficiency
            else:
                iter +=1
                if iter>10:
                    return playable_combos, max_efficiency
                    
        return playable_combos, max_efficiency
           
        # else:
        #     # print('mana efficiency is None')
        #     return None

       











# macro game routines

    
    def main_phase_action(self):
        """
        main_phase_action is the main function that will be called to make decisions on what actions to take in the main phase

        You can module out the base_main_phase_action_decision function and replace it with a custom function to change how the bot
        decides what the next action to be taken in the main phase should be
        
        """
        #check if self.game_state['action' is still true]
        if self.game_state['action_required'] == False or self.game_state['phase'] not in ['Phase_Main1', 'Phase_Main2']:

            return False
        
        #get action list
        actions = self.check_for_actions(gameStateId = self.game_state['gameStateId'])
        df, mana_available  = self.create_action_dataframe(actions)
        if self.game_state['action_required'] == False or self.game_state['phase'] not in ['Phase_Main1', 'Phase_Main2']:
            return False
        action = self.action_decision.main_phase(df, mana_available)
        self.zero_cursor()
        return True
    
            












    ## ASYNC ROUTINES

    async def update_game_state(self, sleep_time = 1, game_starting_position = None):
        
        while True:
            
            current_state = self.player_log.get_current_game_state(position = game_starting_position)
            try:
                self.game_state['gameStateId'] = current_state.get('gameStateId')
                self.game_state['msgId'] = current_state.get('msgId')
            except:
                # self.logger.info('No game state found')
                print('No game state found')
           
            
            try:
                turnInfo = current_state.get('gameStateMessage').get('turnInfo')
            except:
                turnInfo = None
            
            
            
            if turnInfo:
                self.game_state['turnNumber'] = turnInfo.get('turnNumber')
                self.game_state['phase'] = turnInfo.get('phase')
                self.game_state['step'] = turnInfo.get('step')
                self.game_state['activePlayer'] = turnInfo.get('activePlayer')
                self.game_state['priorityPlayer'] = turnInfo.get('priorityPlayer')
            else:
                # self.logger.info('No turnInfo found in game state')
                print('No turnInfo found in game state')
            
            
            actions = self.check_for_actions(gameStateId = self.game_state['gameStateId'], position = game_starting_position)
            
            if actions:
                self.game_state['action_required'] = True
                self.game_state['action_required_json'] = actions
            else:
                self.game_state['action_required'] = False
                self.game_state['action_required_json'] = None
            
            await asyncio.sleep(sleep_time)

    def format_gui_output(self, mana_available, action_df):
        return f'mana available: {mana_available} \n {action_df.to_string()}'

    async def show_actions(self,record = True, sleep_time=1):
        while True:
            if self.game_state['action_required']:
                # self.logger.info('action required is True')
                # self.logger.info('action type: %s', self.game_state['action_required_json']['type'])
                try:
                    prompt = self.game_state['action_required_json']['prompt']['promptId']
                except KeyError:
                    # print('can"t get prompt')
                    prompt = None
                # self.logger.info(f'prompt: {prompt}')

                if prompt ==2:
                    # self.logger.info('play spells detected')
                    actions = self.game_state['action_required_json']
                    if actions is not None:
                        action_df, mana_available  = self.create_action_dataframe(actions)
                        # self.logger.info('df: %s', action_df.to_string())
                        # self.logger.info('mana_available: %s', mana_available)
                        mana_actions = self.extract_activate_mana_actions(self.game_state['action_required_json'])
                        # # print('mana_actions:', mana_actions)    
                        mana_df = self.create_mana_dataframe(mana_actions)
            
                        # print('action_df')
                        # print(action_df)
                        # print('mana_df')
                        # print(mana_df)

                        new_play, max_efficiency = self.process_single_cost(mana_df, action_df)
                        # print('new play returned from process_single_cost:', new_play)
                        # print('val of self.efficent_cards:', self.efficient_cards)
                        
                        if max_efficiency is not None:
                            print('max efficiency is not none')
                            print('max_efficiency:', max_efficiency[0])
                        else:
                            # print('max efficiency is none')
                            output_string = 'No Plays'
                            self.gui.update_text(output_string)
                        if self.efficient_cards is None and new_play is not None:
                            self.efficient_cards = new_play
                            # self.logger.info('new play: %s', self.efficient_cards)
                            if max_efficiency is not None:   
                                output_string = 'max efficiency:'+str(max_efficiency[0]) + '\n' 
                                
                                for i in self.efficient_cards:
                                    output_string += '\n---------------\n'
                                    for card in i: 
                                        output_string += card + ' , '
                                # print('output string: ', output_string)
                                self.gui.update_text(output_string)
                        elif new_play is not None and self.efficient_cards is not None:
                            if new_play != self.efficient_cards:  
                                self.efficient_cards = new_play                           
                                # self.logger.info('new play: %s', self.efficient_cards)
                                if max_efficiency is not None:   
                                    output_string = 'max efficiency:'+str(max_efficiency[0]) + '\n' 
                                    
                                    for i in self.efficient_cards:
                                        output_string += '\n---------------\n'
                                        for card in i: 
                                            output_string += card + ' , '
                                self.gui.update_text(output_string)
                        

            await asyncio.sleep(sleep_time)
    

class ManaBugGUI:
    def __init__(self, root):
        self.root = root
        self.root.title('Mana Bug')
        self.text_area = ScrolledText(root, wrap=tk.WORD, width=40, height=10)
        self.text_area.pack(padx=10, pady=10)
        
        # self.kill_button = tk.Button(root, text='Kill', command=self.stop_loop)
        # self.kill_button.pack(pady=5)
        self.start_stop_button = tk.Button(root, text = "Start", command = self.toggle_loop)
        self.start_stop_button.pack(pady=5)

        self.log_path = self.load_log_path()
        self.log_path_label = tk.Label(root, text = "log file path: "+ self.log_path)
        self.log_path_label.pack(pady=5)

        self.set_log_button = tk.Button(root, text = "Set Log File Path", command = self.set_log_path)
        self.set_log_button.pack(pady=5)
        
        self.loop = None
        self.loop_running = False
        self.thread = None
        self.bring_to_front()

    def update_text(self, text):
        # print('running update_text')

        # Split the text into sections based on the line spacers
        sections = text.split('\n---------------\n')

        # Use a set to keep track of unique sections
        unique_sections = set()
        unique_text = []

        for section in sections:
            # Strip leading and trailing whitespace for comparison
            section = section.strip()
            if section not in unique_sections and section:
                unique_sections.add(section)
                unique_text.append(section)

        # Join the unique sections with the line spacers
        text_no_duplicates = '\n---------------\n'.join(unique_text)

        # Update the text area with the unique text
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, text_no_duplicates + '\n')
        self.text_area.see(tk.END)
        self.bring_to_front()


    def bring_to_front(self):
        self.root.lift()
        self.root.attributes('-topmost', 1)
        self.root.after_idle(self.root.attributes, '-topmost', 0)
    def toggle_loop(self):
        if self.loop_running:
            self.stop_loop()
        else:
            self.start_loop()
    def start_loop(self):
        if not self.loop_running:
            self.thread = threading.Thread(target = run_asyncio_in_thread, args=(self,))
            self.thread.start()
            self.start_stop_button.config(text = "Kill")
            self.loop_running = True
    def stop_loop(self):
        if self.loop_running:
            if self.loop:
                self.loop.call_soon_threadsafe(self.loop.stop)
            if self.thread:
                self.thread.join()
            self.start_stop_button.config(text = "Start")
            self.loop_running = False
    # def stop_loop(self):
    #     if self.loop:
    #         self.loop.call_soon_threadsafe(self.loop.stop)
    #         self.kill_button.config(state=tk.DISABLED)  # Disable the button after clicking
    
    def set_log_path(self):
        log_path = filedialog.askopenfilename()
        if log_path:
            self.log_path = log_path
            self.log_path_label.config(text = "log file path: "+ self.log_path)
            self.save_log_file_path()
    def save_log_file_path(self, path):
        config = {'log_path': path}
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file)
    def load_log_path(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                config = json.load(config_file)
                return config.get('log_path', '')
        return ''

def run_asyncio_in_thread(gui):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    gui.loop = loop  # Store the loop in the GUI object for access in the kill button
    sleep_time = .25
    manabug = ManaBugApp(gui)
    tasks = asyncio.gather(
        manabug.show_actions(sleep_time = sleep_time),
        manabug.update_game_state(sleep_time = sleep_time)
    )
    try:
        loop.run_until_complete(tasks)
    except asyncio.CancelledError:
        pass  # Handle the loop cancellation gracefully
    finally:
        loop.close()



def show_popup():
    def open_link(url):
        webbrowser.open_new(url)

    popup = tk.Toplevel()
    popup.title("Welcome to Mana Bug")

    # Create a Text widget for more complex formatting
    text_widget = tk.Text(popup, wrap="word", width=60, height=20)
    text_widget.pack(expand=True, fill="both", padx=20, pady=20)

    # Define the message with placeholders for links
    message = """WELCOME TO THE MANA BUG:
The Mana Bug will present you with the most mana efficient plays available at any time.

Mana efficiency is a major driver of success in Magic: The Gathering. Spending mana effectively can significantly increase your chances of winning.

Here are some of my findings about the effects of mana efficiency on winning in Magic: """

    # Insert the message into the Text widget
    text_widget.insert("1.0", message)

    # Add the first hyperlink
    efficiency_link = "https://jackjosephwright.github.io/mana-efficiency"
    text_widget.insert("end", "mana efficiency website", "link efficiency_link")

    # Continue with the rest of the message
    message_end = """

USING MANA BUG: Make sure "detailed logs" are turned on in MTG Arena. The program will try to locate your log file automatically. If it fails, you can set the log file path manually.
Press start and the Mana Bug will read your log file.

HIRE ME:
My name is Jack Wright, and I am a Data Scientist/Programmer looking for work. Please check out my LinkedIn: """

    # Insert the continuation of the message
    text_widget.insert("end", message_end)

    # Add the second hyperlink
    linkedin_link = "https://www.linkedin.com/in/jack-wright-97b9b61b7/"
    text_widget.insert("end", "LinkedIn", "link linkedin_link")

    # Configure tags
    text_widget.tag_configure("link", foreground="blue", underline=True)
    text_widget.tag_bind("link", "<Enter>", lambda e: text_widget.config(cursor="hand2"))
    text_widget.tag_bind("link", "<Leave>", lambda e: text_widget.config(cursor=""))
    text_widget.tag_bind("efficiency_link", "<Button-1>", lambda e: open_link(efficiency_link))
    text_widget.tag_bind("linkedin_link", "<Button-1>", lambda e: open_link(linkedin_link))

    # Disable editing in the Text widget
    text_widget.config(state="disabled")

    # Add an OK button to close the popup
    tk.Button(popup, text="OK", command=popup.destroy).pack(pady=10)

    # Ensure all events go to the popup until it is closed
    popup.grab_set()
    popup.wait_window()

# def show_popup():
#     popup = tk.Toplevel()
#     popup.title("Welcome to Mana Bug")
    
#     message = """WELCOME TO THE MANA BUG:
#     The Mana Bug will present you with the most mana efficient plays available at any time.

# Mana efficiency is a major driver of success in Magic: The Gathering. Spending mana effectively can significantly increase your chances of winning.


# Here are some of my findings about the effects of mana efficiency on winning in Magic: [link]


# USING MANA BUG: Make sure "detailed logs" are turned on in MTG Arena. The program will try to locate your log file automatically. If it fails, you can set the log file path manually.
# Press start and the Mana Bug will read your log file


# HIRE ME:
# My name is Jack Wright, and I am a Data Scientist/Analyst looking for work. Please check out my LinkedIn: [link]"""
    
#     tk.Label(popup, text=message, padx=20, pady=20, wraplength=300, justify="left").pack()
#     tk.Button(popup, text="OK", command=popup.destroy).pack(pady=10)
    
#     # Wait for the popup window to be destroyed before continuing
#     popup.grab_set()  # Ensure all events go to the popup until it is closed
#     popup.wait_window()

def start_gui():
    root = tk.Tk()
    gui = ManaBugGUI(root)
    manabug = ManaBugApp(gui)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    show_popup()
    root.destroy()
    start_gui()
