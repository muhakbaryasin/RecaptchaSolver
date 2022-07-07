from seleniumwire import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
from random import randint
import pydub
import urllib
from speech_recognition import Recognizer, AudioFile
import os
import pdb
import json
import csv


class BotDetectedException(Exception):
	pass


def recaptcha_checkbox_el(driver):
	frames = driver.find_elements(By.TAG_NAME, "iframe")
	driver.switch_to.frame(frames[0])
	sleep(randint(2, 4))
	checkbox_el = driver.find_element(By.CLASS_NAME, "recaptcha-checkbox-border")
	cb_style = checkbox_el.get_attribute("style")
	
	if cb_style.find('display: none;') > -1:
		return
	
	return checkbox_el


def recaptcha_click_checkbox(driver):
	el_ = recaptcha_checkbox_el(driver)
	el_.click()

def recaptcha_check(driver):
	print('check start')
	driver.switch_to.default_content()
	frames = driver.find_element(By.XPATH,
	    "/html/body/div[2]/div[4]").find_elements(By.TAG_NAME, "iframe")
	sleep(randint(2, 4))
	print('check end')
	
	if len(frames) < 1:
		return False
	
	for index in range(len(frames)):
		if frames[index].get_property('title').find('recaptcha') > -1:
			return True
		
	return False

def recaptcha_solve_audio(driver, first=True):
	if first:
		driver.switch_to.default_content()
		frames = driver.find_elements(By.TAG_NAME, "iframe")
		driver.switch_to.frame(frames[-1])
		driver.find_element(By.ID, "recaptcha-audio-button").click()
		
	driver.switch_to.default_content()
	
	if recaptcha_checkbox_el(driver) is None:
		print("Success")
		driver.switch_to.default_content()
		return
	
	driver.switch_to.default_content()
	
	frames = driver.find_elements(By.TAG_NAME, "iframe")
	driver.switch_to.frame(frames[-1])
	sleep(randint(2, 4))
	
	try:
		error_text_el = driver.find_element(By.CLASS_NAME, 'rc-doscaptcha-header-text')
	except NoSuchElementException:
		error_text_el = None
	
	if error_text_el is not None and error_text_el.text == 'Try again later':
		driver.quit()
		raise BotDetectedException('Bot detected')
	
	verify_message = None
	
	try:
		verify_message = driver.find_element(By.XPATH, '/html/body/div/div/div[1]')
	except:
		pass
	
	if first or (verify_message is not None and verify_message.text ==  'Multiple correct solutions required - please solve more.'):
		pass
	else:
		print("Success")
		driver.switch_to.default_content()
		return
	
	
	driver.find_element(By.XPATH, "/html/body/div/div/div[3]/div/button").click()
	
	
	src = driver.find_element(By.ID, "audio-source").get_attribute("src")
	print(src)
	path = os.path.abspath(os.getcwd())
	urllib.request.urlretrieve(src, path+"/audio.mp3")

	sound = pydub.AudioSegment.from_mp3(
		path+"/audio.mp3").export(path+"/audio.wav", format="wav")
	recognizer = Recognizer()
	recaptcha_audio = AudioFile(path+"/audio.wav")

	with recaptcha_audio as source:
		audio = recognizer.record(source)

	text = recognizer.recognize_google(audio, language="de-DE")
	print(text)

	inputfield = driver.find_element(By.ID, "audio-response")
	inputfield.send_keys(text.lower())
	sleep(10)
	inputfield.send_keys(Keys.ENTER)
	sleep(10)
	
	recaptcha_solve_audio(driver, first=False)
	


if __name__ == "__main__":
	driver = None
	
	while True:
		driver = webdriver.Chrome("./chromedriver")
		driver.get('https://www.google.com/recaptcha/api2/demo')
		recaptcha_click_checkbox(driver)
		
		if recaptcha_check(driver):
			print('recaptcha pop-up exists')
			
			try:
				recaptcha_solve_audio(driver)
			except BotDetectedException:
				print('Bot detected')
				sleep(10)
				continue
		break
	
	button_search = driver.find_element(By.XPATH, '//*[@id="recaptcha-demo-submit"]')
	button_search.click()
	sleep(10)
	input('will exit now! press enter')
	driver.quit()
