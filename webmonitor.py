import requests
import telebot
import sys
import logging

bot_token = ""
chat_id = ""  
logging.basicConfig(filename='webmonitor.log', filemode='a', format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)

def check_prev_status():
  try:
    with open('status.txt', 'x') as f:
      logging.info("File status.txt Created")
      pass
    return True
  except FileExistsError:
    logging.error("Cannot create status.txt file already exist")
    return False

def write_status(status: str):
  with open('status.txt', 'w') as f:
    f.write(status)
    logging.info("File status.txt writed..")

def get_status():
  with open('status.txt', 'r') as f:
    status = f.read()
    return status

def send_notification(message, status, prev_status):
  try:
    bot = telebot.TeleBot(bot_token)
    if status != prev_status:
        bot.send_message(chat_id, f"{message}  Status: {status}")
        logging.info("Send message to Bot")
  except Exception as e:
    print(f"Error sending notification: {e}")
    logging.error(f"Got error {e}")

def check_website(url):
  try:
    response = requests.get(url)
    if response.status_code == 200:
      logging.info(f"{url} is live")
      status = "Live"
      prev_status = get_status()
      write_status(status)
      send_notification(url, status, prev_status)
    else:
      logging.info(f"{url} is down")
      status = "Down"
      prev_status = get_status()
      write_status(status)
      send_notification(url, status, prev_status)
  except requests.exceptions.RequestException:
    logging.info(f"{url} is down Network Error")
    status = "Down (Network Error)"
    prev_status = get_status()
    write_status(status)
    send_notification(url, status, prev_status)

if __name__ == "__main__":
  logging.info("Program started.")
  if len(sys.argv) > 1:
    websites = sys.argv[1:]
    check_prev_status()
    for website in websites:
        check_website(website)
  else:
    print("No websites provided. Usage webmonitor.py [Sites] ")