<?php

use PHPUnit\Framework\TestCase;

class ProductTest extends TestCase
{
    protected $db;

    protected function setUp(): void
    {
        $this->db = new mysqli('localhost', 'root', '', 'vutrudongho');

        if ($this->db->connect_error) {
            die("Connection failed: " . $this->db->connect_error);
        }
    }

    protected function tearDown(): void
    {
        $this->db->close();
    }

    public function insertProduct($brandName, $productName, $priceToSell, $importPrice, $discount, $model, $color, $gender, $description, $productImg, $productStatus)
    {
        $result = mysqli_query($this->db, "SELECT ProductID FROM product ORDER BY ProductID DESC LIMIT 1");
        $row = mysqli_fetch_array($result);
        $productId = $row ? 'PR' . str_pad(substr($row['ProductID'], 2) + 1, 6, '0', STR_PAD_LEFT) : 'PR000001';

        $result = mysqli_query($this->db, "SELECT BrandID FROM brand WHERE BrandName = '$brandName'");
        $brandId = mysqli_fetch_array($result)['BrandID'];

        $query = "INSERT INTO product (ProductID, BrandID, ProductName, PriceToSell, ImportPrice, Discount, Model, Color, Gender, Description, ProductImg, Status, CanDel)
                  VALUES ('$productId', '$brandId', '$productName', $priceToSell, $importPrice, $discount, '$model', '$color', '$gender', '$description', '$productImg', $productStatus, 1)";

        return mysqli_query($this->db, $query);
    }

    public function deleteProduct($productName)
    {
        $query = "DELETE FROM product WHERE ProductName = '$productName'";
        return mysqli_query($this->db, $query);
    }

       public function testThemSanPhamThanhCong()
    {
        $_POST['submit'] = 'insert';
        $_POST['brand'] = 'Casio'; 
        $_POST['product-name'] = 'Apple Watch';
        $_POST['model'] = 'Đồng hồ cơ';
        $_POST['color'] = 'Màu đỏ';
        $_POST['gender'] = 'Unisex';
        $_POST['import-price'] = '1000000';
        $_POST['price-to-sell'] = '1200000';
        $_POST['discount'] = '10';
        $_POST['desc'] = 'This is a product description.';
        $_POST['product-status'] = 1;

        $_FILES['product-img'] = [
            'name' => 'a.jpg',
            'type' => 'image/jpeg',
            'tmp_name' => '/tmp/phpunit-test-file',
            'error' => 0,
            'size' => 1024
        ];

        $targetDir = 'assets/img/productImg/';
        $targetDir . basename($_FILES['product-img']['name']);

        $insertResult = $this->insertProduct(
            $_POST['brand'],
            $_POST['product-name'],
            $_POST['price-to-sell'],
            $_POST['import-price'],
            $_POST['discount'],
            $_POST['model'],
            $_POST['color'],
            $_POST['gender'],
            $_POST['desc'],
            $_FILES['product-img']['name'],
            $_POST['product-status']
        );

        $this->assertTrue($insertResult, 'Thêm sản phẩm thành công.');

        $query = "SELECT * FROM product WHERE ProductName = '{$_POST['product-name']}'";
        $result = mysqli_query($this->db, $query);
        $product = mysqli_fetch_assoc($result);

        $brandQuery = "SELECT BrandID FROM brand WHERE BrandName = 'Casio'";
        $brandResult = mysqli_query($this->db, $brandQuery);
        $brand = mysqli_fetch_assoc($brandResult);
        $expectedBrandID = $brand['BrandID'];

        $this->assertEquals($_POST['product-name'], $product['ProductName'], 'Tên sản phẩm đúng.');
        $this->assertEquals($expectedBrandID, $product['BrandID'], 'Thương hiệu đúng.');
        $this->assertEquals($_POST['price-to-sell'], $product['PriceToSell'], 'Giá bán đúng.');
        $this->assertEquals($_POST['import-price'], $product['ImportPrice'], 'Giá nhập đúng.');
        $this->assertEquals($_POST['discount'], $product['Discount'], 'Giảm giá đúng.');
        $this->assertEquals($_POST['model'], $product['Model'], 'Mô hình đúng.');
        $this->assertEquals($_POST['color'], $product['Color'], 'Màu sắc đúng.');
        $this->assertEquals($_POST['gender'], $product['Gender'], 'Giới tính đúng.');
        $this->assertEquals($_POST['desc'], $product['Description'], 'Mô tả đúng.');
        $this->assertEquals('a.jpg', $product['ProductImg'], 'Hình ảnh đúng.');
        $this->assertEquals(1, $product['Status'], 'Trạng thái đúng.');

        $this->deleteProduct($_POST['product-name']);
    }
    public function testKhongDienThongTinBatBuoc()
    {
        $_POST['submit'] = 'insert';
        $_POST['brand'] = ' ';
        $_POST['product-name'] = ' ';
        $_POST['model'] = ' ';
        $_POST['color'] = ' ';
        $_POST['gender'] = ' ';
        $_POST['import-price'] = ' ';
        $_POST['price-to-sell'] = ' ';
        $_POST['discount'] = ' ';
        $_POST['desc'] = ' ';
        $_POST['product-status'] = 1;

        $_FILES['product-img']['name'] = 'a.jpg';
        $_FILES['product-img']['tmp_name'] = 'D:/a.jpg';
        $_FILES['product-img']['error'] = 0;
        $_FILES['product-img']['size'] = 1024;

        $errors = [];

        $requiredFields = [
            'brand' => 'modal-product-container-content__err-brand',
            'product-name' => 'modal-product-container-content__err-name',
            'model' => 'modal-product-container-content__err-model',
            'color' => 'modal-product-container-content__err-color',
            'gender' => 'modal-product-container-content__err-gender',
            'import-price' => 'modal-product-container-content__err-import-price',
            'price-to-sell' => 'modal-product-container-content__err-price-to-sell',
            'desc' => 'modal-product-container-content__err-desc',
        ];

        foreach ($requiredFields as $field => $errorClass) {
            if (empty(trim($_POST[$field]))) {
                $errors[] = "*Trường $field không được để trống";
            }
        }

        foreach ($requiredFields as $field => $errorClass) {
            $expectedError = "*Trường $field không được để trống";
            $this->assertStringContainsString($expectedError, implode("\n", $errors), "Thiếu thông báo lỗi cho trường $field.");
        }

        if (!empty($errors)) {
            return;
        }

        $result = $this->insertProduct(
            $_POST['brand'],
            $_POST['product-name'],
            $_POST['price-to-sell'],
            $_POST['import-price'],
            $_POST['discount'],
            $_POST['model'],
            $_POST['color'],
            $_POST['gender'],
            $_POST['desc'],
            $_FILES['product-img']['name'],
            $_POST['product-status']
        );

        $this->assertFalse($result, 'Sản phẩm không được phép thêm khi thiếu thông tin bắt buộc!');
    }

    public function testTaiLenFileKhongPhaiHinhAnh()
    {
        $_POST['submit'] = 'insert';
        $_POST['brand'] = 'Casio';
        $_POST['product-name'] = 'Apple Watch';
        $_POST['model'] = 'Đồng hồ cơ';
        $_POST['color'] = 'Màu đỏ';
        $_POST['gender'] = 'Unisex';
        $_POST['import-price'] = '1000000';
        $_POST['price-to-sell'] = '1200000';
        $_POST['discount'] = '10';
        $_POST['desc'] = 'This is a product description.';
        $_POST['product-status'] = 1;

        $_FILES['product-img']['name'] = 'KTPM.docx';
        $_FILES['product-img']['tmp_name'] = 'KTPM.docx';
        $_FILES['product-img']['error'] = 0;
        $_FILES['product-img']['size'] = 1024;

        $allowedFileTypes = ['image/jpeg', 'image/png', 'image/jpg']; 
        $fileType = mime_content_type($_FILES['product-img']['tmp_name']);

        if (!in_array($fileType, $allowedFileTypes)) {
            $this->assertFalse(true, 'File tải lên không phải hình ảnh hợp lệ!');
            return;
        }

        $result = $this->insertProduct(
            $_POST['brand'],
            $_POST['product-name'],
            $_POST['price-to-sell'],
            $_POST['import-price'],
            $_POST['discount'],
            $_POST['model'],
            $_POST['color'],
            $_POST['gender'],
            $_POST['desc'],
            $_FILES['product-img']['name'],
            $_POST['product-status']
        );

        $this->assertFalse($result, 'Sản phẩm không được phép thêm khi tải lên file không phải hình ảnh!');
    }

    public function testTenSanPhamVuotQuaDoDaiChoPhep()
    {
        $_POST['submit'] = 'insert';
        $_POST['brand'] = 'Casio';
        $_POST['product-name'] = str_repeat('A', 310); 
        $_POST['model'] = 'Đồng hồ cơ';
        $_POST['color'] = 'Màu đỏ';
        $_POST['gender'] = 'Unisex';
        $_POST['import-price'] = '1000000';
        $_POST['price-to-sell'] = '1200000';
        $_POST['discount'] = '10';
        $_POST['desc'] = 'This is a product description.';
        $_POST['product-status'] = 1;

        $_FILES['product-img']['name'] = 'a.jpg';
        $_FILES['product-img']['tmp_name'] = 'D:/a.jpg';
        $_FILES['product-img']['error'] = 0;
        $_FILES['product-img']['size'] = 1024;
        $errors = [];

        if (strlen($_POST['product-name']) > 300) {
            $errors['product-name'] = 'modal-product-container-content__err-name';
        }

        $this->assertArrayHasKey('product-name', $errors, 'Tên sản phẩm vượt quá 300 ký tự không bị phát hiện.');
        $this->assertEquals('modal-product-container-content__err-name', $errors['product-name'], 'Lỗi không đúng với lớp chỉ định.');

        if (!empty($errors)) {
            return;
        }

        $result = $this->insertProduct(
            $_POST['brand'],
            $_POST['product-name'],
            $_POST['price-to-sell'],
            $_POST['import-price'],
            $_POST['discount'],
            $_POST['model'],
            $_POST['color'],
            $_POST['gender'],
            $_POST['desc'],
            $_FILES['product-img']['name'],
            $_POST['product-status']
        );
        $this->assertFalse($result, 'Sản phẩm không được phép thêm khi tên vượt quá 300 ký tự.');
    }


    public function testGiaNhapLonHonGiaBan()
    {
        $_POST['submit'] = 'insert';
        $_POST['brand'] = 'Casio';
        $_POST['product-name'] = 'Apple Watch';
        $_POST['model'] = 'Đồng hồ cơ';
        $_POST['color'] = 'Màu đỏ';
        $_POST['gender'] = 'Unisex';
        $_POST['import-price'] = '100000';
        $_POST['price-to-sell'] = '1000';
        $_POST['discount'] = '10';
        $_POST['desc'] = 'This is a product description.';
        $_POST['product-status'] = 1;

        $_FILES['product-img']['name'] = 'a.jpg';
        $_FILES['product-img']['tmp_name'] = 'D:/a.jpg';
        $_FILES['product-img']['error'] = 0;
        $_FILES['product-img']['size'] = 1024;

        $result = $this->insertProduct(
            $_POST['brand'],
            $_POST['product-name'],
            $_POST['price-to-sell'],
            $_POST['import-price'],
            $_POST['discount'],
            $_POST['model'],
            $_POST['color'],
            $_POST['gender'],
            $_POST['desc'],
            $_FILES['product-img']['name'],
            $_POST['product-status']
        );

        $this->assertFalse($result, 'Thêm sản phẩm thất bại vì giá nhập lớn hơn giá bán.');
    }

    public function testMaGiamGiaLonHon100()
    {
        $_POST['submit'] = 'insert';
        $_POST['brand'] = 'Casio';
        $_POST['product-name'] = 'Apple Watch';
        $_POST['model'] = 'Đồng hồ cơ';
        $_POST['color'] = 'Màu đỏ';
        $_POST['gender'] = 'Unisex';
        $_POST['import-price'] = '100000';
        $_POST['price-to-sell'] = '100000';
        $_POST['discount'] = '120';
        $_POST['desc'] = 'This is a product description.';
        $_POST['product-status'] = 1;

        $_FILES['product-img']['name'] = 'a.jpg';
        $_FILES['product-img']['tmp_name'] = 'D:/a.jpg';
        $_FILES['product-img']['error'] = 0;
        $_FILES['product-img']['size'] = 1024;

        $result = $this->insertProduct(
        $_POST['brand'],
        $_POST['product-name'],
        $_POST['price-to-sell'],
        $_POST['import-price'],
        $_POST['discount'],
        $_POST['model'],
        $_POST['color'],
        $_POST['gender'],
        $_POST['desc'],
        $_FILES['product-img']['name'],
        $_POST['product-status']
        );

        $this->assertFalse($result, 'Thêm sản phẩm thất bại vì mã giảm giá vượt quá 100.');
    }

    public function testMaGiamGiaSoAm()
    {
        $_POST['submit'] = 'insert';
        $_POST['brand'] = 'Casio';
        $_POST['product-name'] = 'Apple Watch';
        $_POST['model'] = 'Đồng hồ cơ';
        $_POST['color'] = 'Màu đỏ';
        $_POST['gender'] = 'Unisex';
        $_POST['import-price'] = '100000';
        $_POST['price-to-sell'] = '100000';
        $_POST['discount'] = '-10';
        $_POST['desc'] = 'This is a product description.';
        $_POST['product-status'] = 1;

        $_FILES['product-img']['name'] = 'a.jpg';
        $_FILES['product-img']['tmp_name'] = 'D:/a.jpg';
        $_FILES['product-img']['error'] = 0;
        $_FILES['product-img']['size'] = 1024;

        $errors = [];

        // Kiểm tra độ dài tên sản phẩm
        if ((float)($_POST['discount']) < 0) {
            $errors['discount'] = 'modal-product-container-content__err-discount';
        }

        $this->assertArrayHasKey('discount', $errors, 'Discount false');
        $this->assertEquals('modal-product-container-content__err-discount', $errors['discount'], 'Lỗi không đúng với lớp chỉ định.');

        if (!empty($errors)) {
            return;
        }

        $result = $this->insertProduct(
        $_POST['brand'],
        $_POST['product-name'],
        $_POST['price-to-sell'],
        $_POST['import-price'],
        $_POST['discount'],
        $_POST['model'],
        $_POST['color'],
        $_POST['gender'],
        $_POST['desc'],
        $_FILES['product-img']['name'],
        $_POST['product-status']
        );

        $this->assertFalse($result, 'Thêm sản phẩm thất bại vì mã giảm giá < 0.');
    }


    public function testTrungTenSanPham()
    {
        $_POST['submit'] = 'insert';
        $_POST['brand'] = 'Casio';
        $_POST['product-name'] = 'Apple Watch';
        $_POST['model'] = 'Đồng hồ cơ';
        $_POST['color'] = 'Màu đỏ';
        $_POST['gender'] = 'Unisex';
        $_POST['import-price'] = '100000';
        $_POST['price-to-sell'] = '100000';
        $_POST['discount'] = '120';
        $_POST['desc'] = 'This is a product description.';
        $_POST['product-status'] = 1;

        $_FILES['product-img']['name'] = 'a.jpg';
        $_FILES['product-img']['tmp_name'] = 'D:/a.jpg';
        $_FILES['product-img']['error'] = 0;
        $_FILES['product-img']['size'] = 1024;

        $result = $this->insertProduct(
        $_POST['brand'],
        $_POST['product-name'],
        $_POST['price-to-sell'],
        $_POST['import-price'],
        $_POST['discount'],
        $_POST['model'],
        $_POST['color'],
        $_POST['gender'],
        $_POST['desc'],
        $_FILES['product-img']['name'],
        $_POST['product-status']
        );

        $this->assertFalse($result, 'Thêm sản phẩm thất bại vì trùng lặp thêm sản phẩm.');
    }

    public function testKieuMayKhac()
    {
        $_POST['submit'] = 'insert';
        $_POST['brand'] = 'Casio';
        $_POST['product-name'] = 'Apple Watch';
        $_POST['model'] = 'Kiểu máy mới';
        $_POST['color'] = 'Màu đỏ';
        $_POST['gender'] = 'Unisex';
        $_POST['import-price'] = '100000';
        $_POST['price-to-sell'] = '1000';
        $_POST['discount'] = '10';
        $_POST['desc'] = 'This is a product description.';
        $_POST['product-status'] = 1;

        $_FILES['product-img']['name'] = 'a.jpg';
        $_FILES['product-img']['tmp_name'] = 'D:/a.jpg';
        $_FILES['product-img']['error'] = 0;
        $_FILES['product-img']['size'] = 1024;

        $result = $this->insertProduct(
        $_POST['brand'],
        $_POST['product-name'],
        $_POST['price-to-sell'],
        $_POST['import-price'],
        $_POST['discount'],
        $_POST['model'],
        $_POST['color'],
        $_POST['gender'],
        $_POST['desc'],
        $_FILES['product-img']['name'],
        $_POST['product-status']
        );

        $this->assertTrue($result, 'Thêm sản phẩm thành công!');

        $this->deleteProduct($_POST['product-name']);
    }

    public function testMauSacKhac()
    {
        $_POST['submit'] = 'insert';
        $_POST['brand'] = 'Casio';
        $_POST['product-name'] = 'Apple Watch';
        $_POST['model'] = 'Đồng hồ cơ';
        $_POST['color'] = 'Màu sắc khác';
        $_POST['gender'] = 'Unisex';
        $_POST['import-price'] = '100000';
        $_POST['price-to-sell'] = '1000';
        $_POST['discount'] = '10';
        $_POST['desc'] = 'This is a product description.';
        $_POST['product-status'] = 1;

        $_FILES['product-img']['name'] = 'a.jpg';
        $_FILES['product-img']['tmp_name'] = 'D:/a.jpg';
        $_FILES['product-img']['error'] = 0;
        $_FILES['product-img']['size'] = 1024;

        $result = $this->insertProduct(
            $_POST['brand'],
            $_POST['product-name'],
            $_POST['price-to-sell'],
            $_POST['import-price'],
            $_POST['discount'],
            $_POST['model'],
            $_POST['color'],
            $_POST['gender'],
            $_POST['desc'],
            $_FILES['product-img']['name'],
            $_POST['product-status']
        );

        $this->assertTrue($result, 'Thêm sản phẩm thành công!');
        $this->deleteProduct($_POST['product-name']);
    }
}
