"""
Integration tests for the frontend authentication flow.
These tests simulate user interactions with the sign-in form components.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os


class TestSignInForm:
    """
    Test suite for the sign-in form component.
    """

    @classmethod
    def setup_class(cls):
        """Set up the test environment."""
        # Use Chrome driver (make sure chromedriver is in PATH)
        cls.driver = webdriver.Chrome()
        cls.wait = WebDriverWait(cls.driver, 10)

        # Get the base URL from environment or use default
        cls.base_url = os.getenv('NEXTJS_TEST_URL', 'http://localhost:3000')

    @classmethod
    def teardown_class(cls):
        """Clean up after tests."""
        cls.driver.quit()

    def setup_method(self):
        """Set up before each test method."""
        # Navigate to the sign-in page
        self.driver.get(f"{self.base_url}/auth/sign-in")

    def test_render_signin_form(self):
        """Test that the sign-in form renders correctly."""
        # Wait for the email input field to be present
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        # Verify the email input field exists
        assert email_input is not None

        # Verify the password input field exists
        password_input = self.driver.find_element(By.NAME, "password")
        assert password_input is not None

        # Verify the submit button exists
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        assert submit_button is not None

    def test_signin_with_valid_credentials(self):
        """Test signing in with valid credentials."""
        # Wait for the email input field to be present
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        # Enter valid email
        email_input.send_keys("test@example.com")

        # Enter valid password
        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys("validpassword123")

        # Submit the form
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Wait for redirect to dashboard or home page
        self.wait.until(EC.url_contains("/dashboard"))

        # Verify that the user is redirected to the correct page
        assert "/dashboard" in self.driver.current_url

    def test_signin_with_invalid_credentials(self):
        """Test signing in with invalid credentials."""
        # Wait for the email input field to be present
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        # Enter invalid email
        email_input.send_keys("invalid@example.com")

        # Enter invalid password
        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys("wrongpassword")

        # Submit the form
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Wait for error message to appear
        error_message = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "text-red-800"))
        )

        # Verify that an error message is displayed
        assert error_message.text != ""

    def test_signin_with_missing_fields(self):
        """Test signing in with missing required fields."""
        # Wait for the submit button to be present
        submit_button = self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )

        # Try to submit without entering email or password
        submit_button.click()

        # Wait for error message to appear
        error_message = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "text-red-800"))
        )

        # Verify that an error message is displayed
        assert error_message.text != ""

    def test_navigate_to_signup_page(self):
        """Test navigating from sign-in to sign-up page."""
        # Wait for the sign-up link to be present
        signup_link = self.wait.until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Sign up"))
        )

        # Click the sign-up link
        signup_link.click()

        # Wait for navigation to sign-up page
        self.wait.until(EC.url_contains("/auth/sign-up"))

        # Verify that the user is on the sign-up page
        assert "/auth/sign-up" in self.driver.current_url


class TestSignUpForm:
    """
    Test suite for the sign-up form component.
    """

    @classmethod
    def setup_class(cls):
        """Set up the test environment."""
        # Use Chrome driver (make sure chromedriver is in PATH)
        cls.driver = webdriver.Chrome()
        cls.wait = WebDriverWait(cls.driver, 10)

        # Get the base URL from environment or use default
        cls.base_url = os.getenv('NEXTJS_TEST_URL', 'http://localhost:3000')

    @classmethod
    def teardown_class(cls):
        """Clean up after tests."""
        cls.driver.quit()

    def setup_method(self):
        """Set up before each test method."""
        # Navigate to the sign-up page
        self.driver.get(f"{self.base_url}/auth/sign-up")

    def test_render_signup_form(self):
        """Test that the sign-up form renders correctly."""
        # Wait for the email input field to be present
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        # Verify the email input field exists
        assert email_input is not None

        # Verify the password input field exists
        password_input = self.driver.find_element(By.NAME, "password")
        assert password_input is not None

        # Verify the confirm password input field exists
        confirm_password_input = self.driver.find_element(By.NAME, "confirmPassword")
        assert confirm_password_input is not None

        # Verify the submit button exists
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        assert submit_button is not None

    def test_signup_with_valid_credentials(self):
        """Test signing up with valid credentials."""
        # Wait for the email input field to be present
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        # Enter valid email
        email_input.send_keys(f"newuser{int(time.time())}@example.com")

        # Enter valid password
        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys("SecurePass123!")

        # Enter confirm password
        confirm_password_input = self.driver.find_element(By.NAME, "confirmPassword")
        confirm_password_input.send_keys("SecurePass123!")

        # Submit the form
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Wait for redirect to dashboard or home page
        self.wait.until(EC.url_contains("/dashboard"))

        # Verify that the user is redirected to the correct page
        assert "/dashboard" in self.driver.current_url

    def test_signup_with_mismatched_passwords(self):
        """Test signing up with mismatched passwords."""
        # Wait for the email input field to be present
        email_input = self.wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )

        # Enter email
        email_input.send_keys(f"newuser{int(time.time())}@example.com")

        # Enter password
        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys("SecurePass123!")

        # Enter different confirm password
        confirm_password_input = self.driver.find_element(By.NAME, "confirmPassword")
        confirm_password_input.send_keys("DifferentPass456!")

        # Submit the form
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()

        # Wait for error message to appear
        error_message = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "text-red-800"))
        )

        # Verify that an error message about password mismatch is displayed
        assert "match" in error_message.text.lower()


if __name__ == "__main__":
    pytest.main([__file__])