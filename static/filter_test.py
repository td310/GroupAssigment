import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pymysql
from selenium.common.exceptions import NoSuchElementException

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.get("http://watchplace.great-site.net/statistic.php")
    driver.maximize_window()
    yield driver
    driver.quit()

def get_total_sales_from_db(date_from, date_to):
    try:
        connection = pymysql.connect(
            host='localhost',  
            user='root',            
            password='',              
            database='vutrudongho2',  
        )
        cursor = connection.cursor()
        
        query = f"""
        select SUM(d.Quantity) 
        from `order` as o, `order_line` as d
        where o.OrderID = d.OrderID and Date(o.OderDate) between '2022-01-01' AND '2024-12-31';
        """
        cursor.execute(query)
        result = cursor.fetchone()

        return int(result[0]) if result[0] is not None else 0  
    except Exception as e:
        print(f"Lỗi kết nối cơ sở dữ liệu: {e}")
        return 0
    finally:
        if 'connection' in locals():
            connection.close()

def test_case_01(driver):
    date_from = "01-01-2022"
    date_to = "12-31-2024"
    
    date_from_input = driver.find_element(By.NAME, "date-from")
    date_to_input = driver.find_element(By.NAME, "date-to")
    date_from_input.send_keys(date_from)
    date_to_input.send_keys(date_to)
    
    submit_button = driver.find_element(By.NAME, "submit")
    submit_button.click()
    time.sleep(2)

    total_sales_web = 0
    page_num = 1

    while True:
        sales_elements = driver.find_elements(By.XPATH, "//table[@class='statistic-product-sale__table']/tbody/tr/td[5]")
        total_sales_web += sum(int(element.text) for element in sales_elements)
        
        try:
            next_page_button = driver.find_element(By.XPATH, f"//a[text()='{page_num + 1}']")
            next_page_button.click() 
            time.sleep(2)  
            page_num += 1  
        except NoSuchElementException:
            break  
    
    total_sales_db = get_total_sales_from_db(date_from, date_to)
    assert total_sales_web == total_sales_db, f"Tổng doanh số không khớp! Web: {total_sales_web}, DB: {total_sales_db}"

#TC_ID: C_02 - Kiểm tra lọc ngày hợp lệ (Khoảng thời gian không có dữ liệu)
def test_case_02(driver):
    #tìm ngày bắt đầu và ngày kết thúc
    date_from_input = driver.find_element(By.NAME, "date-from")
    date_to_input = driver.find_element(By.NAME, "date-to")

    #nhập dữ liệu ngày bắt đầu và kết thúc
    date_from_input.send_keys("01-01-2025") 
    date_to_input.send_keys("12-31-2025'")  

    #bấm nút tìm kiếm
    submit_button = driver.find_element(By.NAME, "submit")
    submit_button.click()
    time.sleep(2)
    
    tbody = driver.find_element(By.XPATH, "//table[@class='statistic-product-sale__table']/tbody")
    no_results_message = tbody.text.strip()
    
    expected_message = "Không có kết quả thống kê nào trong khoảng thời gian này để hiển thị!"
    assert no_results_message == expected_message

#TC_ID: C_03 - Kiểm tra ngày bắt đầu lớn hơn ngày kết thúc.
def test_case_03(driver):
    #tìm ngày bắt đầu và ngày kết thúc
    date_from_input = driver.find_element(By.NAME, "date-from")
    date_to_input = driver.find_element(By.NAME, "date-to")

    #nhập dữ liệu ngày bắt đầu và kết thúc
    date_from_input.send_keys("12-31-2024")
    date_to_input.send_keys("01-01-2023")
    
    #bấm nút tìm kiếm
    submit_button = driver.find_element(By.NAME, "submit")
    submit_button.click()
    time.sleep(2)
    
    #lấy nội dung từ alert
    alert = driver.switch_to.alert
    alert_text = alert.text

    #kiểm tra alert
    expected_alert_text = "Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc!"
    assert alert_text == expected_alert_text

    #bấm vào ok trong alert
    alert.accept()

#TC_ID: C_04 - Kiểm tra không điền ngày.
def test_case_04(driver):
    #bấm nút tìm kiếm
    submit_button = driver.find_element(By.NAME, "submit")
    submit_button.click()
    
    #TH1: Không có đơn hàng vào thời gian hiện tại
    no_result_message = "Không có kết quả thống kê nào trong khoảng thời gian này để hiển thị!"
    try:
        message_element = driver.find_element(By.XPATH, "//td[@colspan='6']")
        assert message_element.text == no_result_message, \
            f"Thông báo mong đợi: '{no_result_message}', nhưng nhận được '{message_element.text}'"
    except:
        #TH2: Có đơn hàng vào thời gian hiện tại
        rows = driver.find_elements(By.XPATH, "//table[@class='statistic-product-sale__table']/tbody/tr")
        assert len(rows) > 0

#TC_ID: C_05 - Kiểm tra điền ngày bắt đầu nhưng không điền ngày kết thúc.
def test_case_05(driver):
    #nhập ngày bắt đầu
    driver.find_element(By.NAME, "date-from").send_keys("12-31-2024")

    #bấm nút tìm kiếm
    submit_button = driver.find_element(By.NAME, "submit")
    submit_button.click()
    time.sleep(2)

    rows = driver.find_elements(By.XPATH, "//table[@class='statistic-product-sale__table']/tbody/tr")
    assert len(rows) > 0
 
# TC_ID: C_06 - Kiểm tra điền ngày kết thúc nhưng không điền ngày bắt đầu.
def test_case_06(driver):

    #tìm ngày bắt đầu và ngày kết thúc
    date_to_input = driver.find_element(By.NAME, "date-to")

    #nhập dữ liệu ngày bắt đầu và kết thúc
    date_to_input.send_keys("12-31-2024")

    #bấm nút tìm kiếm
    submit_button = driver.find_element(By.NAME, "submit")
    submit_button.click()
    
    #TH1: Không có đơn hàng vào thời gian hiện tại
    no_result_message = "Không có kết quả thống kê nào trong khoảng thời gian này để hiển thị!"
    try:
        message_element = driver.find_element(By.XPATH, "//td[@colspan='6']")
        assert message_element.text == no_result_message, \
            f"Thông báo mong đợi: '{no_result_message}', nhưng nhận được '{message_element.text}'"
    except:
    #TH2: Có đơn hàng vào thời gian hiện tại
        rows = driver.find_elements(By.XPATH, "//table[@class='statistic-product-sale__table']/tbody/tr")
        assert len(rows) > 0

#TC_ID: C_07 - Kiểm tra lọc ngày với nhiều trang kết quả.
def test_case_07(driver):
    # Tìm và nhập ngày bắt đầu và ngày kết thúc
    date_from_input = driver.find_element(By.NAME, "date-from")
    date_to_input = driver.find_element(By.NAME, "date-to")
    date_from_input.send_keys("01-01-2023")
    date_to_input.send_keys("12-31-2024")

    # Bấm nút tìm kiếm
    submit_button = driver.find_element(By.NAME, "submit")
    submit_button.click()
    time.sleep(2)

    # Kiểm tra sự tồn tại của phân trang
    paging_div = driver.find_element(By.CLASS_NAME, "paging")
    paging_items = paging_div.find_elements(By.CLASS_NAME, "paging__item")

    # Kiểm tra sự tồn tại của trang 2
    page_2 = next((item for item in paging_items if item.text == "2"), None)
    assert page_2 is not None