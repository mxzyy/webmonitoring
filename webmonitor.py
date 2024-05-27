import requests
import telebot
import logging
import json
import argparse
from datetime import datetime

sites = []
bot_token = ''
chat_id = ''
file = "status.json"
logging.basicConfig(filename='webmonitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)


def read_file(file: str):
    try:
        with open(file, 'r') as f:
            readlines = f.readlines()
            lists = [check_url(x.strip()) for x in readlines]
            return lists
    except Exception as e:
        print(e)

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
      status = loadjson[sites]['Status']
      return status
  except:
    logging.info(f"{sites} error cannot read status not found")
    return "Err"
    
def write_json(sites: str, lists: list):
    try:
        with open(file, 'r') as f:
          load = json.load(f)
        with open(file, 'w') as f:
          load[sites] = lists
          json.dump(load, f, indent=4) 
          #print(load['sites']['status'])
    except Exception as e:
        print(e)

def read_json(sites: str):
   try:
      with open(file, 'r') as f:
         load = json.load(f)
         lists = load[sites]
         return lists
   except Exception as e:
      print(e)

def send_notification(message, status, prev_status, status_code):
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
        last_status = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        write_json(message, {"Status": status,"Last Live": last_status})
        status = status + ' 🟩'
      else:
        last_status = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        write_json(message, {"Status": status,"Last Down": last_status})
        status = status + ' ❌'
      bot.send_message(chat_id, f"[{datestr}] Diinfokan Web {message:100} Status: {status:5} HTTP_Status_Code: [{status_code}] Last Live: {read_json(message)['Last Live']}")
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
      send_notification(url, status, prev_status, response.status_code)
      logging.info(f"{url} is sending requests")
    else:
      logging.info(f"{url} is down")
      status = "Down"
      prev_status = read_site_status(url)
      send_notification(url, status, prev_status, response.status_code)
  except requests.exceptions.RequestException:
    response = requests.get(url)
    logging.info(f"{url} is down Network Error")
    status = "Down (Network Error)"
    prev_status = read_site_status(url)
    write_site_status(url ,status)
    send_notification(url, status, prev_status, response.status_code)

def check_url(url: str):
    if not ('https' in url or 'http' in url):
        url = 'https://' + url
        return url
    else:
        return url

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
  try:
    for i in websites:
      sites.append(check_url(i[0]))
  except:
    print("Tidak ada domain yang diinput, mencoba membaca files")
    pass

  try:
    for j in files:
      sites.extend(read_file(j[0]))
  except:
    print("Tidak ada file yang diinput.")
    pass

  for k in sites:
    #print(k)
    check_website(k)
