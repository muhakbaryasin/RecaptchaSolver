import speech_recognition
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from random import randint
import pydub
import urllib
from speech_recognition import Recognizer, AudioFile
import os
from time import sleep
from models.BotDetectedException import BotDetectedException


class RecaptchaSolver(object):
    @staticmethod
    def recaptcha_checkbox_el(driver):
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        driver.switch_to.frame(frames[0])
        sleep(randint(2, 4))
        checkbox_el = driver.find_element(By.CLASS_NAME, "recaptcha-checkbox-border")
        cb_style = checkbox_el.get_attribute("style")

        if cb_style.find('display: none;') > -1:
            return

        return checkbox_el

    @staticmethod
    def recaptcha_click_checkbox(driver):
        el_ = RecaptchaSolver.recaptcha_checkbox_el(driver)
        el_.click()

    @staticmethod
    def recaptcha_check(driver):
        print('check start')
        driver.switch_to.default_content()
        frames = driver.find_elements(By.TAG_NAME, "iframe")
        sleep(randint(2, 4))
        print('check end')
        if len(frames) < 1:
            return False

        for index in range(len(frames)):
            if frames[index].get_property('title').find('recaptcha') > -1:
                return True

        return False

    @staticmethod
    def recaptcha_solve_audio(driver, first=True):
        if first:
            driver.switch_to.default_content()
            frames = driver.find_elements(By.TAG_NAME, "iframe")
            driver.switch_to.frame(frames[-1])
            driver.find_element(By.ID, "recaptcha-audio-button").click()

        driver.switch_to.default_content()

        if RecaptchaSolver.recaptcha_checkbox_el(driver) is None:
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

        if first or (verify_message is not None and (verify_message.text.find('pecahkan lebih banyak') > -1 or verify_message.text == 'Multiple correct solutions required - please solve more.')):
            pass
        else:
            print("Success ok")
            driver.switch_to.default_content()
            return

        driver.find_element(By.XPATH, "/html/body/div/div/div[3]/div/button").click()

        src = driver.find_element(By.ID, "audio-source").get_attribute("src")
        print(src)
        path = os.path.abspath(os.getcwd())
        urllib.request.urlretrieve(src, path + "/temp/audio.mp3")

        sound = pydub.AudioSegment.from_mp3(
            path + "/temp/audio.mp3").export(path + "/temp/audio.wav", format="wav")
        recognizer = Recognizer()
        recaptcha_audio = AudioFile(path + "/temp/audio.wav")

        with recaptcha_audio as source:
            audio = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio)
        except speech_recognition.UnknownValueError:
            text = 'sorry i cant hear it clearly'
        print(text)

        input_field = driver.find_element(By.ID, "audio-response")
        input_field.send_keys(text.lower())
        sleep(10)
        input_field.send_keys(Keys.ENTER)
        sleep(10)

        RecaptchaSolver.recaptcha_solve_audio(driver, first=False)

    @staticmethod
    def solve_captcha(driver):
        RecaptchaSolver.recaptcha_click_checkbox(driver)

        if RecaptchaSolver.recaptcha_check(driver):
            print('recaptcha pop-up exists')
            RecaptchaSolver.recaptcha_solve_audio(driver)
