import os
import time
import sys
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class KudosSpreader:

    def __init__(self, username, password) -> None:

        try:

            self.start_time = time.time()
            self.driver = webdriver.Firefox()
            self.driver.get('https://www.strava.com/login')

            # Wait for the login form to be present
            wait = WebDriverWait(self.driver, 10)
            
            wait.until(EC.presence_of_element_located((By.ID, 'email'))).send_keys(username)
            
            self.driver.find_element(By.ID, 'password').send_keys(password)
            self.driver.find_element(By.ID, 'login-button').click()

            time.sleep(3)

            self.driver.get('https://www.strava.com/dashboard')

            wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'feed-ui')))
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'[data-testid="dashboard-athlete-name"]' )))
            self.athlete_name = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="dashboard-athlete-name"]')[0].text
            self.TARGET_DATE_TEXT = "10 July"

        except Exception as e:

            print('Login Error: check username and password')
            print(e)
            self.driver.quit()
            sys.exit(1)



    def get_unclicked_buttons(self,activities):

        unclicked_buttons = []
        
        for activity in activities:

            buttons = activity.find_elements(By.CSS_SELECTOR, 'button[data-testid="kudos_button"]')

            for btn in buttons:
                try:
                    # When filled_kudos is not in data-testid an exception will be raised
                    btn.find_element(By.CSS_SELECTOR, 'svg[data-testid="filled_kudos"]')
                except:
                    unclicked_buttons.append(btn)

        return unclicked_buttons


           



    def get_activities(self):

   
        activities = []
        feed_entry_elements = self.driver.find_elements(By.CSS_SELECTOR, "[id^='feed-entry']")

        for fe in feed_entry_elements:
            try:
                owner_name = fe.find_element(By.CSS_SELECTOR, '[data-testid="owners-name"]').text

                if(owner_name != self.athlete_name ):
                    activities.append(fe)
            except:
                pass

        return activities


    def run(self):

        try:

            while True:
                if(time.time()-self.start_time > 300):
                    break
                date_elements = self.driver.find_elements(By.CSS_SELECTOR, 'time[data-testid="date_at_time"]')

                unclicked_kudos = self.get_unclicked_buttons(self.get_activities())

                for button in unclicked_kudos:
                    try:
                        button.click()
                        time.sleep(2)
                    except Exception as e:
                        print(f"Error clicking button: {e}")

                footer = self.driver.find_element(By.TAG_NAME, 'footer')
                self.driver.execute_script("arguments[0].scrollIntoView(true);", footer)
                self.driver.execute_script("window.scrollBy(0, -300);")

                time.sleep(5)

                target_date_found = any(self.TARGET_DATE_TEXT in date_element.text for date_element in date_elements)

                if target_date_found:
                    break
            
        finally:
        # Close the browser
            self.driver.quit()
            pass


if __name__ == "__main__":

    load_dotenv()
    username = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')

    ks = KudosSpreader(username=username, password=password)
    ks.run()