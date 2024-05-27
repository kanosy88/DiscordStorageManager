from concurrent.futures import ThreadPoolExecutor
import json
import requests
import os
import re
import time
from .utils import get_config
import subprocess

config = get_config()

def deleteFile(file_name:str):
    file_path = f'{config["splitted_file_directory"]}/{file_name}'

    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print(f"The file '{file_path}' does not exist")

def cleanSplittedFilesCache():
    splitted_files_cache = os.listdir(config["splitted_file_directory"])

    for file in splitted_files_cache:
        deleteFile(file)

def extract_number(file_name):
    match = re.search(r'(\d+)_bigSouvenirLolHighlight\.rar', file_name)
    return int(match.group(1)) if match else float('inf')

def merge_files_from_directory(directory, output_file):
    parts = os.listdir(directory)

    parts.sort(key=extract_number)

    with open(output_file, 'wb') as merged_file:
        for part in parts:
            part_path = os.path.join(directory, part)
            with open(part_path, 'rb') as part_file:
                merged_file.write(part_file.read())

    print(f'\nOutput File: {os.path.abspath(output_file)}')
    subprocess.Popen(rf'explorer /select,"{os.path.abspath(output_file)}"')

def downloadFromLink(downloadLink:str, FileName:str):
    downloadSpeed = 2048

    with open(f'{config["splitted_file_directory"]}/{FileName}', 'wb') as file:
        response = requests.get(downloadLink, stream=True)

        for block in response.iter_content(8192):
            if not block:
                break

            file.write(block)

def fetch_all_messages(channel_id):
    messages = []
    url = f'https://discord.com/api/v9/channels/{channel_id}/messages'
    params = {'limit': 100}
    headers = {'Authorization': config['discord_token']}

    while True:
        response = requests.get(url, headers=headers, params=params)
        new_messages = json.loads(response.text)
        if not new_messages:
            break
        messages.extend(new_messages)
        params['before'] = new_messages[-1]['id']
    
    return messages

def checkFolderExist(folder_path:str) -> bool:
    return os.path.isdir(folder_path)

def InitFolder():
    if not checkFolderExist(config['output_directory']):
        os.system(f"mkdir {config['output_directory'].removeprefix("./")}")
    
    if not checkFolderExist(config['splitted_file_directory']):
        os.system(f"mkdir {config['splitted_file_directory'].removeprefix("./")}")

def main_getfile():
    os.system('cls')
    
    InitFolder()

    messages = fetch_all_messages(config['channel_id'])
    messageContents = []

    fileToSelect = input('File Name: ')

    for n_message in messages:
        if fileToSelect in n_message['content']:
            messageContents.append(n_message['content'])
    
    nbr_of_files = len(messageContents)
    print(f"Numbers of Part: {nbr_of_files}")
    
    startTime = time.time()

    with ThreadPoolExecutor(max_workers=config['get_max_worker']) as executor:
        futures = []

        for message in messages:
            messageContent = message['content']

            if fileToSelect in messageContent:
                fileDownloadUrl = message['attachments'][0]['url']
                file_name = messageContent
                
                futures.append(executor.submit(downloadFromLink, fileDownloadUrl, file_name))

        for future in futures:
            future.result()

    merge_files_from_directory(config['splitted_file_directory'], f'{config["output_directory"]}/{file_name}')
    cleanSplittedFilesCache()
    downloadTime = round(time.time() - startTime)
    print(f'\nTotal Time to download: {downloadTime} seconds')