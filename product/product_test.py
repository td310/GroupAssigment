import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.alert import Alert
import time
import pymysql
from selenium.common.exceptions import NoSuchElementException

@pytest.fixture
def driver():
    driver = webdriver.Chrome()
    driver.get("http://watchplace.great-site.net/product-manage.php")
    driver.maximize_window()
    yield driver
    driver.quit()

class ProductForm:
    def __init__(self, driver):
        self.driver = driver
        self.btn_add = driver.find_element(By.CLASS_NAME, "container-product-header__insert")
        self.brand_dropdown = Select(driver.find_element(By.ID, "modal-product-container-content__brand"))
        self.product_name_input = driver.find_element(By.ID, "modal-product-container-content__product-name")
        self.image_input = driver.find_element(By.ID, "modal-product-container-content__product-img")
        self.model_dropdown = Select(driver.find_element(By.ID, "modal-product-container-content__model"))
        self.color_dropdown = Select(driver.find_element(By.ID, "modal-product-container-content__color"))
        self.gender_dropdown = Select(driver.find_element(By.ID, "modal-product-container-content__gender"))
        self.import_price_input = driver.find_element(By.ID, "modal-product-container-content__import-price")
        self.sell_price_input = driver.find_element(By.ID, "modal-product-container-content__price-to-sell")
        self.discount_input = driver.find_element(By.ID, "modal-product-container-content__discount")
        self.description_input = driver.find_element(By.ID, "modal-product-container-content__desc")
        self.submit_button = driver.find_element(By.XPATH, "//button[@class='modal-product-container__btn insert']")
        self.submit_edit_button = driver.find_element(By.XPATH, "//button[@class='modal-product-container__btn edit']")
        self.search_input = driver.find_element(By.NAME,"product-search")
        self.search_btn = driver.find_element(By.NAME,"button-search")


    def open_form(self):
        self.btn_add.click()

    def click_edit_button(self, product_id):
        edit_button = self.driver.find_element(By.XPATH, f"//span[@onclick=\"displayEditModal('{product_id}');\"]")
        edit_button.click()

    def clear_and_fill_input(self, element, value):
        element.clear()
        element.send_keys(value)

    def click_search_btn(self):
        self.search_btn.click()

    def fill_form(self, brand, product_name, image_path, model, color, gender, import_price, sell_price, discount, description):
        self.brand_dropdown.select_by_visible_text(brand)
        self.clear_and_fill_input(self.product_name_input, product_name)
        self.image_input.send_keys(image_path)
        self.model_dropdown.select_by_visible_text(model)
        self.color_dropdown.select_by_visible_text(color)
        self.gender_dropdown.select_by_visible_text(gender)
        self.clear_and_fill_input(self.import_price_input, import_price)
        self.clear_and_fill_input(self.sell_price_input, sell_price)
        self.clear_and_fill_input(self.discount_input, discount)
        self.clear_and_fill_input(self.description_input, description)


    def submit_form(self, action="insert"):
        if action == "insert":
            self.submit_button.click()
        elif action == "edit":
            self.submit_edit_button.click()
        else:
            raise ValueError("Error")

def get_product_from_db():
    connection = pymysql.connect(
        host='localhost',  
        user='root',            
        password='',               
        database='vutrudongho2',  
    )
    with connection.cursor() as cursor:
        query = """SELECT ProductName,Model,Color,b.BrandName , Gender
        from `brand` as b, `product` as p
        where b.BrandID = p.BrandID """
        cursor.execute(query)
        result = cursor.fetchall()
        product = [(row[0], row[1], row[2], row[3], row[4]) for row in result]
        return product


# TC01: Kiểm tra thêm sản phẩm thành công.
def test_case_01(driver):
    form = ProductForm(driver)
    form.open_form()
    product_name = "Citizen Nam – Eco-Drive (Năng Lượng Ánh Sáng) – Kính Sapphire – Dây Da (AR1113-12A) Được xếp hạng"

    form.fill_form(
        brand="Casio",
        product_name=product_name,
        image_path="D:/per3.jpg",
        model="Đồng hồ thông minh",
        color="Bạc",
        gender="Nam",
        import_price="12000000",
        sell_price="13000000",
        discount="10",
        description="Đồng hồ thông minh casio"
    )

    form.submit_form(action="insert")

    time.sleep(1)
    alert = Alert(driver)
    alert.accept()
    time.sleep(2)
    alert.accept()
    time.sleep(2)

    existing_product_names = get_product_from_db()
    product_value = [product[0] for product in existing_product_names]
    assert product_name in product_value

#TC02: Kiểm tra trường hợp không điền thông tin bắt buộc.
def test_case_02(driver):
    form = ProductForm(driver)
    form.open_form()

    form.submit_form(action="insert")
    time.sleep(2)

    error_fields = [
        ".modal-product-container-content__err-name",
        ".modal-product-container-content__err-brand",
        ".modal-product-container-content__err-model",
        ".modal-product-container-content__err-gender",
        ".modal-product-container-content__err-color",
        ".modal-product-container-content__err-import-price",
        ".modal-product-container-content__err-price-to-sell",
        ".modal-product-container-content__err-desc"

    ]
    
    for field in error_fields:
        error_message = driver.find_element(By.CSS_SELECTOR, field)
        assert error_message.text == "*Trường này không được để trống"

    
#TC03: Kiểm tra trường hợp upload không phải hình ảnh.
def test_case_03(driver):
    form = ProductForm(driver)

    form.open_form()

    form.fill_form(
        brand="Casio",
        product_name="Test đồng hồ casio",
        image_path="D:/KTPM.docx",
        model="Đồng hồ thông minh",
        color="Bạc",
        gender="Nam",
        import_price="12000000",
        sell_price="13000000",
        discount="10",
        description="Đồng hồ thông minh casio"
    )

    form.submit_form(action="insert")

    time.sleep(3)
    error_img_message = driver.find_element(By.CSS_SELECTOR, ".modal-product-container-content__err-img")
    assert "Chỉ chấp nhận file hình ảnh" in error_img_message

#TC04: Kiểm tra độ dài của tên sản phẩm.
def test_case_04(driver):
    form = ProductForm(driver)

    form.open_form()

    long_product_name = "A" * 310

    form.fill_form(
        brand="Casio",
        product_name=long_product_name,
        image_path="D:/per3.jpg",
        model="Đồng hồ thông minh",
        color="Bạc",
        gender="Nam",
        import_price="12000000",
        sell_price="13000000",
        discount="10",
        description="Đồng hồ thông minh casio"
    )

    form.submit_form(action="insert")
    error_name_message = driver.find_element(By.CSS_SELECTOR, ".modal-product-container-content__err-name")
    assert error_name_message.text == "*Tên đồng hồ không vượt quá 300 kí tự"

#TC05: Điền vào trường giá nhập lớn hơn so với giá bán.
def test_case_05(driver):
    form = ProductForm(driver)

    form.open_form()


    form.fill_form(
        brand="Casio",
        product_name="Test đồng hồ",
        image_path="D:/per3.jpg",
        model="Đồng hồ thông minh",
        color="Bạc",
        gender="Nam",
        import_price="13000",
        sell_price="12000",
        discount="10",
        description="Đồng hồ thông minh casio"
    )

    form.submit_form(action="insert")
    time.sleep(1)
    alert = driver.switch_to.alert
    alert_text = alert.text

    expected_alert_text = "Giá nhập lớn hơn giá bán."
    assert alert_text == expected_alert_text

#TC06: Kiểm tra trường mã giảm giá vượt quá 100.
def test_case_06(driver):
    form = ProductForm(driver)

    form.open_form()

    form.fill_form(
        brand="Casio",
        product_name="Test đồng hồ",
        image_path="D:/per3.jpg",
        model="Đồng hồ thông minh",
        color="Bạc",
        gender="Nam",
        import_price="1200000",
        sell_price="1300000",
        discount="1000",
        description="Đồng hồ thông minh casio"
    )

    form.submit_form(action="insert")
    time.sleep(1)

    alert = driver.switch_to.alert
    alert_text = alert.text

    expected_alert_text = "Mã giảm giá vượt quá 100%"
    assert alert_text == expected_alert_text

#TC07: Kiểm tra trường giá nhập là số âm.
def test_case_07(driver):
    form = ProductForm(driver)

    form.open_form()
    sub_import_price = '-10000'
    form.fill_form(
        brand="Casio",
        product_name="Test đồng hồ",
        image_path="D:/per3.jpg",
        model="Đồng hồ thông minh",
        color="Bạc",
        gender="Nam",
        import_price=sub_import_price,
        sell_price="1300000",
        discount="10",
        description="Đồng hồ thông minh casio"
    )

    import_price_value = form.import_price_input.get_attribute("value")
    assert import_price_value > sub_import_price

#TC08: Kiểm tra trường giá bán là số âm.
def test_case_08(driver):
    form = ProductForm(driver)

    form.open_form()
    sub_sell_price = '-10000'
    form.fill_form(
        brand="Casio",
        product_name="Test đồng hồ",
        image_path="D:/per3.jpg",
        model="Đồng hồ thông minh",
        color="Bạc",
        gender="Nam",
        import_price="120000",
        sell_price=sub_sell_price,
        discount="10",
        description="Đồng hồ thông minh casio"
    )

    import_price_value = form.sell_price_input.get_attribute("value")
    assert import_price_value > sub_sell_price

#TC09: Kiểm tra số âm trường mã giảm giá.
def test_case_09(driver):
    form = ProductForm(driver)

    form.open_form()
    sub_discount = '-10'
    form.fill_form(
        brand="Casio",
        product_name="Test đồng hồ",
        image_path="D:/per3.jpg",
        model="Đồng hồ thông minh",
        color="Bạc",
        gender="Nam",
        import_price="120000",
        sell_price="130000",
        discount=sub_discount,
        description="Đồng hồ thông minh casio"
    )

    import_điscount_value = form.discount_input.get_attribute("value")
    assert import_điscount_value > sub_discount

#TC10: Kiểm tra thêm sản phẩm trùng tên với sản phẩm đã tồn tại.
def test_case_10(driver):
    form = ProductForm(driver)

    form.open_form()
    product_name_test = "Citizen BM9012-02A – Kính Sapphire – Eco-Drive (Năng Lượng Ánh Sáng) – Dây Da"

    form.fill_form(
        brand="Casio",
        product_name=product_name_test,
        image_path="D:/per3.jpg",
        model="Đồng hồ thông minh",
        color="Bạc",
        gender="Nam",
        import_price="120000",
        sell_price="130000",
        discount='10',
        description="Đồng hồ thông minh casio"
    )
        
    existing_products = get_product_from_db()
    existing_product_names = [product[0] for product in existing_products] 
    assert product_name_test not in existing_product_names

    form.submit_form(action="insert")
    time.sleep(1)
    alert = Alert(driver)
    alert.accept()
    time.sleep(2)
    alert.accept()
    time.sleep(2)
#TC11: Kiểm tra nhập “Kiểu máy khác”.
def test_case_11(driver):
    form = ProductForm(driver)

    form.open_form()

    form.fill_form(
        brand="Casio",
        product_name="Tên đồng hồ",
        image_path="D:/per3.jpg",
        model="Khác",
        color="Bạc",
        gender="Nam",
        import_price="120000",
        sell_price="130000",
        discount='10',
        description="Đồng hồ thông minh casio"
    )
    time.sleep(1)

    other_model_value="Đồng hồ cơ"
    other_model = driver.find_element(By.ID,"orther-product-model-value")
    other_model.send_keys(other_model_value)

    form.submit_form(action="insert")

    time.sleep(1)
    alert = Alert(driver)
    alert.accept()
    time.sleep(3)
    alert.accept()
    time.sleep(3)

    existing_products = get_product_from_db()
    existing_models = [product[1] for product in existing_products]

    assert other_model_value in existing_models


#TC12: Kiểm tra nhập “Màu sắc khác”.
def test_case_12(driver):
    form = ProductForm(driver)

    form.open_form()

    form.fill_form(
        brand="Casio",
        product_name="Tên đồng hồ",
        image_path="D:/per3.jpg",
        model="Đồng hồ cơ",
        color="Khác",
        gender="Nam",
        import_price="120000",
        sell_price="130000",
        discount='10',
        description="Đồng hồ thông minh casio"
    )
    time.sleep(1)

    other_color_value="Đen"
    other_color = driver.find_element(By.ID,"orther-product-color-value")
    other_color.send_keys(other_color_value)

    form.submit_form(action="insert")

    time.sleep(1)
    alert = Alert(driver)
    alert.accept()
    time.sleep(3)
    alert.accept()
    time.sleep(3)

    existing_products = get_product_from_db()
    existing_models = [product[2] for product in existing_products]
    assert other_color_value in existing_models

#TC13: Kiểm tra sửa thông tin sản phẩm thành công.
def test_case_13(driver):
    form = ProductForm(driver)

    form.click_edit_button("PR000026")
    product_name = "Citizen BI5006-81P – Quartz (Pin) – Mặt Số 39 Mm, Lịch Ngày, Chống Nước 5 ATM"
    form.fill_form(
        brand="Seiko 2",
        product_name=product_name,
        image_path="D:/per2.jpg",
        model="Đồng hồ cơ",
        color="Đen",
        gender="Nữ",
        import_price="140000",
        sell_price="160000",
        discount='2',
        description="Đồng hồ thông minh Seiko 2"
    )
    time.sleep(1)

    form.submit_form(action="edit")

    time.sleep(1)
    alert = Alert(driver)
    alert.accept()
    time.sleep(3)
    alert.accept()
    time.sleep(3)

    existing_product_names = get_product_from_db()
    product_value = [product[0] for product in existing_product_names]
    assert product_name in product_value

#TC14: Kiểm tra sửa sản phẩm khi xóa hết thông tin trong các trường.
def test_case_14(driver):
    form = ProductForm(driver)
    form.click_edit_button("PR000026")

    form.fill_form(
        brand="Casio",
        product_name=" ",
        image_path="D:/a.jpg",
        model="Đồng hồ cơ",
        color="Đen",
        gender="Nam",
        import_price=" ",
        sell_price=" ",
        discount=' ',
        description=" "
    )

    form.submit_form(action="edit")
    time.sleep(2)

    error_fields = [
        ".modal-product-container-content__err-name",
        ".modal-product-container-content__err-import-price",
        ".modal-product-container-content__err-price-to-sell",
        ".modal-product-container-content__err-desc"
    ]
    
    for field in error_fields:
        error_message = driver.find_element(By.CSS_SELECTOR, field)
        assert error_message.text == "*Trường này không được để trống"

#TC15: Kiểm tra sửa sản phẩm và hủy thao tác.
def test_case_15(driver):
    form = ProductForm(driver)
    open_form = form.click_edit_button("PR000026")

    form.fill_form(
        brand="Seiko 2",
        product_name="tên đồng hồ",
        image_path="D:/per2.jpg",
        model="Đồng hồ cơ",
        color="Đen",
        gender="Nữ",
        import_price="140000",
        sell_price="160000",
        discount='2',
        description="Đồng hồ thông minh Seiko 2"
    )

    close_btn = driver.find_element(By.CLASS_NAME, "modal-product-container__close")
    close_btn.click()

    assert open_form is None

#TC16: Kiểm tra sửa sản phẩm khi thương hiệu không hoạt động.
def test_case_16(driver):
    title_element = driver.find_element(By.XPATH, f"//tr[@id='PR000024']/td[12]")
    assert title_element.text == "Ngừng kinh doanh"

#TC17: Kiểm tra xóa sản phẩm thành công.
def test_case_17(driver):
    product_id = "PR000026"
    del_element = driver.find_element(By.XPATH, f"//span[@onclick=\"displayPopupDel('{product_id}');\"]")
    del_element.click()
    time.sleep(1)
    alert = Alert(driver)
    alert.accept()
    time.sleep(2)
    alert.accept()
    time.sleep(2)

    rows = driver.find_elements(By.XPATH, f"//tr[@id='{product_id}']")
    assert len(rows) == 0

#TC18: Kiểm tra tìm kiếm với chữ hoa, chữ thường.
def test_case_18(driver):
    brand_name = "CASIO"
    form = ProductForm(driver)
    form.search_input.send_keys(brand_name)
    form.click_search_btn()

    table_rows = driver.find_elements(By.XPATH, "//table[@class='container-product__table']/tbody/tr")

    for row in table_rows:
        brand_name = row.find_element(By.XPATH, "./td[1]").text
        assert brand_name == "Casio"
        
#TC19: Kiểm tra tìm kiếm với từ khóa rỗng.
def test_case_19(driver):
    form = ProductForm(driver)
    form.click_search_btn()

    db_products = get_product_from_db()[-1:]

    table_rows = driver.find_elements(By.XPATH, "//table[@class='container-product__table']/tbody/tr")[:1]

    for i, row in enumerate(table_rows):
        brand_name_ui = row.find_element(By.XPATH, "./td[1]").text  
        brand_name_db = db_products[i][3]
        assert brand_name_ui == brand_name_db

#TC20: Kiểm tra tìm kiếm không hợp lệ.
def test_case_20(driver):
    form = ProductForm(driver)
    form.search_input.send_keys("abc!!#@")
    form.click_search_btn()

    message_element = driver.find_element(By.XPATH, "//table[@class='container-product__table']/tbody/tr/td[@colspan='12']")
    
    message_text = message_element.text
    assert message_text == "Không có đồng hồ nào để hiển thị!"

#TC21: Kiểm tra tìm kiếm theo tên sản phẩm.
def test_case_21(driver):
    product_name = "Citizen ED8180-52X – Nữ – Quartz (Pin) – Mặt Số 33mm, Kính Cứng, Chống Nước 3atm"
    form = ProductForm(driver)
    form.search_input.send_keys(product_name)
    form.click_search_btn()

    existing_product_names = get_product_from_db()
    product_value = [product[0] for product in existing_product_names]
    assert product_name in product_value

#TC22: Kiểm tra tìm kiếm theo thương hiệu sản phẩm.
def test_case_22(driver):
    brand_name = "Citizen"
    form = ProductForm(driver)
    form.search_input.send_keys(brand_name)
    form.click_search_btn()

    existing_product_names = get_product_from_db()
    product_value = [product[3] for product in existing_product_names]
    assert brand_name in product_value

#TC23: Kiểm tra tìm kiếm theo màu sắc sản phẩm.
def test_case_23(driver):
    color_name = "Đen"
    form = ProductForm(driver)
    form.search_input.send_keys(color_name)
    form.click_search_btn()

    existing_product_names = get_product_from_db()
    product_value = [product[2] for product in existing_product_names]
    assert color_name in product_value

#TC24: Kiểm tra tìm kiếm theo kiểu máy sản phẩm.
def test_case_24(driver):
    model_name = "Đồng hồ cơ"
    form = ProductForm(driver)
    form.search_input.send_keys(model_name)
    form.click_search_btn()

    existing_product_names = get_product_from_db()
    product_value = [product[1] for product in existing_product_names]
    assert model_name in product_value

#TC25: Kiểm tra tìm kiếm theo giới tính của sản phẩm.
def test_case_25(driver):
    gender_name = "Nam"
    form = ProductForm(driver)
    form.search_input.send_keys(gender_name)
    form.click_search_btn()

    existing_product_names = get_product_from_db()
    product_value = [product[4] for product in existing_product_names]
    assert gender_name in product_value

#TC26: Kiểm tra hiển thị đúng số lượng mục trên mỗi trang.
def test_case_26(driver):
    paging_div = driver.find_element(By.CLASS_NAME, "paging")
    paging_items = paging_div.find_elements(By.CLASS_NAME, "paging__item")

    page_2 = next((item for item in paging_items if item.text == "2"), None)
    assert page_2 is not None


#TC27: Kiểm tra chức năng chuyển sang trang tiếp theo.
def test_case_27(driver):
    first_page_data = []
    rows = driver.find_elements(By.XPATH, "//table[@class='container-product__table']/tbody/tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        first_page_data.append([cell.text for cell in cells[:5]]) 

    next_page_button = driver.find_element(By.XPATH, "//a[contains(@class, 'paging__item') and text()='2']")
    next_page_button.click()
    time.sleep(2) 

    second_page_data = []
    rows = driver.find_elements(By.XPATH, "//table[@class='container-product__table']/tbody/tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        second_page_data.append([cell.text for cell in cells[:5]]) 

    assert first_page_data != second_page_data

#TC28: Kiểm tra chức năng chuyển sang trang tiếp theo.
def test_case_28(driver):
    next_page_button = driver.find_element(By.XPATH, "//a[contains(@class, 'paging__item') and text()='2']")
    next_page_button.click()
    time.sleep(2) 

    second_page_data = []
    rows = driver.find_elements(By.XPATH, "//table[@class='container-product__table']/tbody/tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        second_page_data.append([cell.text for cell in cells[:5]])

    previous_page_button = driver.find_element(By.XPATH, "//a[contains(@class, 'paging__item') and text()='1']")
    previous_page_button.click()
    time.sleep(2) 

    first_page_data = []
    rows = driver.find_elements(By.XPATH, "//table[@class='container-product__table']/tbody/tr")
    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        first_page_data.append([cell.text for cell in cells[:5]])  

    assert first_page_data != second_page_data

#TC29: Kiểm tra chuyển đến trang cuối cùng.
def test_case_29(driver):
    last_page_button = driver.find_element(By.XPATH, "//a[contains(@class, 'paging__item') and text()='Last']")
    last_page_button.click()
    time.sleep(2) 
    
    current_page_number = driver.find_element(By.XPATH, "//a[contains(@class, 'paging__item--active')]").text
    
    total_pages = 4
    assert int(current_page_number) == total_pages

#TC30: Kiểm tra quay về trang đầu tiên.
def test_case_30(driver):
    last_page_button = driver.find_element(By.XPATH, "//a[contains(@class, 'paging__item') and text()='Last']")
    last_page_button.click()
    time.sleep(2) 
    
    first_page_button = driver.find_element(By.XPATH, "//a[contains(@class, 'paging__item') and text()='First']")
    first_page_button.click()
    time.sleep(2)
    
    current_page_number = driver.find_element(By.XPATH, "//a[contains(@class, 'paging__item--active')]").text
    
    assert int(current_page_number) == 1