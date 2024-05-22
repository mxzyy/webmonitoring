import requests
import telebot
import logging
import json
import argparse
from datetime import datetime

sites = []
bot_token = ""
chat_id = ""  
file = "status.json"
logging.basicConfig(filename='webmonitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)


def readfile(file: str):
  with open(file, 'r') as f:
    rawdata = f.readlines()
    data = [line.strip() for line in rawdata]
    return data

def check_file_handler():
  try:
    with open(file, 'x') as f:
      #print(f'file {file} created.')
      data = {"sites": "status"}
      json.dump(data, f, indent=4)
      logging.info(f"file {file} has been created.")
      pass
    return True
  except FileExistsError:
    #print(f'file {file} already exist')
    logging.error(f"file {file} already exist.")
    return False

def write_site_status(sites: str, status: str):
  try:
    with open(file, 'r') as data:
      loadjson = json.load(data)
    with open(file, 'w') as f:
      loadjson[sites] = status
      json.dump(loadjson, f, indent=4)
      #print(f"{sites} updated with {status}")
      logging.info(f"{sites} updated with status : {status}")
  except:
    #print("error write status")
    logging.error(f"{sites} error cannot write status")

def read_site_status(sites: str):
  try:
    with open(file, 'r') as f:
      loadjson = json.load(f)
      status = loadjson[sites]
      return status
  except:
    logging.info(f"{sites} error cannot read status not found")
    return "Err"
    
def send_notification(message, status, prev_status):
  now = datetime.now()
  datestr = now.strftime("%d/%m/%Y-%H:%M:%S")
  try:
    bot = telebot.TeleBot(bot_token)
    if status != prev_status:
      if 'https://' in message:
        message = message[8:]
      elif 'http://' in message:
        message = message[7:]
      if status == 'Live':
        status = status + ' 🟩'
      else:
        status = status + ' ❌'
      bot.send_message(chat_id, f"[{datestr}] Diinfokan Web {message:10}  Status: {status}")
      logging.info("Send message to Bot")
  except Exception as e:
    #print(f"Error sending notification: {e}")
    logging.error(f"Got error {e}")

def check_website(url):
  try:
    response = requests.get(url)
    if response.status_code == 200:
      logging.info(f"{url} is live")
      status = "Live"
      prev_status = read_site_status(url)
      write_site_status(url, status)
      send_notification(url, status, prev_status)
      logging.info(f"{url} is sending requests")
    else:
      logging.info(f"{url} is down")
      status = "Down"
      prev_status = read_site_status(url)
      write_site_status(url, status)
      send_notification(url, status, prev_status)
  except requests.exceptions.RequestException:
    logging.info(f"{url} is down Network Error")
    status = "Down (Network Error)"
    prev_status = read_site_status(url)
    write_site_status(url ,status)
    send_notification(url, status, prev_status)

if __name__ == "__main__":
  logging.info("Program started.")
  check_file_handler()
  parser = argparse.ArgumentParser(description='Tools untuk melakukan check terhadap website yang sedang aktif/tidak')
  parser.add_argument('-d', '--domain', type=str, action='append', nargs='*', help='Domain yang akan di-check')
  parser.add_argument('-f', '--file', type=str, action='append', nargs='*', help='Membaca teks dari file')
  args = parser.parse_args()
  websites = args.domain
  files = args.file
  args = parser.parse_args()
  for website in websites:
    if not ('https' in website[0] or 'http' in website[0]):
      website = 'https://' + website[0]
    else:
      website = website[0]
    check_website(website)
