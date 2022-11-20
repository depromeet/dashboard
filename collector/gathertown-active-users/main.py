import os
import re
import requests
import time
import undetected_chromedriver as uc

from dotenv import load_dotenv
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BOT_NAME = '대시보드 봇'


def init_driver():
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--window-size=1920x1080')
    chrome_driver = uc.Chrome(options=options)
    chrome_driver.get(os.getenv('GATHERTOWN_URL'))
    time.sleep(10)
    return chrome_driver


def login_with_email(chrome_driver):
    # input email
    id_element = chrome_driver.find_element(By.CSS_SELECTOR, '[placeholder="Enter your email address"]')
    id_element.send_keys(os.getenv('GMAIL_USER'))
    time.sleep(1)

    # sign in with email
    chrome_driver.find_element(By.XPATH, '//*[@id="app-container"]/div/div/div/div[5]/button').click()
    time.sleep(3)

    # input passcode
    passcode = get_passcode_from_email()
    if len(passcode) > 6:
        raise Exception("passcode's length must be 6.")
    index = 1
    for number in passcode:
        x_path = '//*[@id="app-container"]/div/div/div/div[4]/input[{}]'.format(index)
        id_element = chrome_driver.find_element(By.XPATH, x_path)
        id_element.send_keys(number)
        index += 1
    # docker 에서 실행하면 오래 기다려야함
    time.sleep(float(os.getenv('TIMEOUT_SECONDS_AFTER_INPUT_PASSCODE')))


def parse_participant_names(chrome_driver):
    # request permission
    buttons = chrome_driver.find_elements(By.CSS_SELECTOR, '[type="button"]')
    buttons = list(filter(lambda b: b.text == 'Request Permissions', buttons))
    if len(buttons) != 0:
        buttons[0].click()
        time.sleep(10)
    else:
        print('Request permission button not found')

    # FIXME: input value 지우고 다시 쓰면, 기존 value 값 살아남
    #   AS-IS: 'originText' -> '' -> 'originTextnewText'
    #   TO-BE: 'originText' -> '' -> 'newText'
    # input name
    name_element = chrome_driver.find_element(By.CSS_SELECTOR, '[placeholder="What\'s your name?"]')
    name_value = name_element.get_attribute('value')
    if len(name_value) == 0:
        print('name_element.value is empty.')
        name_element.send_keys(BOT_NAME)

    # join the gathering
    chrome_driver.find_element(By.XPATH, '//*[@id="app-container"]/div/div/div[3]/div[3]/div[2]/form/div/button') \
        .click()
    # docker 에서 실행하면 오래 기다려야함
    time.sleep(float(os.getenv('TIMEOUT_SECONDS_AFTER_JOIN_THE_GATHERING')))

    # get participant names
    elements = chrome_driver.find_elements(By.CSS_SELECTOR, '[tabindex="0"]')
    names = []
    for element in elements:
        text = element.get_property('innerText')
        names.append(text)
    return names


def cleanse_participant_names(participant_names):
    participant_names = filter(lambda u: u != BOT_NAME, participant_names)
    participant_names = map(extract_name_only, participant_names)
    return list(set(participant_names))


def extract_name_only(source):
    if len(source) <= 0:
        return source
    match = re.match(r'^(?:\d+m\n)?(.*)(?:\n.*)?$', source)
    if match is None:
        print('Failed to extract name. text:', source)
        return source
    return match.groups()[0]


# 안읽은 메일 중 첫번째 메일에서 passcode 읽기 시도
def get_passcode_from_email():
    from ReadEmailWithBody import ReadEmailWithBody
    from bs4 import BeautifulSoup

    reader = ReadEmailWithBody()
    response = reader.instantiate()
    if response.ok:
        unread_emails = reader.read_email(response.body)
        for each_mail in list(unread_emails):
            return BeautifulSoup(each_mail['body'], 'html.parser').select('body > b')[0].text
    else:
        print('Failed to get passcode. body:', response.body)
        return ''


def count_participants():
    result = requests.get(os.getenv('GATHERTOWN_COUNT_URL'))
    json = result.json()
    return int(json['roomCount'])


def get_active_users():
    if count_participants() == 0:
        return []
    driver = init_driver()
    login_with_email(driver)
    participant_names = parse_participant_names(driver)
    clean_participant_names = cleanse_participant_names(participant_names)
    driver.close()
    return clean_participant_names


if __name__ == '__main__':
    load_dotenv()
    users = get_active_users()
    print(users)
