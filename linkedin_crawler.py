from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from dotenv import load_dotenv
import os
import time
import json
import random
import logging

class LinkedInCrawler:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize Chrome driver with enhanced anti-detection
        options = webdriver.ChromeOptions()
        
        # Generate random user agent
        ua = UserAgent()
        user_agent = ua.random
        self.logger.info(f"Using User Agent: {user_agent}")
        
        # Enhanced anti-detection options
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--lang=en-US')
        options.add_argument('--disable-web-security')
        
        # Add additional preferences
        options.add_experimental_option('prefs', {
            'profile.default_content_setting_values.notifications': 2,
            'intl.accept_languages': 'en-US,en',
            'profile.password_manager_enabled': False,
            'credentials_enable_service': False,
            'profile.default_content_settings.popups': 0
        })
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Add proxy support (optional - uncomment and add your proxy if needed)
        # proxy = "your-proxy-address:port"
        # options.add_argument(f'--proxy-server={proxy}')
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Additional anti-detection measures
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
        
        # Add random fingerprint
        self.driver.execute_script("""
            navigator.mediaDevices = {};
            navigator.permissions = {};
            navigator.plugins = new Array(Math.floor(Math.random() * 10) + 1).fill({});
        """)
        
    def random_sleep(self, min_time=2, max_time=5):
        """Sleep for a random amount of time between min_time and max_time"""
        time.sleep(random.uniform(min_time, max_time))

    def human_like_typing(self, element, text):
        """Type text in a human-like manner with random delays"""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))

    def scroll_random(self):
        """Scroll the page randomly to simulate human behavior"""
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        for i in range(1, random.randint(3, 7)):
            scroll_point = random.randint(100, total_height)
            self.driver.execute_script(f"window.scrollTo(0, {scroll_point});")
            self.random_sleep(1, 3)

    def login(self):
        """Login to LinkedIn with enhanced human-like behavior"""
        try:
            # Random starting point
            self.driver.get('https://www.linkedin.com')
            self.random_sleep(2, 4)
            
            # Go to login page with some randomness
            self.driver.get('https://www.linkedin.com/login')
            self.random_sleep(2, 4)
            
            # Wait for email field and enter email
            email_elem = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            self.human_like_typing(email_elem, self.email)
            self.random_sleep(1, 2)
            
            # Enter password with human-like typing
            password_elem = self.driver.find_element(By.ID, "password")
            self.human_like_typing(password_elem, self.password)
            self.random_sleep(1, 2)
            
            # Move mouse randomly before clicking (using JavaScript)
            self.driver.execute_script("""
                var button = document.querySelector("button[type='submit']");
                var rect = button.getBoundingClientRect();
                var x = rect.left + rect.width * Math.random();
                var y = rect.top + rect.height * Math.random();
                var clickEvent = new MouseEvent('click', {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: x,
                    clientY: y
                });
                button.dispatchEvent(clickEvent);
            """)
            
            # Wait for login to complete with random timing
            self.random_sleep(4, 7)
            
            # Verify login success with multiple selectors
            try:
                success_selectors = [
                    "div.feed-identity-module",    # Feed page
                    "div.search-global-typeahead", # Search bar
                    "img.global-nav__me-photo",    # Profile photo in nav
                    "div.global-nav__me",          # Profile section in nav
                    ".share-box-feed-entry__avatar", # Post box
                    ".feed-shared-actor__avatar",  # Feed item
                ]
                
                for selector in success_selectors:
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        self.logger.info(f"Successfully logged in (verified with {selector})")
                        return True
                    except TimeoutException:
                        continue
                
                # If we couldn't find any known elements, check if we're still on login page
                if "login" not in self.driver.current_url:
                    self.logger.info("Login likely successful (no longer on login page)")
                    return True
                else:
                    self.logger.error("Still on login page - login failed")
                    return False
                    
            except Exception as e:
                self.logger.warning(f"Login verification encountered an error: {str(e)}")
                # If we're no longer on the login page, assume success
                if "login" not in self.driver.current_url:
                    self.logger.info("Continuing despite verification error (no longer on login page)")
                    return True
                return False
            
        except TimeoutException as e:
            self.logger.error(f"Timeout while trying to log in: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {str(e)}")
            return False
    
    def get_profile_data(self, profile_url):
        """Extract data from a LinkedIn profile using exact selectors"""
        try:
            self.logger.info(f"Navigating to profile: {profile_url}")
            self.driver.get(profile_url)
            self.random_sleep(5, 8)

            profile_data = {}

            # 1. Get Basic Information
            basic_info = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.bg-color-background-container.mx-2.mt-2.mb-1"))
            )

            # Name and Title
            try:
                name = basic_info.find_element(By.CSS_SELECTOR, "h1.text-color-text.heading-large").text.strip()
                profile_data['name'] = name
                self.logger.info(f"Found name: {name}")

                title = basic_info.find_element(By.CSS_SELECTOR, "div.body-small.text-color-text span[dir='ltr']").text.strip()
                profile_data['title'] = title
                self.logger.info(f"Found title: {title}")
            except NoSuchElementException as e:
                self.logger.error(f"Error finding basic info: {str(e)}")
                return None

            # 2. Get Education
            try:
                education_section = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "section.education-container"))
                )
                education_items = education_section.find_elements(By.CSS_SELECTOR, "ol > li.entity-lockup")
                profile_data['education'] = []

                for item in education_items:
                    education_info = {}
                    try:
                        # School name
                        school = item.find_element(By.CSS_SELECTOR, "div.list-item-heading span[dir='ltr']").text.strip()
                        education_info['school'] = school

                        # Degree and Field
                        details = item.find_elements(By.CSS_SELECTOR, "div.body-small.text-color-text span[dir='ltr']")
                        if len(details) > 0:
                            education_info['degree'] = details[0].text.strip()
                        if len(details) > 1:
                            education_info['field'] = details[1].text.strip()

                        # Duration
                        years = item.find_elements(By.CSS_SELECTOR, "div.body-small.text-color-text-low-emphasis span.body-small")
                        if len(years) >= 2:
                            education_info['duration'] = f"{years[0].text.strip()} - {years[1].text.strip()}"

                        profile_data['education'].append(education_info)
                    except NoSuchElementException:
                        continue

            except Exception as e:
                self.logger.warning(f"Error getting education: {str(e)}")
                profile_data['education'] = []

            # 3. Get Skills
            try:
                skills_section = self.driver.find_element(By.CSS_SELECTOR, "section.skills-container")
                skills = skills_section.find_elements(By.CSS_SELECTOR, "li.skill-item span[dir='ltr']")
                profile_data['skills'] = [skill.text.strip() for skill in skills]
                self.logger.info(f"Found {len(profile_data['skills'])} skills")
            except NoSuchElementException:
                profile_data['skills'] = []

            # 4. Get Experience
            try:
                exp_section = self.driver.find_element(By.CSS_SELECTOR, "section.experience-container")
                exp_items = exp_section.find_elements(By.CSS_SELECTOR, "li.sub-group")
                profile_data['experience'] = []

                for item in exp_items:
                    try:
                        exp_info = {}
                        # Role
                        role = item.find_element(By.CSS_SELECTOR, "div.body-medium-bold span[dir='ltr']").text.strip()
                        exp_info['role'] = role

                        # Company
                        company = item.find_element(By.CSS_SELECTOR, "div.body-small span[dir='ltr']").text.strip()
                        exp_info['company'] = company

                        # Duration
                        duration = item.find_elements(By.CSS_SELECTOR, "div.body-small > span.body-small")
                        if len(duration) >= 2:
                            exp_info['duration'] = f"{duration[0].text.strip()} - {duration[1].text.strip()}"

                        # Location
                        location = item.find_element(By.CSS_SELECTOR, "div.text-xs span[dir='ltr']").text.strip()
                        exp_info['location'] = location

                        profile_data['experience'].append(exp_info)
                    except NoSuchElementException as e:
                        self.logger.warning(f"Error processing experience item: {str(e)}")
                        continue

            except NoSuchElementException:
                profile_data['experience'] = []

            return profile_data

        except TimeoutException as e:
            self.logger.error(f"Timeout while extracting profile data: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error while extracting profile data: {str(e)}")
            return None
            
            # Simulate random mouse movements
            self.driver.execute_script("""
                document.addEventListener('mousemove', function(e) {
                    window.lastMouseX = e.clientX;
                    window.lastMouseY = e.clientY;
                });
            """)
            
            profile_data = {}
            
            # Initial random scroll
            self.scroll_random()
            
            # Check for verification page or other barriers
            if "checkpoint" in self.driver.current_url or "authwall" in self.driver.current_url:
                self.logger.error("Hit LinkedIn verification page - session might need manual verification")
                return None

            # Ensure we're actually on a profile page
            if "/in/" not in self.driver.current_url:
                self.logger.error("Not on a profile page - might have been redirected")
                return None

            profile_data = {}

            # Get basic info (name, title, etc.)
            basic_info = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.bg-color-background-container.mx-2.mt-2.mb-1"))
            )

            # Get name
            try:
                name = basic_info.find_element(By.CSS_SELECTOR, "h1.text-color-text.heading-large").text.strip()
                profile_data['name'] = name
                self.logger.info("Found name: " + name)
            except NoSuchElementException:
                self.logger.error("Could not find name")
                return None

            # Get title
            try:
                title = basic_info.find_element(By.CSS_SELECTOR, "div.body-small.text-color-text span[dir='ltr']").text.strip()
                profile_data['title'] = title
            except NoSuchElementException:
                profile_data['title'] = None
            
            retry_count = 0
            while retry_count < 3:
                try:
                    # Try each selector
                    for selector in name_selectors:
                        try:
                            element = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                            )
                            name = element.text.strip()
                            if name:
                                profile_data['name'] = name
                                self.logger.info(f"Successfully found name using selector: {selector}")
                                break
                        except:
                            continue
                    
                    # If we found a name, break the retry loop
                    if 'name' in profile_data and profile_data['name']:
                        break
                        
                    # If we didn't find a name, try refreshing
                    retry_count += 1
                    if retry_count < 3:
                        self.logger.warning(f"Name not found, attempt {retry_count + 1}/3")
                        self.random_sleep(3, 5)
                        self.driver.refresh()
                        self.random_sleep(3, 5)
                    else:
                        self.logger.error("Failed to get name after 3 retries")
                        return None
                        
                except Exception as e:
                    retry_count += 1
                    self.logger.error(f"Error during name extraction: {str(e)}")
                    if retry_count == 3:
                        return None
                    self.random_sleep(3, 5)
                    self.driver.refresh()
                    self.random_sleep(3, 5)
            
            # Random pause after getting name
            self.random_sleep(1, 3)
            
            # Get basic profile information
            try:
                # Get title
                title_element = basic_info_container.find_element(By.CSS_SELECTOR, "div.body-small.text-color-text span[dir='ltr']")
                profile_data['title'] = title_element.text.strip()
                self.logger.info("Successfully found title")
            except NoSuchElementException:
                profile_data['title'] = None
                self.logger.warning("Title not found")

            # Get Education Details
            try:
                education_section = self.driver.find_element(By.CSS_SELECTOR, "section.education-container")
                education_items = education_section.find_elements(By.CSS_SELECTOR, "ol > li")
                profile_data['education'] = []
                
                for item in education_items:
                    try:
                        education_info = {
                            'school': item.find_element(By.CSS_SELECTOR, "div.list-item-heading span[dir='ltr']").text.strip(),
                            'degree': None,
                            'field': None,
                            'duration': None
                        }
                        
                        # Get degree and field
                        degree_field = item.find_elements(By.CSS_SELECTOR, "div.body-small.text-color-text span[dir='ltr']")
                        if len(degree_field) >= 1:
                            education_info['degree'] = degree_field[0].text.strip()
                        if len(degree_field) >= 2:
                            education_info['field'] = degree_field[1].text.strip()
                        
                        # Get duration
                        duration_elements = item.find_elements(By.CSS_SELECTOR, "div.body-small.text-color-text-low-emphasis span.body-small")
                        if len(duration_elements) >= 2:
                            start_year = duration_elements[0].text.strip()
                            end_year = duration_elements[1].text.strip()
                            education_info['duration'] = f"{start_year} - {end_year}"
                        
                        profile_data['education'].append(education_info)
                    except Exception as e:
                        self.logger.warning(f"Error processing education item: {str(e)}")
                        continue
                
            except NoSuchElementException:
                profile_data['education'] = []
                self.logger.warning("Education section not found")

            try:
                # Get location and connections
                location_connections = basic_info_container.find_element(
                    By.CSS_SELECTOR,
                    "div.body-small.text-color-text-low-emphasis"
                )
                location_text = location_connections.text.strip()
                
                # Split the text by the dot separator
                parts = [part.strip() for part in location_text.split("·")]
                
                profile_data['location'] = parts[0] if parts else None
                # Extract connections number if available
                for part in parts:
                    if "connections" in part.lower():
                        profile_data['connections'] = part.strip()
                        break
                else:
                    profile_data['connections'] = None
                
                self.logger.info("Successfully found location and connections")
            except NoSuchElementException:
                profile_data['location'] = None
                profile_data['connections'] = None
                self.logger.warning("Location/Connections information not found")
            
            # Get Skills
            try:
                skills_section = self.driver.find_element(By.CSS_SELECTOR, "section.skills-container")
                skill_items = skills_section.find_elements(By.CSS_SELECTOR, "li.skill-item span[dir='ltr']")
                profile_data['skills'] = [skill.text.strip() for skill in skill_items]
                self.logger.info(f"Found {len(profile_data['skills'])} skills")
            except NoSuchElementException:
                profile_data['skills'] = []
                self.logger.warning("Skills section not found")
                
            # Get Experience
            try:
                experience_section = self.driver.find_element(By.CSS_SELECTOR, "section.experience-container")
                experience_items = experience_section.find_elements(By.CSS_SELECTOR, "ol > li")
                profile_data['experience'] = []
                
                for item in experience_items:
                    try:
                        # Find all sub-groups within the experience item
                        sub_groups = item.find_elements(By.CSS_SELECTOR, "ul > li.sub-group")
                        
                        for sub_group in sub_groups:
                            experience_info = {}
                            
                            # Get role
                            try:
                                role_elem = sub_group.find_element(By.CSS_SELECTOR, "div.body-medium-bold span[dir='ltr']")
                                experience_info['role'] = role_elem.text.strip()
                            except NoSuchElementException:
                                experience_info['role'] = None
                            
                            # Get company
                            try:
                                company_elem = sub_group.find_element(By.CSS_SELECTOR, "div.body-small span[dir='ltr']")
                                experience_info['company'] = company_elem.text.strip()
                            except NoSuchElementException:
                                experience_info['company'] = None
                            
                            # Get duration and time period
                            try:
                                duration_elements = sub_group.find_elements(By.CSS_SELECTOR, "div.body-small > span.body-small")
                                dates = [elem.text.strip() for elem in duration_elements if elem.text.strip()]
                                
                                if len(dates) >= 2:
                                    experience_info['duration'] = f"{dates[0]} - {dates[1]}"
                                    
                                # Get total time (e.g., "7 mos")
                                total_time = sub_group.find_element(By.CSS_SELECTOR, "span.dot-separator + span")
                                experience_info['total_time'] = total_time.text.strip()
                            except NoSuchElementException:
                                experience_info['duration'] = None
                                experience_info['total_time'] = None
                            
                            # Get location
                            try:
                                location_elem = sub_group.find_element(By.CSS_SELECTOR, "div.text-xs span[dir='ltr']")
                                experience_info['location'] = location_elem.text.strip()
                            except NoSuchElementException:
                                experience_info['location'] = None
                            
                            profile_data['experience'].append(experience_info)
                    except Exception as e:
                        self.logger.warning(f"Error processing experience item: {str(e)}")
                        continue
                        
            except NoSuchElementException:
                profile_data['experience'] = []
                self.logger.warning("Experience section not found")
            
            # Get experience with enhanced scrolling and waiting
            profile_data['experience'] = []
            try:
                # Scroll to experience section
                exp_section = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "experience"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", exp_section)
                self.random_sleep(2, 4)

                # Click "Show all experiences" if available
                try:
                    show_more = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='experiences']")
                    self.driver.execute_script("arguments[0].click();", show_more)
                    self.random_sleep(2, 4)
                except NoSuchElementException:
                    pass

                exp_items = exp_section.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")
                
                for item in exp_items:
                    try:
                        # Scroll to each item smoothly
                        self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", item)
                        self.random_sleep(0.5, 1.5)
                        
                        selectors = {
                            'role': ["span.mr1.t-bold", ".experience-item__title"],
                            'company': [".t-normal.t-black", ".experience-item__company"],
                            'duration': [".t-normal.t-black--light", ".experience-item__duration"]
                        }
                        
                        experience_data = {}
                        for field, selector_list in selectors.items():
                            for selector in selector_list:
                                try:
                                    experience_data[field] = item.find_element(By.CSS_SELECTOR, selector).text
                                    break
                                except NoSuchElementException:
                                    continue
                            
                            if field not in experience_data:
                                experience_data[field] = None
                        
                        # Try to get description if available
                        try:
                            description = item.find_element(By.CSS_SELECTOR, ".show-more-less-text").text
                            experience_data['description'] = description
                        except NoSuchElementException:
                            experience_data['description'] = None
                        
                        profile_data['experience'].append(experience_data)
                        
                    except Exception as e:
                        self.logger.warning(f"Error processing experience item: {str(e)}")
                        continue
                        
            except Exception as e:
                self.logger.warning(f"Error processing experience section: {str(e)}")
                pass
            
            # Get skills with enhanced interaction
            profile_data['skills'] = []
            try:
                # Scroll to skills section smoothly
                skills_section = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "skills"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", skills_section)
                self.random_sleep(2, 4)

                # Try different methods to expand skills
                skill_expanders = [
                    "div#skills + div + div",
                    "button[aria-label*='skills']",
                    ".skills-section-expand"
                ]

                for expander in skill_expanders:
                    try:
                        skills_button = self.driver.find_element(By.CSS_SELECTOR, expander)
                        self.driver.execute_script("arguments[0].click();", skills_button)
                        self.random_sleep(2, 4)
                        break
                    except NoSuchElementException:
                        continue

                # Try different skill selectors
                skill_selectors = [
                    "span.mr1.t-bold",
                    ".skill-category-entity__name",
                    ".pv-skill-category-entity__name-text"
                ]

                for selector in skill_selectors:
                    try:
                        skill_items = skills_section.find_elements(By.CSS_SELECTOR, selector)
                        if skill_items:
                            profile_data['skills'] = []
                            for skill in skill_items:
                                # Scroll to each skill smoothly
                                self.driver.execute_script(
                                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                                    skill
                                )
                                self.random_sleep(0.2, 0.5)
                                skill_text = skill.text.strip()
                                if skill_text and skill_text not in profile_data['skills']:
                                    profile_data['skills'].append(skill_text)
                            break
                    except Exception as e:
                        self.logger.warning(f"Error with skill selector {selector}: {str(e)}")
                        continue

            except Exception as e:
                self.logger.warning(f"Error processing skills section: {str(e)}")
                pass

            # Final random scroll
            self.scroll_random()
            
        except TimeoutException as e:
            self.logger.error(f"Timeout while extracting profile data: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error while extracting profile data: {str(e)}")
            return None
        
        return profile_data
    
    def close(self):
        """Close the browser"""
        self.driver.quit()

def save_to_json(data, filename):
    """Save the profile data to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def main():
    # Create crawler instance
    crawler = LinkedInCrawler()
    
    try:
        # Login to LinkedIn with retry
        max_retries = 3
        login_success = False
        
        for attempt in range(max_retries):
            if crawler.login():
                login_success = True
                break
            else:
                print(f"Login attempt {attempt + 1} failed, {'retrying...' if attempt < max_retries - 1 else 'giving up.'}")
                time.sleep(2)
        
        if not login_success:
            print("Failed to login after multiple attempts")
            crawler.close()
            return
        
        # Add extra delay after successful login
        time.sleep(5)
        
        # Get profile URL from user
        while True:
            try:
                profile_url = input("\nEnter LinkedIn profile URL (or 'quit' to exit): ").strip()
                
                if profile_url.lower() == 'quit':
                    break
                    
                if not profile_url.startswith('https://www.linkedin.com/'):
                    print("Please enter a valid LinkedIn URL starting with 'https://www.linkedin.com/'")
                    continue
                
                print("\nStarting profile extraction...")
                profile_data = crawler.get_profile_data(profile_url)
                
                if profile_data:
                    # Save to JSON file
                    output_file = f"profile_{int(time.time())}.json"
                    save_to_json(profile_data, output_file)
                    print(f"\nSuccess! Profile data saved to {output_file}")
                    
                    # Ask if user wants to extract another profile
                    if input("\nWould you like to extract another profile? (y/n): ").lower() != 'y':
                        break
                else:
                    print("\nFailed to get profile data. Would you like to try another profile?")
                    if input("Continue? (y/n): ").lower() != 'y':
                        break
                        
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                break
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                if input("Would you like to try again? (y/n): ").lower() != 'y':
                    break
    
    finally:
        # Always close the browser
        print("\nClosing browser...")
        crawler.close()

if __name__ == "__main__":
    main()