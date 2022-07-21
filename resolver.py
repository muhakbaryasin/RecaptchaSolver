from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from models.RecaptchaSolver import RecaptchaSolver
from time import sleep


if __name__ == "__main__":
	driver = webdriver.Chrome("./driver/chromedriver")
	#seleniumwire_options=proxy_option_)
	driver.get('https://www.google.com/recaptcha/api2/demo')
	RecaptchaSolver.solve_captcha(driver)

	button_submit = driver.find_element(By.XPATH, '//*[@id="recaptcha-demo-submit"]')
	button_submit.click()

	try:
		sleep(120)
	except KeyboardInterrupt:
		driver.quit()

	driver.quit()
