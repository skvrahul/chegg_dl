from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import json, base64
import io
from time import sleep
from PIL import Image,ImageDraw,ImageFont
import argparse
def chrome_takeFullScreenshot(driver) :
  def send(cmd, params):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({'cmd':cmd, 'params': params})
    response = driver.command_executor._request('POST', url, body)
    return response.get('value')

  def evaluate(script):
    response = send('Runtime.evaluate', {'returnByValue': True, 'expression': script})
    return response['result']['value']

  metrics = evaluate( \
    "({" + \
      "width: Math.max(window.innerWidth, document.body.scrollWidth, document.documentElement.scrollWidth)|0," + \
      "height: Math.max(innerHeight, document.body.scrollHeight, document.documentElement.scrollHeight)|0," + \
      "deviceScaleFactor: window.devicePixelRatio || 1," + \
      "mobile: typeof window.orientation !== 'undefined'" + \
    "})")
  send('Emulation.setDeviceMetricsOverride', metrics)
  screenshot = send('Page.captureScreenshot', {'format': 'png', 'fromSurface': True})
  send('Emulation.clearDeviceMetricsOverride', {})

  return base64.b64decode(screenshot['data'])

#Function to define the crop boundaries of the screenshot
def get_crop_box(im):
    width, height = im.size
    LEFT_CUT = 280
    RIGHT_CUT = 280
    TOP_CUT = 50
    BOTTOM_CUT = 50
    crop_box = (LEFT_CUT, TOP_CUT, width - RIGHT_CUT, height - BOTTOM_CUT)
    return crop_box

#Function to add text to an image
def add_text(im, text):
    width, height = im.size
    size = 50 #Size of the area containing the text 
    blank = Image.new("RGB",(width,height+size))
    blank.paste(im, (0, size))
    draw =  ImageDraw.Draw(im)
    font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 16)
    draw.text((0, 0),text,(0,0,0),font=font)
    return im

#Function to deactivate the review box at the bottom of the page
def deactivate_review_box(driver):
    rb = driver.find_element_by_css_selector('.review-box.TBS_REVIEW_BOX')
    driver.execute_script("arguments[0].style.visibility='hidden'", rb)

#Function to download every page of textbook till the end is reached
#and save each page to a file
def download_textbook(driver, URL):
    driver.get(URL)
    sleep(5)
    expand = driver.find_element_by_id('fullscreen')
    expand.click()
    while(True):
        deactivate_review_box(driver)
        pngdata  = chrome_takeFullScreenshot(driver)
        im = Image.open(io.BytesIO(pngdata))
        im = im.crop(get_crop_box(im))
        question = driver.find_element_by_class_name('title').text
        filename = './textbook/'+question+'.png'
        add_text(im, question)
        im.save(filename)
        #Finding the right arrow
        right = driver.find_element_by_css_selector('.arrow.arrow-right')
        try:
            right.click()
            #NOTE: Change the below value based on the speed of the internet connection. It should be sufficient time to fetch an entire answer
            sleep(6)
        except Exception as e:
            print('Reached end of the textbook')
            break
#Function to automatically login to Chegg(May cause issues with captcha)
def login(driver):
    USERNAME = 'username@example.com'
    PASSWORD = 'password'
    driver.get('https://www.chegg.com/login')
    login = driver.find_element_by_id('emailForSignIn')
    password = driver.find_element_by_id('passwordForSignIn') 
    login.send_keys(USERNAME) 
    password.send_keys(PASSWORD+Keys.RETURN) 

def main(args):
    capabilities = {
      'browserName': 'chrome',
      'chromeOptions':  {
        'useAutomationExtension': False,
        'args': ['--disable-infobars' ]
      }
    }
    driver = webdriver.Chrome(desired_capabilities=capabilities)

    #Uncomment the below 2 lines to login manually
    #print('Please login to chegg manually')
    #sleep(100)

    login(driver)
    URL = args['link']
    download_textbook(driver, URL)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple script to download a textbook/solutions from Chegg') 
    parser.add_argument('-l','--link', help='Link to the textbook/solution guide you would like to download from Chegg', required=True)
    args = vars(parser.parse_args())
    main(args)

