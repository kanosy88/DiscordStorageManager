import requests
import time
import os
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog
from .utils import get_config

config = get_config()
max_file_size = 25000000

def uploadBlob(fileToSend:bytes, content:str, channel_id:str):
    data = {'content': content}
    files = {'content': fileToSend}
    headers = {'Authorization': config['discord_token']}

    r = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", headers=headers, data=data, files=files)

def upload_part(file_path, start, end, part, file_base, file_extension, channel_id:str):
    with open(file_path, 'rb') as file:
        file.seek(start)
        chunk_data = file.read(end - start)
        new_file_name = f"{str(part + 1)}_{file_base}{file_extension}"

        print(f'Start Uploading: {new_file_name}')
        uploadBlob(chunk_data, new_file_name, channel_id)

def upload_split_file(file_path:str, channel_id:str):
    with open(file_path, 'rb') as file:
        file_size = os.fstat(file.fileno()).st_size
        file_name = os.path.basename(file_path)
        file_base, file_extension = os.path.splitext(file_name)
        
        if file_size > max_file_size:
            number_of_parts = (file_size + max_file_size - 1) // max_file_size
            print(f"Nombre de parties: {number_of_parts}")

            with ThreadPoolExecutor(max_workers=config['send_max_worker']) as executor:
                futures = []
                for part in range(number_of_parts):
                    start = part * max_file_size
                    end = min(start + max_file_size, file_size)
                    futures.append(executor.submit(upload_part, file_path, start, end, part, file_base, file_extension, channel_id))
                
                for future in futures:
                    future.result()

def sendFileToDiscord(filePath:str, channel_id:str):
    with open(filePath, 'rb') as file:
        file_size = os.fstat(file.fileno()).st_size
        file_name = os.path.basename(filePath)
        file_base, file_extension = os.path.splitext(file_name)

        startTime = time.time()

        print(f'File Size: {round(file_size/1000/1000)}Mo')

        if file_size > max_file_size:
            upload_split_file(filePath, channel_id)
        else:
            print(f'\nStart Uploading: {file_name}')
            uploadBlob(file.read(), f'[FullFile]_{file_name}', channel_id)

        uploadTime = round(time.time() - startTime)
        print(f'\nTotal Time to upload: {uploadTime} seconds')

def main_sendFile():
    os.system('cls')

    root = tk.Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(title='Select Files to Upload')

    for file_path in file_paths:
        sendFileToDiscord(file_path, config["channel_id"])
        
    print(f"\nAll selected files are successfully uploaded to Discord.")