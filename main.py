import os
import locale
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from urllib.parse import urlparse

import subprocess

#Get current directory
path = os.path.realpath(__file__+ "/..") + "/"

#Read all links in list.txt
link_list = []
list_file = open(path + 'list.txt', 'r')
while True:
    line = list_file.readline()
    
    #EOF
    if not line:
        break
    
    print(line)
    link_list.append(line)
list_file.close()
print("There are total", len(link_list), "links")

#start chrome first
print("Booting up browser")
driver = webdriver.Chrome()

#Ask ITSC
print('ISTC ID: ', end='')
istc_id = input()
print('password: ', end='')
password = input()

#Start Looping the link
first_time = True
for i in range(len(link_list)):
    print("Now getting link", i, ",", link_list[i])
    driver.get(link_list[i])
    time.sleep(3)

    if(first_time):
        #Login
        driver.find_element(By.NAME, 'loginfmt').send_keys(istc_id)
        driver.find_element(By.ID, "idSIButton9").click()
        time.sleep(1.5)
        driver.find_element(By.NAME, 'passwd').send_keys(password)
        driver.find_element(By.ID, "idSIButton9").click()
        time.sleep(7)

        #Duo
        while(True):
            domain = urlparse(driver.current_url).netloc
            if domain == 'api-84f626fe.duosecurity.com':
                #Check expired
                print("Waiting for DUO")
                time.sleep(1)
                if len(driver.find_elements(By.ID, 'error-view-header-text')) != 0:
                    print('Expired')
                    driver.refresh()
                elif len(driver.find_elements(By.ID, 'trust-browser-button')) != 0:
                    print("trust")
                    driver.find_element(By.ID, "trust-browser-button").click()
                    break

                #start over when domain still duo
                continue

            break
        print("DUO finish")
        time.sleep(10)

        #Login End
        first_time = False

    #Get Link
    JS_get_network_requests = "var performance = window.performance || window.msPerformance || window.webkitPerformance || {}; var network = performance.getEntries() || {}; for(let i = 0; i < network.length; i++) { if(network[i].initiatorType == 'xmlhttprequest') { if(network[i].name.includes('m3u8') && !network[i].name.includes('chunklist')) { return network[i].name; } } }"
    network_requests = driver.execute_script(JS_get_network_requests)

    #Start download
    command = 'yt-dlp ' + '\'' + network_requests + '\' -o \'' + str((i+1)) + '.mp4\''
    process = subprocess.run(command, shell=True)
    print("Finish")

driver.close()