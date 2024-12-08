import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.get("http://watchplace.great-site.net/product-manage.php")
    yield driver
    driver.quit()

def test_sidebar_responsive(driver):
    screen_sizes = [
        {"width": 1920, "height": 1080, "expected_visible": True},
        {"width": 1366, "height": 768, "expected_visible": True},
        {"width": 768, "height": 1024, "expected_visible": False},    
        {"width": 375, "height": 667, "expected_visible": False}  
    ]

    for size in screen_sizes:
        driver.set_window_size(size["width"], size["height"])
        time.sleep(2)
        sidebar = driver.find_element(By.CLASS_NAME, "sidebar")
        is_displayed = sidebar.is_displayed()
        assert is_displayed == size["expected_visible"], (
            f"Sidebar visibility mismatch at {size['width']}x{size['height']}."
        )
