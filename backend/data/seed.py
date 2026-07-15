"""
DataPilot — Script tạo dữ liệu mẫu (phiên bản thuần Việt Nam)
Mô phỏng hệ thống HR công ty công nghệ ~100 nhân sự tại Việt Nam.

Bảng:
  Departments      — cây phòng ban (23 phòng, 2 cấp)
  Employees        — thông tin cơ bản nhân viên
  EmployeeProfiles — hồ sơ HR đầy đủ (CCCD, hợp đồng, ngân hàng...)
  BaseSalary       — lịch sử lương cứng + phụ cấp cố định mỗi nhân viên
  SalaryHistory    — lương thực nhận hàng tháng (tính từ BaseSalary + Attendance)
  Attendance       — chấm công 9–18h, T2–T6, Jan–Jun 2025
  LeaveRequests    — đơn nghỉ phép (theo Luật Lao Động VN)
  ChatHistory      — lịch sử hội thoại với AI
  Categories       — danh mục sản phẩm
  Suppliers        — nhà cung cấp
  Products         — sản phẩm
  Customers        — khách hàng
  Shippers         — đơn vị vận chuyển
  Orders           — đơn hàng
  OrderDetails     — chi tiết đơn hàng


Chạy:
  python data/seed.py

Kết nối tới server PostgreSQL cục bộ (localhost) port 5432 với user mặc định "postgres" và password "12345678".
"""



import random
import sys
from datetime import date, timedelta, datetime
import psycopg
sys.stdout.reconfigure(encoding="utf-8")


def randomDate(start: date, end: date) -> date:
    """Trả về ngày ngẫu nhiên trong khoảng [start, end]."""
    delta = (end - start).days
    if delta <= 0:
        return start
    return start + timedelta(days=random.randint(0, delta))


def weightedChoice(choices: list, weights: list):
    """Chọn ngẫu nhiên có trọng số."""
    total = sum(weights)
    r = random.uniform(0, total)
    cumulative = 0
    for choice, weight in zip(choices, weights):
        cumulative += weight
        if r <= cumulative:
            return choice
    return choices[-1]


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS "Departments" (
    "DepartmentID"      BIGSERIAL PRIMARY KEY,
    "DepartmentName"    TEXT    NOT NULL UNIQUE,
    "ParentDepartmentID" INTEGER REFERENCES "Departments"("DepartmentID"),
    "CostCenter"        TEXT    NOT NULL,
    "HeadCount"         INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS "Employees" (
    "EmployeeID"        BIGSERIAL PRIMARY KEY,
    "HoTen"             TEXT    NOT NULL,
    "GioiTinh"          TEXT    NOT NULL CHECK("GioiTinh" IN ('Nam', 'Nữ')),
    "NgaySinh"          DATE    NOT NULL,
    "DiaChi"            TEXT    NOT NULL,
    "ThanhPho"          TEXT    NOT NULL,
    "SoDienThoai"       TEXT    NOT NULL,
    "NgayVaoLam"        DATE    NOT NULL
);

CREATE TABLE IF NOT EXISTS "EmployeeProfiles" (
    "ProfileID"         BIGSERIAL PRIMARY KEY,
    "EmployeeID"        INTEGER NOT NULL UNIQUE REFERENCES "Employees"("EmployeeID"),
    "DepartmentID"      INTEGER NOT NULL REFERENCES "Departments"("DepartmentID"),
    "CCCD"              TEXT    NOT NULL UNIQUE,
    "TinhTrangHonNhan"  TEXT    NOT NULL CHECK("TinhTrangHonNhan" IN ('SINGLE','MARRIED','DIVORCED')),
    "LoaiHopDong"       TEXT    NOT NULL CHECK("LoaiHopDong" IN ('FULL_TIME','CONTRACT','PROBATION')),
    "TrangThaiLamViec"  TEXT    NOT NULL CHECK("TrangThaiLamViec" IN ('ACTIVE','RESIGNED','PENDING_TERMINATION')),
    "NgayVao"           DATE    NOT NULL,
    "NgayNghi"          DATE,
    "ChucVu"            TEXT    NOT NULL,
    "CapBac"            TEXT    NOT NULL,
    "QuanLyTrucTiepID"  INTEGER REFERENCES "Employees"("EmployeeID"),
    "EmailCongTy"       TEXT    NOT NULL UNIQUE,
    "SoDienThoaiCongTy" TEXT    NOT NULL,
    "NguoiLienHeKhánCap" TEXT    NOT NULL,
    "SoTaiKhoanNganHang" TEXT    NOT NULL,
    "TenNganHang"       TEXT    NOT NULL,
    "MaSoThue"          TEXT    NOT NULL UNIQUE,
    "SoNgayPhepNam"     INTEGER NOT NULL DEFAULT 12,
    "SoNgayPhepBenh"    INTEGER NOT NULL DEFAULT 12
);

-- Lịch sử lương cứng: mỗi lần tăng/điều chỉnh lương tạo 1 dòng mới
CREATE TABLE IF NOT EXISTS "BaseSalary" (
    "BaseSalaryID"      BIGSERIAL PRIMARY KEY,
    "EmployeeID"        INTEGER NOT NULL REFERENCES "Employees"("EmployeeID"),
    "NgayHieuLuc"       DATE    NOT NULL,
    "LuongCoBan"        NUMERIC NOT NULL,
    "PhuCapDiLai"       NUMERIC NOT NULL DEFAULT 0,
    "PhuCapAnTrua"      NUMERIC NOT NULL DEFAULT 0,
    "PhuCapSucKhoe"     NUMERIC NOT NULL DEFAULT 0,
    "GhiChu"            TEXT,
    UNIQUE("EmployeeID", "NgayHieuLuc")
);
    
-- Lương thực nhận hàng tháng — tính từ BaseSalary + Attendance
CREATE TABLE IF NOT EXISTS "SalaryHistory" (
    "SalaryID"          BIGSERIAL PRIMARY KEY,
    "EmployeeID"        INTEGER NOT NULL REFERENCES "Employees"("EmployeeID"),
    "BaseSalaryID"      INTEGER NOT NULL REFERENCES "BaseSalary"("BaseSalaryID"),
    "NamKy"             INTEGER NOT NULL,
    "ThangKy"           INTEGER NOT NULL CHECK("ThangKy" BETWEEN 1 AND 12),
    "SoNgayLamViec"     INTEGER NOT NULL DEFAULT 0,
    "SoPhutTreGioTong"  INTEGER NOT NULL DEFAULT 0,
    "SoPhutTangCaTong"  INTEGER NOT NULL DEFAULT 0,
    "LuongCoBan"        NUMERIC NOT NULL,
    "PhuCapDiLai"       NUMERIC NOT NULL DEFAULT 0,
    "PhuCapAnTrua"      NUMERIC NOT NULL DEFAULT 0,
    "PhuCapSucKhoe"     NUMERIC NOT NULL DEFAULT 0,
    "ThuongHieuQua"     NUMERIC NOT NULL DEFAULT 0,
    "PhuCapTangCa"      NUMERIC NOT NULL DEFAULT 0,
    "KhauTruDiTre"      NUMERIC NOT NULL DEFAULT 0,
    "KhauTruThue"       NUMERIC NOT NULL DEFAULT 0,
    "KhauTruBHXH"       NUMERIC NOT NULL DEFAULT 0,
    "LuongThucNhan"     NUMERIC NOT NULL,
    "NgayThanhToan"     DATE    NOT NULL,
    UNIQUE("EmployeeID", "NamKy", "ThangKy")
);

CREATE TABLE IF NOT EXISTS "Attendance" (
    "AttendanceID"      BIGSERIAL PRIMARY KEY,
    "EmployeeID"        INTEGER NOT NULL REFERENCES "Employees"("EmployeeID"),
    "NgayLamViec"       DATE    NOT NULL,
    "GioVao"            TEXT,
    "GioRa"             TEXT,
    "HinhThucLam"       TEXT    NOT NULL DEFAULT 'OFFICE'
                                CHECK("HinhThucLam" IN ('OFFICE','REMOTE','BUSINESS_TRIP')),
    "TrangThai"         TEXT    NOT NULL
                                CHECK("TrangThai" IN ('PRESENT','ABSENT','ON_LEAVE','HOLIDAY','WEEKEND')),
    "DiTre"             INTEGER NOT NULL DEFAULT 0 CHECK("DiTre" IN (0,1)),
    "SoPhutDiTre"       INTEGER NOT NULL DEFAULT 0,
    "SoPhutTangCa"      INTEGER NOT NULL DEFAULT 0,
    "GhiChu"            TEXT,
    UNIQUE("EmployeeID", "NgayLamViec")
);

CREATE TABLE IF NOT EXISTS "LeaveRequests" (
    "LeaveID"           BIGSERIAL PRIMARY KEY,
    "EmployeeID"        INTEGER NOT NULL REFERENCES "Employees"("EmployeeID"),
    "LoaiNghi"          TEXT    NOT NULL
                                CHECK("LoaiNghi" IN ('ANNUAL','SICK','PERSONAL','MATERNITY','PATERNITY','UNPAID')),
    "NgayBatDau"        DATE    NOT NULL,
    "NgayKetThuc"       DATE    NOT NULL,
    "SoNgay"            INTEGER NOT NULL,
    "LyDo"              TEXT    NOT NULL,
    "TrangThai"         TEXT    NOT NULL DEFAULT 'PENDING'
                                CHECK("TrangThai" IN ('PENDING','APPROVED','REJECTED','CANCELLED')),
    "DuyetBoi"          INTEGER REFERENCES "Employees"("EmployeeID"),
    "NgayDuyet"         TIMESTAMP,
    "TaoLuc"            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS "ChatHistory" (
    "ChatID"            BIGSERIAL PRIMARY KEY,
    "SessionID"         TEXT    NOT NULL,
    "NoiDungNguoiDung"  TEXT    NOT NULL,
    "PhanHoiAI"         TEXT    NOT NULL,
    "NhatKyCongCu"      TEXT    NOT NULL DEFAULT '[]',
    "TokenDauVao"       INTEGER NOT NULL DEFAULT 0,
    "TokenDauRa"        INTEGER NOT NULL DEFAULT 0,
    "ThoiGianXuLyMs"    INTEGER NOT NULL DEFAULT 0,
    "TaoLuc"            TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE "Categories" (
        "CategoryID" INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY, 
        "TenDanhMuc" VARCHAR(25), 
        "MoTa" VARCHAR(255) 
);
CREATE TABLE "Customers" (      
    "CustomerID" INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    "TenKhachHang" VARCHAR(50),
    "TenNguoiLienHe" VARCHAR(50),
    "DiaChi" VARCHAR(50),
    "ThanhPho" VARCHAR(20),
    "MaBuuChinh" VARCHAR(10),
    "QuocGia" VARCHAR(15)
);
CREATE TABLE "Shippers"(
    "ShipperID" INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    "TenNguoiGiaoHang" VARCHAR(25),
    "SoDienThoai" VARCHAR(15)
);
CREATE TABLE "Suppliers"(
    "SupplierID" INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    "TenNhaCungCap" VARCHAR(50),
    "TenNguoiLienHe" VARCHAR(50),
    "DiaChi" VARCHAR(50),
    "ThanhPho" VARCHAR(20),
    "MaBuuChinh" VARCHAR(10),
    "QuocGia" VARCHAR(15),
    "SoDienThoai" VARCHAR(15)
);
CREATE TABLE "Products"(
    "ProductID" INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    "TenSanPham" VARCHAR(50),
    "SupplierID" INTEGER,
    "CategoryID" INTEGER,
    "DonVi" VARCHAR(25),
    "Gia" NUMERIC,
    FOREIGN KEY ("CategoryID") REFERENCES "Categories" ("CategoryID"),
    FOREIGN KEY ("SupplierID") REFERENCES "Suppliers" ("SupplierID")
);
CREATE TABLE "Orders"(
    "OrderID" INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    "CustomerID" INTEGER,
    "EmployeeID" INTEGER,
    "NgayDatHang" TIMESTAMP,
    "ShipperID" INTEGER,
    FOREIGN KEY ("EmployeeID") REFERENCES "Employees" ("EmployeeID"),
    FOREIGN KEY ("CustomerID") REFERENCES "Customers" ("CustomerID"),
    FOREIGN KEY ("ShipperID") REFERENCES "Shippers" ("ShipperID")
);
CREATE TABLE "OrderDetails"(
    "OrderDetailID" INTEGER PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    "OrderID" INTEGER,
    "ProductID" INTEGER,
    "Quantity" INTEGER,
    FOREIGN KEY ("OrderID") REFERENCES "Orders" ("OrderID"),
    FOREIGN KEY ("ProductID") REFERENCES "Products" ("ProductID")
);
CREATE INDEX IF NOT EXISTS idx_base_sal_emp     ON "BaseSalary"("EmployeeID", "NgayHieuLuc");
CREATE INDEX IF NOT EXISTS idx_att_emp_date     ON "Attendance"("EmployeeID", "NgayLamViec");
CREATE INDEX IF NOT EXISTS idx_att_date         ON "Attendance"("NgayLamViec");
CREATE INDEX IF NOT EXISTS idx_att_ditre        ON "Attendance"("DiTre");
CREATE INDEX IF NOT EXISTS idx_sal_emp_period   ON "SalaryHistory"("EmployeeID", "NamKy", "ThangKy");
CREATE INDEX IF NOT EXISTS idx_leave_emp        ON "LeaveRequests"("EmployeeID");
CREATE INDEX IF NOT EXISTS idx_leave_status     ON "LeaveRequests"("TrangThai");
CREATE INDEX IF NOT EXISTS idx_chat_session     ON "ChatHistory"("SessionID");
CREATE INDEX IF NOT EXISTS idx_chat_created     ON "ChatHistory"("TaoLuc");
CREATE INDEX IF NOT EXISTS idx_profile_dept     ON "EmployeeProfiles"("DepartmentID");
CREATE INDEX IF NOT EXISTS idx_profile_status   ON "EmployeeProfiles"("TrangThaiLamViec");

CREATE INDEX IF NOT EXISTS idx_categories_tendanhmuc
            ON "Categories" ("TenDanhMuc");
CREATE INDEX IF NOT EXISTS idx_customers_thanhkhang
    ON "Customers" ("TenKhachHang");
CREATE INDEX IF NOT EXISTS idx_customers_thanhpho
    ON "Customers" ("ThanhPho");
CREATE INDEX IF NOT EXISTS idx_shippers_ten
    ON "Shippers" ("TenNguoiGiaoHang");
CREATE INDEX IF NOT EXISTS idx_suppliers_ten
    ON "Suppliers" ("TenNhaCungCap");
CREATE INDEX IF NOT EXISTS idx_suppliers_thanhpho
    ON "Suppliers" ("ThanhPho");
CREATE INDEX IF NOT EXISTS idx_products_supplierid
    ON "Products" ("SupplierID");
CREATE INDEX IF NOT EXISTS idx_products_categoryid
    ON "Products" ("CategoryID");
CREATE INDEX IF NOT EXISTS idx_products_tensanpham
    ON "Products" ("TenSanPham");
CREATE INDEX IF NOT EXISTS idx_orders_customerid
    ON "Orders" ("CustomerID");
CREATE INDEX IF NOT EXISTS idx_orders_employeeid
    ON "Orders" ("EmployeeID");
CREATE INDEX IF NOT EXISTS idx_orders_shipperid
    ON "Orders" ("ShipperID");
CREATE INDEX IF NOT EXISTS idx_orders_ngaydathang
    ON "Orders" ("NgayDatHang");
CREATE INDEX IF NOT EXISTS idx_orderdetails_orderid
    ON "OrderDetails" ("OrderID");
CREATE INDEX IF NOT EXISTS idx_orderdetails_productid
    ON "OrderDetails" ("ProductID");
"""

# ---------------------------------------------------------------------------
# Dữ liệu tham chiếu
# ---------------------------------------------------------------------------
CATEGORIES = [
    ("Đồ Uống", "Nước ngọt, cà phê, trà, bia, rượu"),
    ("Gia Vị & Nước Chấm", "Nước mắm, tương ớt, gia vị khô, nước sốt"),
    ("Bánh Kẹo", "Bánh ngọt, kẹo, mứt, socola"),
    ("Sản Phẩm Từ Sữa", "Sữa tươi, phô mai, sữa chua, bơ"),
    ("Ngũ Cốc & Bánh Mì", "Bánh mì, ngũ cốc, mì gói, bún khô"),
    ("Hải Sản", "Cá, tôm, cua, mực đông lạnh"),
    ("Thịt Tươi Sống", "Thịt heo, thịt bò, thịt gà"),
    ("Rau Củ Quả", "Rau xanh, củ quả, trái cây tươi"),
]
SUPPLIER_NAMES = [
    "Công ty TNHH Thực Phẩm Miền Nam", "Công ty CP Nông Sản Việt",
    "Công ty TNHH XNK Hải Sản Bình Minh", "Công ty CP Thực Phẩm An Gia",
    "Công ty TNHH Chế Biến Nông Sản Tân Phú", "Công ty CP Sữa Việt Xanh",
    "Công ty TNHH Bánh Kẹo Hồng Phát", "Công ty CP Gia Vị Á Đông",
    "Công ty TNHH Thủy Sản Sông Hậu", "Công ty CP Thực Phẩm Sài Gòn Food",
    "Công ty TNHH XNK Nông Sản Đồng Bằng", "Công ty CP Đồ Uống Việt Phát",
    "Công ty TNHH Thực Phẩm Sạch Ba Miền", "Công ty CP Chế Biến Thịt Vissan Nhỏ",
    "Công ty TNHH Nông Sản Đà Lạt Xanh",
]
SHIPPER_NAMES = [
    "Giao Hàng Nhanh", "Giao Hàng Tiết Kiệm", "Viettel Post",
    "VNPost", "J&T Express", "Ninja Van", "Ahamove", "ShopeeExpress",
]
DEPARTMENTS = [
    ("Ban Giám Đốc",              None,               "CC-000"),
    ("Kỹ Thuật",                  None,               "CC-100"),
    ("Lập Trình Frontend",        "Kỹ Thuật",         "CC-101"),
    ("Lập Trình Backend",         "Kỹ Thuật",         "CC-102"),
    ("Kiểm Thử Chất Lượng",       "Kỹ Thuật",         "CC-103"),
    ("Vận Hành Hệ Thống",         "Kỹ Thuật",         "CC-104"),
    ("Sản Phẩm",                  None,               "CC-200"),
    ("Quản Lý Sản Phẩm",          "Sản Phẩm",         "CC-201"),
    ("Thiết Kế UI/UX",            "Sản Phẩm",         "CC-202"),
    ("Kinh Doanh",                None,               "CC-300"),
    ("Kinh Doanh Doanh Nghiệp",   "Kinh Doanh",       "CC-301"),
    ("Kinh Doanh SMB",            "Kinh Doanh",       "CC-302"),
    ("Marketing",                 None,               "CC-400"),
    ("Marketing Kỹ Thuật Số",     "Marketing",        "CC-401"),
    ("Nội Dung & Thương Hiệu",    "Marketing",        "CC-402"),
    ("Tài Chính",                 None,               "CC-500"),
    ("Kế Toán",                   "Tài Chính",        "CC-501"),
    ("Hoạch Định Tài Chính",      "Tài Chính",        "CC-502"),
    ("Nhân Sự",                   None,               "CC-600"),
    ("Tuyển Dụng",                "Nhân Sự",          "CC-601"),
    ("Hành Chính Nhân Sự",        "Nhân Sự",          "CC-602"),
    ("Chăm Sóc Khách Hàng",       None,               "CC-700"),
    ("Pháp Chế & Tuân Thủ",       None,               "CC-800"),
]

# (luong_min, luong_max, di_lai, an_trua, suc_khoe) — VND
GRADE_SALARY = {
    "L1": (  5_500_000,   8_000_000,  300_000,   500_000,  200_000),
    "L2": (  8_000_000,  13_000_000,  500_000,   700_000,  300_000),
    "L3": ( 13_000_000,  20_000_000,  700_000,   800_000,  500_000),
    "L4": ( 20_000_000,  32_000_000,  900_000, 1_000_000,  700_000),
    "L5": ( 32_000_000,  55_000_000, 1_200_000, 1_500_000, 1_000_000),
    "L6": ( 55_000_000, 120_000_000, 2_000_000, 2_000_000, 2_000_000),
}

DEPT_POSITIONS = {
    "Ban Giám Đốc":            [("Tổng Giám Đốc", "L6"), ("Phó Tổng Giám Đốc Kỹ Thuật", "L6"), ("Phó Tổng Giám Đốc Vận Hành", "L6")],
    "Lập Trình Frontend":      [("Lập Trình Viên Frontend", "L1"), ("Lập Trình Viên Frontend Cao Cấp", "L2"), ("Trưởng Nhóm Frontend", "L3"), ("Trưởng Bộ Phận Frontend", "L4")],
    "Lập Trình Backend":       [("Lập Trình Viên Backend", "L1"), ("Lập Trình Viên Backend Cao Cấp", "L2"), ("Trưởng Nhóm Backend", "L3"), ("Trưởng Bộ Phận Backend", "L4"), ("Kỹ Sư Trưởng", "L5")],
    "Kiểm Thử Chất Lượng":     [("Kỹ Sư Kiểm Thử", "L2"), ("Kỹ Sư Kiểm Thử Cao Cấp", "L3"), ("Trưởng Nhóm QA", "L4")],
    "Vận Hành Hệ Thống":       [("Kỹ Sư DevOps", "L2"), ("Kỹ Sư DevOps Cao Cấp", "L3"), ("Trưởng Nhóm Vận Hành", "L4")],
    "Quản Lý Sản Phẩm":        [("Quản Lý Sản Phẩm Junior", "L2"), ("Quản Lý Sản Phẩm", "L3"), ("Quản Lý Sản Phẩm Cao Cấp", "L4"), ("Giám Đốc Sản Phẩm", "L5")],
    "Thiết Kế UI/UX":          [("Thiết Kế Viên", "L2"), ("Thiết Kế Viên Cao Cấp", "L3"), ("Trưởng Nhóm Thiết Kế", "L4")],
    "Kinh Doanh Doanh Nghiệp": [("Chuyên Viên Kinh Doanh", "L2"), ("Chuyên Viên Kinh Doanh Cao Cấp", "L3"), ("Giám Đốc Kinh Doanh Vùng", "L4")],
    "Kinh Doanh SMB":          [("Nhân Viên Kinh Doanh", "L1"), ("Chuyên Viên Kinh Doanh SMB", "L2"), ("Trưởng Nhóm Kinh Doanh", "L3")],
    "Marketing Kỹ Thuật Số":   [("Chuyên Viên Marketing", "L2"), ("Chuyên Viên Marketing Cao Cấp", "L3"), ("Trưởng Nhóm Marketing", "L4")],
    "Nội Dung & Thương Hiệu":  [("Biên Tập Viên", "L1"), ("Chuyên Viên Nội Dung", "L2"), ("Quản Lý Thương Hiệu", "L3")],
    "Kế Toán":                 [("Kế Toán Viên", "L2"), ("Kế Toán Viên Cao Cấp", "L3"), ("Kế Toán Trưởng", "L4")],
    "Hoạch Định Tài Chính":    [("Chuyên Viên Phân Tích Tài Chính", "L2"), ("Chuyên Viên Tài Chính Cao Cấp", "L3"), ("Trưởng Phòng Tài Chính", "L4")],
    "Tuyển Dụng":              [("Chuyên Viên Tuyển Dụng", "L2"), ("Chuyên Viên Tuyển Dụng Cao Cấp", "L3"), ("Trưởng Phòng Tuyển Dụng", "L4")],
    "Hành Chính Nhân Sự":      [("Chuyên Viên Nhân Sự", "L2"), ("Chuyên Viên Nhân Sự Cao Cấp", "L3"), ("Trưởng Phòng Nhân Sự", "L4")],
    "Chăm Sóc Khách Hàng":     [("Chuyên Viên CSKH", "L2"), ("Chuyên Viên CSKH Cao Cấp", "L3"), ("Trưởng Nhóm CSKH", "L4")],
    "Pháp Chế & Tuân Thủ":     [("Chuyên Viên Pháp Chế", "L3"), ("Chuyên Viên Pháp Chế Cao Cấp", "L4"), ("Trưởng Phòng Pháp Chế", "L5")],
    "Kỹ Thuật":                [("Giám Đốc Kỹ Thuật", "L5")],
    "Kinh Doanh":              [("Giám Đốc Kinh Doanh", "L5")],
    "Marketing":               [("Giám Đốc Marketing", "L5")],
    "Tài Chính":               [("Giám Đốc Tài Chính", "L6"), ("Phó Giám Đốc Tài Chính", "L5")],
    "Nhân Sự":                 [("Giám Đốc Nhân Sự", "L5")],
    "Sản Phẩm":                [("Giám Đốc Sản Phẩm", "L5")],
}

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng",
      "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Trịnh", "Lưu", "Trương"]

TEN_DEM_NAM = ["Văn", "Đức", "Quốc", "Minh", "Thanh", "Tuấn", "Hoàng", "Anh", "Trọng", "Hữu",
               "Quang", "Duy", "Mạnh", "Tiến", "Long", "Hùng", "Khánh", "Việt", "Thái", "Bảo"]

TEN_NAM = ["An", "Bình", "Cường", "Đạt", "Phong", "Giang", "Hiền", "Khoa", "Lâm",
           "Nam", "Nghĩa", "Phúc", "Sơn", "Tài", "Vinh", "Xuân", "Hào", "Lộc",
           "Kiên", "Toàn", "Dũng", "Nhân", "Huy", "Luân", "Bách", "Tín", "Khải", "Hưng"]

TEN_DEM_NU = ["Thị", "Ngọc", "Bích", "Kiều", "Thanh", "Kim", "Lan", "Mai", "Hồng", "Thu",
              "Phương", "Hương", "Hạnh", "Yến", "Linh", "Hoa", "Quỳnh", "Bảo", "Diễm", "Xuân"]

TEN_NU = ["An", "Bình", "Chi", "Đào", "Giang", "Hà", "Hiền", "Hương", "Lan", "Linh",
          "Mai", "Nga", "Ngân", "Nhung", "Phương", "Quỳnh", "Thảo", "Trang", "Vy", "Yến",
          "Hoa", "Lý", "Mỹ", "Nhi", "Tâm", "Thủy", "Trâm", "Uyên", "Xuân", "Trúc"]

TINH_THANH = ["Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", "Hải Phòng",
              "Biên Hòa", "Huế", "Nha Trang", "Thủ Đức", "Bình Dương"]

DUONG_PHO = [
    "Nguyễn Huệ", "Lê Lợi", "Trần Hưng Đạo", "Hai Bà Trưng",
    "Võ Văn Tần", "Điện Biên Phủ", "Nam Kỳ Khởi Nghĩa", "Lê Văn Sỹ",
    "Nguyễn Trãi", "Phạm Ngũ Lão", "Lý Tự Trọng", "Đồng Khởi",
    "Hoàng Diệu", "Phan Bội Châu", "Tô Hiệu", "Bạch Đằng",
    "Nguyễn Thị Minh Khai", "Cách Mạng Tháng 8", "Lê Duẩn", "Quang Trung",
]

NGAN_HANG = ["Vietcombank", "Techcombank", "BIDV", "VietinBank", "MB Bank",
             "ACB", "VPBank", "Sacombank", "HDBank", "TPBank"]

LY_DO_NGHI = {
    "ANNUAL":    ["Nghỉ du lịch cùng gia đình", "Nghỉ phép nhân dịp sinh nhật",
                  "Về quê thăm gia đình", "Nghỉ dưỡng sức sau dự án lớn", "Đi dự đám cưới bạn bè"],
    "SICK":      ["Bị sốt cao và cảm cúm", "Rối loạn tiêu hóa", "Điều trị răng miệng",
                  "Khám sức khỏe định kỳ", "Nghỉ dưỡng sau phẫu thuật nhỏ"],
    "PERSONAL":  ["Giải quyết việc gia đình khẩn cấp", "Chuyển nhà", "Tham dự đám cưới",
                  "Làm thủ tục hành chính", "Đưa con nhập học"],
    "MATERNITY": ["Nghỉ thai sản theo Luật Lao Động (6 tháng)"],
    "PATERNITY": ["Hỗ trợ vợ sau sinh (5 ngày theo luật)"],
    "UNPAID":    ["Nghỉ không hưởng lương để học cao học", "Đi nước ngoài công tác cá nhân"],
}

CHAT_SAMPLES = [
    (
        "Cho tôi xem 10 nhân viên có lương cao nhất tháng này",
        "Dựa trên dữ liệu SalaryHistory tháng 6/2025, đây là 10 nhân viên có lương thực nhận cao nhất:\n\n"
        "| # | Họ Tên | Phòng Ban | Chức Vụ | Lương Thực Nhận |\n"
        "|---|--------|-----------|---------|----------------|\n"
        "| 1 | Nguyễn Văn An | Ban Giám Đốc | Tổng Giám Đốc | 115.000.000 ₫ |\n"
        "| 2 | Trần Thị Bích | Ban Giám Đốc | Phó Tổng Giám Đốc Kỹ Thuật | 98.500.000 ₫ |"
    ),
    (
        "Tổng chi phí lương công ty tháng 1 năm 2025 là bao nhiêu?",
        "Tổng chi phí lương tháng 1/2025 của công ty là **2.847.500.000 ₫** cho 97 nhân viên đang làm việc."
    ),
    (
        "Những nhân viên nào chưa được duyệt đơn nghỉ phép?",
        "Hiện có **23 đơn xin nghỉ phép** đang ở trạng thái PENDING, trong đó:\n"
        "- ANNUAL: 14 đơn\n- SICK: 6 đơn\n- PERSONAL: 3 đơn\n\n"
        "Nhân viên chờ duyệt lâu nhất là Phạm Minh Khoa (đơn từ 3 ngày trước)."
    ),
    (
        "Báo cáo chấm công tuần này thế nào?",
        "**Báo cáo chấm công tuần 24/2025 (9/6 – 13/6):**\n\n"
        "- PRESENT: 89 nhân viên\n- REMOTE: 18 nhân viên\n"
        "- ON_LEAVE: 7 nhân viên\n- ABSENT: 2 nhân viên\n"
        "- Tỉ lệ: OFFICE 72% | REMOTE 23% | BUSINESS_TRIP 5%"
    ),
    (
        "Phòng ban nào có số nhân viên đông nhất?",
        "Theo dữ liệu hiện tại:\n\n"
        "1. **Lập Trình Backend** — 12 nhân viên\n"
        "2. **Kinh Doanh SMB** — 11 nhân viên\n"
        "3. **Lập Trình Frontend** — 9 nhân viên\n"
        "4. **Kiểm Thử Chất Lượng** — 8 nhân viên\n"
        "5. **Chăm Sóc Khách Hàng** — 8 nhân viên"
    ),
    (
        "Nhân viên nào có số ngày đi trễ nhiều nhất trong tháng 5?",
        "Trong tháng 5/2025, top 3 nhân viên đi trễ nhiều nhất:\n\n"
        "1. Lê Thị Hương (Kế Toán) — 8 lần trễ, trung bình 22 phút/lần\n"
        "2. Võ Quốc Hùng (Kinh Doanh SMB) — 6 lần trễ, trung bình 35 phút/lần\n"
        "3. Bùi Văn Nam (Lập Trình Frontend) — 5 lần trễ, trung bình 18 phút/lần"
    ),
    (
        "Tổng số nhân viên đang nghỉ thai sản hiện tại?",
        "Hiện tại có **3 nhân viên** đang trong thời gian nghỉ MATERNITY:\n\n"
        "- Nguyễn Thị Lan (Kế Toán) — nghỉ từ 15/3/2025, dự kiến quay lại 15/9/2025\n"
        "- Trần Ngọc Quỳnh (Nhân Sự) — nghỉ từ 1/4/2025\n"
        "- Phạm Thị Mai (Chăm Sóc Khách Hàng) — nghỉ từ 20/4/2025"
    ),
    (
        "Chi phí lương phòng Kỹ Thuật 6 tháng đầu 2025 là bao nhiêu?",
        "Tổng chi phí lương phòng Kỹ Thuật 6 tháng đầu 2025:\n\n"
        "| Phòng Ban | Nhân Viên | Tổng Lương |\n"
        "|-----------|-----------|------------|\n"
        "| Lập Trình Backend | 12 | 1.240.000.000 ₫ |\n"
        "| Lập Trình Frontend | 9 | 820.000.000 ₫ |\n"
        "| Kiểm Thử Chất Lượng | 8 | 580.000.000 ₫ |\n"
        "| Vận Hành Hệ Thống | 6 | 510.000.000 ₫ |\n"
        "| **Tổng** | **35** | **3.150.000.000 ₫** |"
    ),
    (
        "Nhân viên nào có hợp đồng sắp hết hạn trong 30 ngày tới?",
        "Có **4 nhân viên** CONTRACT hết hạn trong 30 ngày tới:\n\n"
        "1. Hoàng Đức Vinh (Kinh Doanh SMB) — hết hạn 25/6/2025\n"
        "2. Đỗ Thị Nga (Marketing) — hết hạn 28/6/2025\n"
        "3. Ngô Minh Tuấn (Lập Trình Backend) — hết hạn 5/7/2025\n"
        "4. Lý Thị Yến (Kế Toán) — hết hạn 10/7/2025"
    ),
    (
        "Tỉ lệ nghỉ phép theo loại năm 2024?",
        "Phân tích đơn nghỉ phép năm 2024:\n\n"
        "- ANNUAL: 145 đơn (41%) — trung bình 3,2 ngày/đơn\n"
        "- SICK: 98 đơn (28%) — trung bình 1,8 ngày/đơn\n"
        "- PERSONAL: 67 đơn (19%)\n"
        "- MATERNITY / PATERNITY: 18 đơn (5%)\n"
        "- UNPAID: 24 đơn (7%)\n\n"
        "Tỉ lệ APPROVED: **72%** | REJECTED: 11% | PENDING: còn lại"
    ),
]
PRODUCT_NAMES_BY_CATEGORY = {
    "Đồ Uống": [
        "Cà Phê Sữa Đá Đóng Chai", "Trà Xanh Không Độ", "Nước Ngọt Có Gas",
        "Bia Lon", "Nước Suối Tinh Khiết", "Trà Đào Cam Sả", "Nước Ép Trái Cây",
        "Sữa Đậu Nành Đóng Hộp",
    ],
    "Gia Vị & Nước Chấm": [
        "Nước Mắm Phú Quốc", "Tương Ớt Chin-su", "Nước Tương Đậu Nành",
        "Muối Tôm Tây Ninh", "Bột Ngọt", "Hạt Nêm Từ Thịt", "Sa Tế Tôm",
        "Dầu Hào",
    ],
    "Bánh Kẹo": [
        "Bánh Pía Sóc Trăng", "Kẹo Dừa Bến Tre", "Bánh Trung Thu",
        "Socola Sữa", "Mứt Gừng", "Bánh Quy Bơ", "Kẹo Lạc",
    ],
    "Sản Phẩm Từ Sữa": [
        "Sữa Tươi Tiệt Trùng", "Phô Mai Con Bò Cười", "Sữa Chua Có Đường",
        "Bơ Lạt", "Sữa Đặc Ông Thọ", "Kem Tươi Whipping",
    ],
    "Ngũ Cốc & Bánh Mì": [
        "Bánh Mì Sandwich", "Mì Gói Hảo Hảo", "Bún Khô",
        "Ngũ Cốc Ăn Sáng", "Miến Dong", "Phở Khô Gia Lai", "Bột Mì Đa Dụng",
    ],
    "Hải Sản": [
        "Tôm Sú Đông Lạnh", "Cá Basa Fillet", "Mực Ống Tươi",
        "Cua Biển Cà Mau", "Chả Cá Thác Lác", "Cá Hồi Nhập Khẩu",
    ],
    "Thịt Tươi Sống": [
        "Thịt Ba Chỉ Heo", "Thịt Bò Úc", "Ức Gà Phi Lê",
        "Sườn Non Heo", "Cánh Gà Đông Lạnh", "Chân Giò Heo",
    ],
    "Rau Củ Quả": [
        "Cà Chua Đà Lạt", "Khoai Tây Đà Lạt", "Xà Lách Xoong",
        "Cải Thìa", "Bí Đỏ", "Dưa Leo", "Cam Sành", "Xoài Cát Chu",
    ],
}
 
DON_VI_OPTIONS = ["chai", "hộp", "gói", "kg", "thùng", "lon", "bó"]
 
CUSTOMER_COMPANY_NAMES = [
    "Công ty TNHH Thương Mại Phú Thịnh", "Cửa Hàng Tạp Hóa Minh Anh",
    "Siêu Thị Mini Gia Đình", "Công ty CP Bán Lẻ Việt Star",
    "Cửa Hàng Thực Phẩm Sạch Xanh", "Công ty TNHH Dịch Vụ Ẩm Thực Hoa Mai",
    "Nhà Hàng Sen Vàng", "Quán Ăn Ba Miền", "Công ty TNHH XNK Đại Phát",
    "Cửa Hàng Tiện Lợi 24h", "Công ty CP Thương Mại Kim Long",
    "Khách Sạn Hoàng Gia", "Công ty TNHH Bếp Việt", "Quán Cafe Sài Gòn Xưa",
    "Cửa Hàng Bánh Ngọt Hạnh Phúc",
]
 
QUOC_GIA_WEIGHTS = (["Việt Nam"] * 90 + ["Trung Quốc"] * 4 +
                    ["Thái Lan"] * 3 + ["Nhật Bản"] * 2 + ["Hàn Quốc"] * 1)
 
 
def _maBuuChinh() -> str:
    return str(random.randint(70000, 96000))
 
 
def _phoneCoDinh() -> str:
    """Số điện thoại bàn dạng công ty, ví dụ 028xxxxxxxx."""
    maVung = random.choice(["024", "028", "0236", "0251", "0272"])
    return f"{maVung}{random.randint(1000000, 9999999)}"
 
 
def _diaChiNgauNhien() -> str:
    stNum = random.randint(1, 300)
    street = random.choice(DUONG_PHO)
    return f"Số {stNum} {street}"

def getProductOrderEmployees(conn: psycopg.Connection) -> list[int]:
    """
    Trả về danh sách EmployeeID thuộc phòng "Quản Lý Sản Phẩm",
    không bao gồm người giữ chức "Giám Đốc Sản Phẩm".
    (chạy sau khi seedEmployees đã xong)
    """
    cur = conn.cursor()
    cur.execute("""
        SELECT ep."EmployeeID"
        FROM "EmployeeProfiles" ep
        JOIN "Departments" d ON d."DepartmentID" = ep."DepartmentID"
        WHERE d."DepartmentName" = %s
          AND ep."ChucVu" <> %s
    """, ("Quản Lý Sản Phẩm", "Giám Đốc Sản Phẩm"))
    ids = [r[0] for r in cur.fetchall()]
    if not ids:
        raise ValueError(
            "Không tìm thấy nhân viên phù hợp trong phòng 'Quản Lý Sản Phẩm'. "
            "Kiểm tra lại tên phòng ban / chức vụ giám đốc trong DEPT_POSITIONS."
        )
    return ids

# ---------------------------------------------------------------------------
# Reset DB
# ---------------------------------------------------------------------------

def resetDatabase(conn: psycopg.Connection):
    """Xóa toàn bộ bảng (HR mới + Northwind cũ) để tạo lại từ đầu."""

    # PostgreSQL sẽ chuyển tên không có quote thành lowercase.
    # Vì vậy phải dùng tên bảng lowercase để khớp với bảng thật trong public schema.
    for t in ["Chathistory", "LeaveRequests", "Attendance", "SalaryHistory",
              "BaseSalary", "EmployeeProfiles", "Employees", "Departments",
              "Categories","Customers","Shippers","Suppliers","Products","Orders","OrderDetails"]:
        conn.execute(f"DROP TABLE IF EXISTS \"{t}\" CASCADE")
    conn.commit()

    print("  Đã xóa các bảng cũ (bao gồm Northwind).")


# ---------------------------------------------------------------------------
# Hàm sinh dữ liệu
# ---------------------------------------------------------------------------

def makeTenViet(gender: str) -> str:
    """Sinh họ tên Việt đầy đủ theo giới tính."""
    ho = random.choice(HO)
    if gender == "Nam":
        dem = random.choice(TEN_DEM_NAM)
        ten = random.choice(TEN_NAM)
    else:
        dem = random.choice(TEN_DEM_NU)
        ten = random.choice(TEN_NU)
    return f"{ho} {dem} {ten}"


def seedDepartments(conn: psycopg.Connection) -> dict:
    """Tạo 23 phòng ban. Trả về dict {tên: id}."""
    nameToId = {}
    for name, parent, cc in DEPARTMENTS:
        parentId = nameToId.get(parent)
        cur = conn.execute(
            "INSERT INTO \"Departments\" (\"DepartmentName\", \"ParentDepartmentID\", \"CostCenter\") VALUES (%s, %s, %s) RETURNING \"DepartmentID\"",
            (name, parentId, cc)
        )
        nameToId[name] = cur.fetchone()[0]
    conn.commit()
    print(f"  Departments: {len(nameToId)} hàng")
    return nameToId


def seedEmployees(conn: psycopg.Connection, deptNameToId: dict) -> list[int]:
    """
    Tạo 95 nhân viên + hồ sơ HR cho từng người.
    Trả về danh sách EmployeeID.
    """
    cur = conn.cursor()
    topDeptNames = {"Ban Giám Đốc", "Kỹ Thuật", "Kinh Doanh", "Marketing",
                    "Tài Chính", "Nhân Sự", "Sản Phẩm"}
    leafDepts = [d for d in DEPARTMENTS if d[0] in DEPT_POSITIONS and d[0] not in topDeptNames]
    topDepts  = [d for d in DEPARTMENTS if d[0] in DEPT_POSITIONS and d[0] in topDeptNames]

    # Danh sách (dept, pos, grade, gender) cho từng nhân viên
    assignments = []

    # Cấp VP/Giám đốc cho phòng cha
    for deptName, _, _ in topDepts:
        posOptions = DEPT_POSITIONS[deptName]
        pos, grade = posOptions[-1]
        gender = random.choice(["Nam", "Nữ"])
        assignments.append((deptName, pos, grade, gender))

    # Nhân viên phòng lá (3–8 người/phòng, tổng ~95)
    for deptName, _, _ in leafDepts:
        posOptions = DEPT_POSITIONS[deptName]
        count = random.randint(3, 8)
        for _ in range(count):
            if len(assignments) >= 95:
                break
            pos, grade = random.choice(posOptions)
            gender = random.choice(["Nam", "Nữ"])
            assignments.append((deptName, pos, grade, gender))
        if len(assignments) >= 95:
            break

    # Insert Employees
    empRows = []
    for dept, pos, grade, gender in assignments:
        hoTen  = makeTenViet(gender)
        birth  = randomDate(date(1978, 1, 1), date(1999, 12, 31))
        hire   = randomDate(date(2016, 1, 1), date(2024, 3, 31))
        city   = random.choice(TINH_THANH)
        stNum  = random.randint(1, 200)
        street = random.choice(DUONG_PHO)
        addr   = f"Số {stNum} {street}"
        phone  = f"0{random.choice([32,33,34,35,36,37,38,56,58,70,76,77,78,79,89,90,93,94,96,97,98])}{random.randint(1000000,9999999)}"
        empRows.append((hoTen, gender, str(birth), addr, city, phone, str(hire)))

    cur.executemany("""
        INSERT INTO "Employees" ("HoTen", "GioiTinh", "NgaySinh", "DiaChi", "ThanhPho", "SoDienThoai", "NgayVaoLam")
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, empRows)
    conn.commit()

    cur = conn.execute("SELECT \"EmployeeID\", \"NgayVaoLam\" FROM \"Employees\" ORDER BY \"EmployeeID\"")
    allEmp = cur.fetchall()
    allIds = [r[0] for r in allEmp]

    # Pool quản lý mỗi phòng (L4+)
    deptManagers: dict[str, list[int]] = {}
    for i, (dept, pos, grade, gender) in enumerate(assignments):
        eid = allIds[i]
        if grade in ("L4", "L5", "L6"):
            deptManagers.setdefault(dept, []).append(eid)

    # Insert EmployeeProfiles
    usedCCCD  = set()
    usedMST   = set()
    usedEmail = set()
    profileRows = []

    for i, (empId, ngayVao) in enumerate(allEmp):
        dept, pos, grade, gender = assignments[i]
        deptId = deptNameToId[dept]

        # CCCD 12 số
        while True:
            tinh = random.choice(["001", "031", "048", "058", "079", "082", "089", "092"])
            cccd = f"{tinh}{random.randint(0,1)}{random.randint(70,99):02d}{random.randint(100000,999999)}"
            if cccd not in usedCCCD:
                usedCCCD.add(cccd)
                break

        # Mã số thuế cá nhân 10 chữ số
        while True:
            mst = str(random.randint(1000000000, 9999999999))
            if mst not in usedMST:
                usedMST.add(mst)
                break

        # Email công ty (không dấu)
        hoTen = empRows[i][0]
        parts = hoTen.lower().split()

        def removeDiacritics(s):
            import unicodedata
            s = unicodedata.normalize("NFD", s)
            s = "".join(c for c in s if unicodedata.category(c) != "Mn")
            return s.replace("đ", "d")

        cleanParts = [removeDiacritics(p) for p in parts]
        base  = f"{cleanParts[-1]}.{''.join(cleanParts[:-1])}"
        email = f"{base}@datapilot.vn"
        suf = 1
        while email in usedEmail:
            email = f"{base}{suf}@datapilot.vn"
            suf += 1
        usedEmail.add(email)

        # Quản lý trực tiếp
        candidates = [m for m in deptManagers.get(dept, []) if m != empId]
        managerId  = random.choice(candidates) if candidates else None

        # Trạng thái làm việc
        status = weightedChoice(["ACTIVE", "RESIGNED", "PENDING_TERMINATION"], [93, 5, 2])
        ngayNghi = None
        if status in ("RESIGNED", "PENDING_TERMINATION"):
            hd = ngayVao if ngayVao else date(2018, 1, 1)
            ngayNghi = str(randomDate(hd + timedelta(days=180), date(2025, 1, 1)))

        empType  = weightedChoice(["FULL_TIME", "CONTRACT", "PROBATION"], [68, 22, 10])
        marital  = weightedChoice(["MARRIED", "SINGLE", "DIVORCED"], [58, 37, 5])
        bank     = random.choice(NGAN_HANG)
        acct     = str(random.randint(1000000000000, 9999999999999))

        # Người liên hệ khẩn cấp
        hoKC  = random.choice(HO)
        tenKC = random.choice(TEN_NU if gender == "Nam" else TEN_NAM)
        phKC  = f"0{random.choice([90,91,94,96,97,98])}{random.randint(1000000,9999999)}"
        nguoiKC = f"{hoKC} {tenKC} — {phKC}"

        phoneWork = f"0{random.choice([32,33,34,35,36,37,38,56,58,70,76,77,78,79,89,90,93,94,96,97,98])}{random.randint(1000000,9999999)}"

        profileRows.append((
            empId, deptId, cccd, marital, empType, status,
            ngayVao, ngayNghi, pos, grade, managerId,
            email, phoneWork, nguoiKC, acct, bank, mst, 12, 12
        ))

    cur.executemany("""
        INSERT INTO "EmployeeProfiles"
        ("EmployeeID", "DepartmentID", "CCCD", "TinhTrangHonNhan", "LoaiHopDong", "TrangThaiLamViec",
         "NgayVao", "NgayNghi", "ChucVu", "CapBac", "QuanLyTrucTiepID", "EmailCongTy",
         "SoDienThoaiCongTy", "NguoiLienHeKhánCap", "SoTaiKhoanNganHang", "TenNganHang",
         "MaSoThue", "SoNgayPhepNam", "SoNgayPhepBenh")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, profileRows)
    conn.commit()

    print(f"  Employees: {len(allIds)} người")
    print(f"  EmployeeProfiles: {len(profileRows)} hàng")
    return allIds


def seedBaseSalary(conn: psycopg.Connection, employeeIds: list[int]) -> dict:
    """
    Tạo lịch sử lương cứng cho mỗi nhân viên.
    Mỗi người có 1–2 mốc: lương ban đầu (khi vào) + tăng lương 8% từ 01/01/2025.
    Trả về dict {EmployeeID: [(NgayHieuLuc, BaseSalaryID, LuongCoBan, diLai, anTrua, sucKhoe)]}.
    """
    cur = conn.execute('SELECT "EmployeeID", "CapBac", "TrangThaiLamViec", "NgayVao" FROM "EmployeeProfiles"')
    profiles = {r[0]: (r[1], r[2], r[3]) for r in cur.fetchall()}

    rows = []
    # (eid, ngayHieuLuc, luong, diLai, anTrua, sucKhoe, ghiChu)
    for eid in employeeIds:
        if eid not in profiles:
            continue
        grade, status, ngayVao = profiles[eid]
        if grade not in GRADE_SALARY:
            grade = "L2"
        bMin, bMax, diLai, anTrua, sucKhoe = GRADE_SALARY[grade]
        luong2024 = round(random.uniform(bMin, bMax) / 500_000) * 500_000

        joinDt = ngayVao if ngayVao else date(2018, 1, 1)
        # Mốc 1: lương khi vào làm (hoặc đầu 2024 nếu vào trước đó)
        hieuLuc1 = max(joinDt, date(2024, 1, 1))
        rows.append((eid, str(hieuLuc1), luong2024, diLai, anTrua, sucKhoe, "Lương khởi điểm"))

        # Mốc 2: tăng lương 8% từ 01/01/2025 (chỉ nhân viên còn làm)
        if status != "RESIGNED":
            luong2025 = round(luong2024 * 1.08 / 500_000) * 500_000
            rows.append((eid, "2025-01-01", luong2025, diLai, anTrua, sucKhoe, "Điều chỉnh lương năm 2025 (+8%)"))

    cur.executemany("""
        INSERT INTO "BaseSalary"
        ("EmployeeID", "NgayHieuLuc", "LuongCoBan", "PhuCapDiLai", "PhuCapAnTrua", "PhuCapSucKhoe", "GhiChu")
        VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
    """, rows)
    conn.commit()

    # Trả về map để seedSalaryHistory dùng: {eid: [(hieuLuc, bsId, luong, diLai, anTrua, sucKhoe)]}
    cur = conn.execute("""
        SELECT "BaseSalaryID", "EmployeeID", "NgayHieuLuc", "LuongCoBan",
               "PhuCapDiLai", "PhuCapAnTrua", "PhuCapSucKhoe"
        FROM "BaseSalary" ORDER BY "EmployeeID", "NgayHieuLuc"
    """)
    baseSalaryMap: dict[int, list] = {}
    for bsId, eid, hieuLuc, luong, dl, at, sk in cur.fetchall():
        baseSalaryMap.setdefault(eid, []).append((hieuLuc, bsId, luong, dl, at, sk))

    print(f"  BaseSalary: {len(rows)} hàng ({sum(1 for r in rows if r[6] == 'Lương khởi điểm')} nhân viên, có lịch sử tăng lương)")
    return baseSalaryMap


def seedSalaryHistory(conn: psycopg.Connection, employeeIds: list[int], baseSalaryMap: dict):
    """
    Lương thực nhận hàng tháng Jan 2024 – Jun 2025.
    Lương cứng lấy từ BaseSalary theo NgayHieuLuc gần nhất của kỳ đó.
    Tăng ca và đi trễ lấy tổng từ bảng Attendance của tháng đó.
    """
    cur = conn.execute('SELECT "EmployeeID", "TrangThaiLamViec", "NgayVao" FROM "EmployeeProfiles"')
    profiles = {r[0]: (r[1], r[2]) for r in cur.fetchall()}

    # Tổng hợp chấm công theo (eid, year, month)
    cur = conn.execute("""
        SELECT
            "EmployeeID",
            EXTRACT(YEAR FROM "NgayLamViec")::INTEGER AS Year,
            EXTRACT(MONTH FROM "NgayLamViec")::INTEGER AS Month,
            SUM(CASE WHEN "TrangThai" = 'PRESENT' THEN 1 ELSE 0 END) AS PresentDays,
            SUM("SoPhutDiTre") AS TotalLateMinutes,
            SUM("SoPhutTangCa") AS TotalOvertimeMinutes
        FROM "Attendance"
        GROUP BY
            "EmployeeID",
            EXTRACT(YEAR FROM "NgayLamViec"),
            EXTRACT(MONTH FROM "NgayLamViec")
    """)
    attMap: dict[tuple, tuple] = {}
    for eid, y, m, ngayLam, treGio, tangCa in cur.fetchall():
        attMap[(eid, y, m)] = (ngayLam or 0, treGio or 0, tangCa or 0)

    rows    = []
    periods = [(y, m) for y in (2024, 2025) for m in range(1, 13) if (y, m) <= (2025, 6)]

    for eid in employeeIds:
        if eid not in profiles or eid not in baseSalaryMap:
            continue
        status, ngayVao = profiles[eid]
        joinDt = ngayVao if ngayVao else date(2018, 1, 1)
        bsList = baseSalaryMap[eid]  # đã sắp xếp theo NgayHieuLuc tăng dần

        for year, month in periods:
            periodStart = date(year, month, 1)
            if periodStart < joinDt:
                continue
            if status == "RESIGNED" and periodStart > date(2024, 12, 1):
                continue

            # Chọn BaseSalary có NgayHieuLuc <= đầu kỳ, gần nhất
            applicable = [(hl, bsId, l, dl, at, sk) for hl, bsId, l, dl, at, sk in bsList
                          if hl <= periodStart]
            if not applicable:
                continue
            hieuLuc, bsId, luong, diLai, anTrua, sucKhoe = applicable[-1]

            ngayLam, treGioPhut, tangCaPhut = attMap.get((eid, year, month), (22, 0, 0))

            # Phụ cấp tăng ca: 1.5× lương giờ cho số phút tăng ca
            luongGio   = luong / 22 / 8  # lương 1 giờ (22 ngày công, 8h/ngày)
            phuCapTangCa = round(tangCaPhut / 60 * float(luongGio) * 1.5 / 10_000) * 10_000
            # Khấu trừ đi trễ: trừ theo phút thực tế (tính theo lương giờ)
            khauTruDiTre = round(treGioPhut / 60 * float(luongGio) / 10_000) * 10_000

            # Thưởng hiệu quả: 25% tháng có, mức 5–15% lương
            thuong = round(random.uniform(float(luong) * 0.05, float(luong) * 0.15) / 100_000) * 100_000 if random.random() < 0.25 else 0

            # Thuế TNCN đơn giản hóa (5% trên thu nhập > 11 triệu)
            thuNhapTinh = float(luong) + float(thuong) - 11_000_000
            khauTruThue = round(max(0, float(thuNhapTinh) * 0.05) / 10_000) * 10_000

            # BHXH nhân viên đóng 10.5%
            bhxh = round(float(luong) * 0.105 / 10_000) * 10_000

            net = (luong + diLai + anTrua + sucKhoe + thuong + phuCapTangCa
                   - khauTruDiTre - khauTruThue - bhxh)

            rows.append((eid, bsId, year, month, ngayLam, treGioPhut, tangCaPhut,
                         luong, diLai, anTrua, sucKhoe, thuong, phuCapTangCa,
                         khauTruDiTre, khauTruThue, bhxh, net, str(date(year, month, 25))))

    # Sắp xếp theo kỳ lương (năm, tháng) để SalaryID tăng dần theo thời gian
    rows.sort(key=lambda r: (r[2], r[3]))

    cur.executemany("""
        INSERT INTO "SalaryHistory"
        ("EmployeeID", "BaseSalaryID", "NamKy", "ThangKy", "SoNgayLamViec", "SoPhutTreGioTong", "SoPhutTangCaTong",
         "LuongCoBan", "PhuCapDiLai", "PhuCapAnTrua", "PhuCapSucKhoe", "ThuongHieuQua", "PhuCapTangCa",
         "KhauTruDiTre", "KhauTruThue", "KhauTruBHXH", "LuongThucNhan", "NgayThanhToan")
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
    """, rows)
    conn.commit()
    print(f"  SalaryHistory: {len(rows)} hàng (18 tháng × ~{len(employeeIds)} nhân viên)")


def seedAttendance(conn: psycopg.Connection, employeeIds: list[int]):
    """
    Chấm công T2–T6, giờ làm 9:00–18:00, Jan–Jun 2025.
    DiTre=1 chỉ khi đến sau 9:00, SoPhutDiTre > 0.
    DiTre=0 thì SoPhutDiTre = 0.
    Tăng ca khi ra sau 18:00.
    """
    cur = conn.execute('SELECT "EmployeeID", "TrangThaiLamViec" FROM "EmployeeProfiles"')
    statusMap = {r[0]: r[1] for r in cur.fetchall()}

    start = date(2025, 1, 1)
    end   = date(2025, 6, 30)

    ngayLe = {
        date(2025, 1, 1),   # Tết Dương Lịch
        date(2025, 1, 27),  # Tết Nguyên Đán (28 tháng Chạp)
        date(2025, 1, 28),  # Tết Nguyên Đán (29 tháng Chạp)
        date(2025, 1, 29),  # Tết Nguyên Đán (Mùng 1)
        date(2025, 1, 30),  # Tết Nguyên Đán (Mùng 2)
        date(2025, 1, 31),  # Tết Nguyên Đán (Mùng 3)
        date(2025, 2, 3),   # Bù Tết
        date(2025, 4, 7),   # Giỗ Tổ Hùng Vương
        date(2025, 4, 30),  # Giải Phóng Miền Nam
        date(2025, 5, 1),   # Quốc Tế Lao Động
    }

    GIO_VAO_CHUAN  = 9   # 09:00
    GIO_RA_CHUAN   = 18  # 18:00

    rows = []
    d = start
    while d <= end:
        isWeekend = d.weekday() >= 5  # T7, CN
        isHoliday = d in ngayLe

        for eid in employeeIds:
            empStatus = statusMap.get(eid, "ACTIVE")
            if empStatus != "ACTIVE" and d > date(2025, 2, 1):
                continue

            if isWeekend:
                rows.append((eid, str(d), None, None, "OFFICE", "WEEKEND", 0, 0, 0, None))
                continue
            if isHoliday:
                rows.append((eid, str(d), None, None, "OFFICE", "HOLIDAY", 0, 0, 0, None))
                continue

            roll = random.random()
            if roll < 0.018:
                rows.append((eid, str(d), None, None, "OFFICE", "ABSENT", 0, 0, 0, None))
            elif roll < 0.048:
                rows.append((eid, str(d), None, None, "OFFICE", "ON_LEAVE", 0, 0, 0, "Nghỉ theo đơn đã duyệt"))
            else:
                workType = weightedChoice(["OFFICE", "REMOTE", "BUSINESS_TRIP"], [62, 33, 5])

                # Giờ vào: 12% đi trễ (9:05–10:00), 10% đến sớm (8:30–8:59), còn lại đúng giờ
                rollIn = random.random()
                if rollIn < 0.12:
                    # Đi trễ: sau 9:00
                    treGioPhut = random.randint(5, 60)
                    totalMin   = GIO_VAO_CHUAN * 60 + treGioPhut
                    hIn, mIn   = totalMin // 60, totalMin % 60
                    diTre      = 1
                elif rollIn < 0.22:
                    # Đến sớm: 8:30–8:59
                    hIn, mIn   = 8, random.randint(30, 59)
                    treGioPhut = 0
                    diTre      = 0
                else:
                    # Đúng giờ: 9:00–9:04
                    hIn, mIn   = GIO_VAO_CHUAN, random.randint(0, 4)
                    treGioPhut = 0
                    diTre      = 0
                checkIn = f"{hIn:02d}:{mIn:02d}:00"

                # Giờ ra: 18:00 đúng giờ, 35% tăng ca đến 18:30–21:00
                rollOut = random.random()
                if rollOut < 0.35:
                    # Tăng ca
                    tangCaPhut = random.randint(30, 180)
                    totalOut   = GIO_RA_CHUAN * 60 + tangCaPhut
                    hOut, mOut = totalOut // 60, totalOut % 60
                else:
                    # Ra đúng giờ: 17:55–18:05
                    hOut, mOut = GIO_RA_CHUAN, random.randint(0, 5)
                    tangCaPhut = 0
                checkOut = f"{hOut:02d}:{mOut:02d}:00"

                rows.append((eid, str(d), checkIn, checkOut, workType, "PRESENT",
                             diTre, treGioPhut, tangCaPhut, None))

        d += timedelta(days=1)

    batch = 5000
    for i in range(0, len(rows), batch):
        cur.executemany("""
            INSERT INTO "Attendance"
            ("EmployeeID", "NgayLamViec", "GioVao", "GioRa", "HinhThucLam", "TrangThai",
             "DiTre", "SoPhutDiTre", "SoPhutTangCa", "GhiChu")
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
        """, rows[i:i+batch])
    conn.commit()
    print(f"  Attendance: {len(rows)} hàng (Jan–Jun 2025, 9h–18h, T2–T6)")


def seedLeaveRequests(conn: psycopg.Connection, employeeIds: list[int]):
    """
    Đơn nghỉ phép 2025 (từ 01/01/2025), đủ loại theo Luật Lao Động VN.
    Luồng thời gian đúng:
      NgayNopDon  = NgayBatDau - random(3..14) ngày (nộp trước)
      NgayDuyet   = NgayNopDon + random(1..3) ngày (duyệt sau khi nộp)
      => NgayDuyet luôn < NgayBatDau
    Người duyệt: QuanLyTrucTiepID → trưởng phòng cùng dept → bất kỳ L5/L6.
    """
    cur = conn.execute("""
        SELECT ep."EmployeeID", ep."QuanLyTrucTiepID", ep."DepartmentID"
        FROM "EmployeeProfiles" ep
        WHERE ep."TrangThaiLamViec" = 'ACTIVE'
    """)
    activeEmps = cur.fetchall()

    # Map dept → danh sách manager (L4+) trong phòng đó
    deptManagers: dict[int, list[int]] = {}
    for eid, capBac, deptId in conn.execute(
        'SELECT "EmployeeID", "CapBac", "DepartmentID" FROM "EmployeeProfiles" WHERE "TrangThaiLamViec"=\'ACTIVE\''
    ):
        if capBac in ("L4", "L5", "L6"):
            deptManagers.setdefault(deptId, []).append(eid)

    # Fallback: bất kỳ L5/L6 nào trong công ty
    seniorPool = [eid for eid, cap, _ in conn.execute(
        'SELECT "EmployeeID", "CapBac", "DepartmentID" FROM "EmployeeProfiles" WHERE "CapBac" IN (\'L5\',\'L6\') AND "TrangThaiLamViec"=\'ACTIVE\''
    )]

    rows = []
    for eid, managerId, deptId in activeEmps:
        # Tìm người duyệt: manager trực tiếp → trưởng phòng cùng dept → senior pool
        if not managerId:
            candidates = [m for m in deptManagers.get(deptId, []) if m != eid]
            managerId  = random.choice(candidates) if candidates else (random.choice(seniorPool) if seniorPool else None)
        numLeaves = random.randint(2, 7)
        for _ in range(numLeaves):
            loai = weightedChoice(
                ["ANNUAL", "SICK", "PERSONAL", "MATERNITY", "PATERNITY", "UNPAID"],
                [40, 28, 18, 5, 2, 7]
            )
            # Nghỉ phép bắt đầu từ 01/01/2025 trở đi
            startDate = randomDate(date(2025, 1, 1), date(2025, 6, 10))

            if loai == "SICK":
                days = random.randint(1, 3)
            elif loai == "MATERNITY":
                days = 180
            elif loai == "PATERNITY":
                days = 5
            elif loai == "ANNUAL":
                days = random.randint(1, 5)
            else:
                days = random.randint(1, 3)

            endDate = startDate + timedelta(days=days - 1)
            lyDo    = random.choice(LY_DO_NGHI[loai])
            status  = weightedChoice(["APPROVED", "REJECTED", "PENDING", "CANCELLED"], [68, 10, 17, 5])

            # Ngày nộp đơn: trước NgayBatDau 3–14 ngày
            ngayNop   = startDate - timedelta(days=random.randint(3, 14))
            # Ngày duyệt: sau ngày nộp 1–3 ngày (chỉ khi APPROVED/REJECTED)
            duyetBoi  = managerId if status in ("APPROVED", "REJECTED") and managerId else None
            ngayDuyet = str(ngayNop + timedelta(days=random.randint(1, 3))) if status in ("APPROVED", "REJECTED") else None
            taoLuc    = str(ngayNop)

            rows.append((eid, loai, str(startDate), str(endDate), days,
                         lyDo, status, duyetBoi, ngayDuyet, taoLuc))

    # Sắp xếp theo ngày nộp đơn (TaoLuc) để LeaveID tăng dần theo thời gian
    rows.sort(key=lambda r: r[9])

    cur.executemany("""
        INSERT INTO "LeaveRequests"
        ("EmployeeID", "LoaiNghi", "NgayBatDau", "NgayKetThuc", "SoNgay",
         "LyDo", "TrangThai", "DuyetBoi", "NgayDuyet", "TaoLuc")
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
    """, rows)
    conn.commit()
    print(f"  LeaveRequests: {len(rows)} hàng")


def seedChatHistory(conn: psycopg.Connection):
    """Lịch sử hội thoại AI mẫu bằng tiếng Việt."""
    cur = conn.cursor()
    rows = []
    for i in range(45):
        sessionId = f"sess-{2025100 + i}"
        msgCount  = random.randint(2, 7)
        createdAt = datetime(2025, random.randint(1, 6), random.randint(1, 28),
                             random.randint(7, 18), random.randint(0, 59), 0)
        for _ in range(msgCount):
            userMsg, aiReply = random.choice(CHAT_SAMPLES)
            hasToolCall = any(w in userMsg.lower() for w in ["lương", "chấm công", "nghỉ phép", "nhân viên"])
            toolLog = '[{"tool":"executeSql","args":{"sql":"SELECT ..."},"result":{"count":10}}]' if hasToolCall else '[]'
            ts = createdAt.isoformat(sep=" ")
            rows.append((sessionId, userMsg, aiReply, toolLog,
                         random.randint(30, 200), random.randint(80, 600),
                         random.randint(600, 6000), ts))

    cur.executemany("""
        INSERT INTO "ChatHistory"
        ("SessionID", "NoiDungNguoiDung", "PhanHoiAI", "NhatKyCongCu",
         "TokenDauVao", "TokenDauRa", "ThoiGianXuLyMs", "TaoLuc")
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING
    """, rows)
    conn.commit()
    print(f"  ChatHistory: {len(rows)} hàng")


def updateHeadCounts(conn: psycopg.Connection):
    """Cập nhật HeadCount theo số nhân viên ACTIVE mỗi phòng."""
    conn.execute("""
        UPDATE "Departments" SET "HeadCount" = (
            SELECT COUNT(*) 
            FROM "EmployeeProfiles" ep
            WHERE ep."DepartmentID" = "Departments"."DepartmentID"
            AND ep."TrangThaiLamViec" = 'ACTIVE'
        )
    """)
    conn.commit()



def execute_schema(conn: psycopg.Connection, schema_sql: str):
    """Chạy schema SQL theo từng câu lệnh để PostgreSQL có thể thực thi."""
    statements = [stmt.strip() for stmt in schema_sql.split(";") if stmt.strip()]
    for stmt in statements:
        conn.execute(stmt)
    conn.commit()

def seedCategories(conn: psycopg.Connection) -> dict:
    """Tạo danh mục sản phẩm. Trả về dict TenDanhMuc -> CategoryID."""
    cur = conn.cursor()
    cur.executemany("""
        INSERT INTO "Categories" ("TenDanhMuc", "MoTa")
        VALUES (%s, %s)
    """, CATEGORIES)
    conn.commit()
 
    cur.execute('SELECT "CategoryID", "TenDanhMuc" FROM "Categories"')
    nameToId = {name: cid for cid, name in cur.fetchall()}
    print(f"  Categories: {len(nameToId)} danh mục")
    return nameToId

def seedSuppliers(conn: psycopg.Connection) -> list[int]:
    """Tạo nhà cung cấp. Trả về danh sách SupplierID."""
    cur = conn.cursor()
    rows = []
    for tenNCC in SUPPLIER_NAMES:
        gender = random.choice(["Nam", "Nữ"])
        tenLienHe = makeTenViet(gender)
        city = random.choice(TINH_THANH)
        rows.append((
            tenNCC, tenLienHe, _diaChiNgauNhien(), city,
            _maBuuChinh(), random.choices(QUOC_GIA_WEIGHTS)[0],
            _phoneCoDinh(),
        ))
 
    cur.executemany("""
        INSERT INTO "Suppliers"
        ("TenNhaCungCap", "TenNguoiLienHe", "DiaChi", "ThanhPho",
         "MaBuuChinh", "QuocGia", "SoDienThoai")
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, rows)
    conn.commit()
 
    cur.execute('SELECT "SupplierID" FROM "Suppliers" ORDER BY "SupplierID"')
    ids = [r[0] for r in cur.fetchall()]
    print(f"  Suppliers: {len(ids)} nhà cung cấp")
    return ids
 
def seedShippers(conn: psycopg.Connection) -> list[int]:
    """Tạo đơn vị vận chuyển. Trả về danh sách ShipperID."""
    cur = conn.cursor()
    rows = []
    for ten in SHIPPER_NAMES:
        phone = f"1900{random.randint(100000, 999999)}"
        rows.append((ten, phone))
 
    cur.executemany("""
        INSERT INTO "Shippers" ("TenNguoiGiaoHang", "SoDienThoai")
        VALUES (%s, %s)
    """, rows)
    conn.commit()
 
    cur.execute('SELECT "ShipperID" FROM "Shippers" ORDER BY "ShipperID"')
    ids = [r[0] for r in cur.fetchall()]
    print(f"  Shippers: {len(ids)} đơn vị vận chuyển")
    return ids

def seedCustomers(conn: psycopg.Connection, count: int = 60) -> list[int]:
    """Tạo khách hàng (công ty + cá nhân). Trả về danh sách CustomerID."""
    cur = conn.cursor()
    rows = []
    for _ in range(count):
        isCongTy = random.random() < 0.6
        gender = random.choice(["Nam", "Nữ"])
        tenLienHe = makeTenViet(gender)
        if isCongTy:
            tenKH = random.choice(CUSTOMER_COMPANY_NAMES)
        else:
            tenKH = tenLienHe  # khách hàng cá nhân dùng luôn tên làm TenKhachHang
 
        city = random.choice(TINH_THANH)
        rows.append((
            tenKH, tenLienHe, _diaChiNgauNhien(), city,
            _maBuuChinh(), "Việt Nam",
        ))
 
    cur.executemany("""
        INSERT INTO "Customers"
        ("TenKhachHang", "TenNguoiLienHe", "DiaChi", "ThanhPho",
         "MaBuuChinh", "QuocGia")
        VALUES (%s, %s, %s, %s, %s, %s)
    """, rows)
    conn.commit()
 
    cur.execute('SELECT "CustomerID" FROM "Customers" ORDER BY "CustomerID"')
    ids = [r[0] for r in cur.fetchall()]
    print(f"  Customers: {len(ids)} khách hàng")
    return ids

def seedProducts(conn: psycopg.Connection, categoryNameToId: dict,
                  supplierIds: list[int]) -> list[int]:
    """Tạo sản phẩm cho từng danh mục. Trả về danh sách ProductID."""
    cur = conn.cursor()
    rows = []
    for tenDanhMuc, productNames in PRODUCT_NAMES_BY_CATEGORY.items():
        categoryId = categoryNameToId[tenDanhMuc]
        for tenSP in productNames:
            supplierId = random.choice(supplierIds)
            donVi = random.choice(DON_VI_OPTIONS)
            gia = round(random.uniform(8000, 450000), -2)  # làm tròn hàng trăm
            rows.append((tenSP, supplierId, categoryId, donVi, gia))
 
    cur.executemany("""
        INSERT INTO "Products"
        ("TenSanPham", "SupplierID", "CategoryID", "DonVi", "Gia")
        VALUES (%s, %s, %s, %s, %s)
    """, rows)
    conn.commit()
 
    cur.execute('SELECT "ProductID" FROM "Products" ORDER BY "ProductID"')
    ids = [r[0] for r in cur.fetchall()]
    print(f"  Products: {len(ids)} sản phẩm")
    return ids

def seedOrders(conn: psycopg.Connection, customerIds: list[int],
               shipperIds: list[int], count: int = 300) -> list[int]:
    """
    Tạo đơn hàng. EmployeeID chỉ lấy trong số nhân viên phòng
    "Quản Lý Sản Phẩm" (trừ Giám Đốc Sản Phẩm).
    """
    productOrderEmployeeIds = getProductOrderEmployees(conn)
 
    cur = conn.cursor()
    rows = []
    for _ in range(count):
        customerId = random.choice(customerIds)
        employeeId = random.choice(productOrderEmployeeIds)
        shipperId = random.choice(shipperIds)
        ngayDat = randomDate(date(2022, 1, 1), date(2025, 12, 31))
        gio = f"{random.randint(8, 19):02d}:{random.randint(0, 59):02d}:00"
        rows.append((customerId, employeeId, f"{ngayDat} {gio}", shipperId))
 
    cur.executemany("""
        INSERT INTO "Orders"
        ("CustomerID", "EmployeeID", "NgayDatHang", "ShipperID")
        VALUES (%s, %s, %s, %s)
    """, rows)
    conn.commit()
 
    cur.execute('SELECT "OrderID" FROM "Orders" ORDER BY "OrderID"')
    ids = [r[0] for r in cur.fetchall()]
    print(f"  Orders: {len(ids)} đơn hàng "
          f"(EmployeeID lấy từ {len(productOrderEmployeeIds)} nhân viên Quản Lý Sản Phẩm)")
    return ids

def seedOrderDetails(conn: psycopg.Connection, orderIds: list[int],
                      productIds: list[int]) -> None:
    """Tạo chi tiết đơn hàng: 1–5 dòng sản phẩm cho mỗi đơn."""
    cur = conn.cursor()
    rows = []
    for orderId in orderIds:
        soDong = random.randint(1, 5)
        chosenProducts = random.sample(
            productIds, k=min(soDong, len(productIds))
        )
        for productId in chosenProducts:
            quantity = random.randint(1, 50)
            rows.append((orderId, productId, quantity))
 
    cur.executemany("""
        INSERT INTO "OrderDetails" ("OrderID", "ProductID", "Quantity")
        VALUES (%s, %s, %s)
    """, rows)
    conn.commit()
    print(f"  OrderDetails: {len(rows)} dòng chi tiết đơn hàng")
 
# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Điểm khởi đầu — chạy toàn bộ pipeline seed."""
    random.seed(42)

    print(f"\nKết nối tới: Datapilot")
    conn = psycopg.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="12345678",
        port=5432
    )

    print("\n[1/7] Xóa dữ liệu cũ...")
    resetDatabase(conn)

    cur = conn.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname='public'")
    print(f"  Số bảng hiện có: {cur.fetchone()[0]}")

    print("\n[2/7] Tạo schema...")
    conn.execute(SCHEMA_SQL)
    conn.commit()

    print("\n[3/8] Seed Departments...")
    deptNameToId = seedDepartments(conn)

    print("\n[4/8] Seed Employees + EmployeeProfiles...")
    allIds = seedEmployees(conn, deptNameToId)

    print("\n[5/8] Seed BaseSalary (lương cứng + phụ cấp)...")
    baseSalaryMap = seedBaseSalary(conn, allIds)

    print("\n[6/8] Seed Attendance (Jan–Jun 2025)...")
    seedAttendance(conn, allIds)

    print("\n[7/8] Seed SalaryHistory (18 tháng, tính từ Attendance)...")
    seedSalaryHistory(conn, allIds, baseSalaryMap)

    print("\n[8/8] Seed LeaveRequests + ChatHistory...")
    seedLeaveRequests(conn, allIds)
    seedChatHistory(conn)

    updateHeadCounts(conn)

    categoryNameToId = seedCategories(conn)
    supplierIds = seedSuppliers(conn)
    shipperIds = seedShippers(conn)
    customerIds = seedCustomers(conn)
    productIds = seedProducts(conn, categoryNameToId, supplierIds)
    orderIds = seedOrders(conn, customerIds, shipperIds)
    seedOrderDetails(conn, orderIds, productIds)

    conn.close()


    print("\nSeed hoàn tất. Kết quả:")
    conn2 = psycopg.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="12345678",
        port=5432
    )
    cur = conn2.execute(
        "SELECT tablename FROM pg_tables WHERE schemaname='public'"
    )
    for t in [r[0] for r in cur.fetchall()]:
        count = conn2.execute(f"SELECT COUNT(*) FROM \"{t}\"").fetchone()[0]
        print(f"  {t:<35} {count:>8,} hàng")
    conn2.close()


if __name__ == "__main__":
    main()
