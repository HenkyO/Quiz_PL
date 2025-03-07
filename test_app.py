import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Konfigurasi Logging
LOG_DIR = "test-results"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "test_log.txt"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Konfigurasi Chrome WebDriver untuk CI/CD (misalnya GitHub Actions)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=chrome_options)

# Base URL aplikasi yang diuji
BASE_URL = "http://127.0.0.1:8000/"

# List untuk menyimpan hasil test
test_results = []

def log_result(test_name, status, message=""):
    result = f"{test_name}: {status} - {message}"
    print(result)
    logging.info(result)

def run_test(test_function):
    """
    Menjalankan setiap test case agar error tidak menghentikan eksekusi test lainnya.
    """
    try:
        test_function()
        test_results.append((test_function.__name__, "✅ PASSED", ""))
    except AssertionError as e:
        test_results.append((test_function.__name__, "❌ FAILED", str(e)))
    except Exception as e:
        test_results.append((test_function.__name__, "⚠️ ERROR", str(e)))

# =======================
# Test Case Registrasi
# =======================

# TC_REG_01: Registrasi dengan Data Valid (user1)
def test_reg_valid():
    driver.get(BASE_URL + "register.php")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("user1")
    driver.find_element(By.ID, "name").send_keys("user1")
    driver.find_element(By.ID, "InputEmail").send_keys("user1@gmail.com")
    driver.find_element(By.ID, "InputPassword").send_keys("user1")
    driver.find_element(By.ID, "InputRePassword").send_keys("user1")
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)
    # Expected: Pendaftaran berhasil, misalnya muncul pesan sukses
    assert "Pendaftaran berhasil" in driver.page_source, "Error: Pendaftaran tidak berhasil."

# TC_REG_02: Registrasi dengan Field Kosong
def test_reg_empty():
    driver.get(BASE_URL + "register.php")
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)
    # Expected: Muncul pesan error bahwa field tidak boleh kosong
    assert "Data tidak boleh kosong" in driver.page_source, "Error: Tidak muncul pesan error untuk field kosong."

# TC_REG_03: Registrasi dengan Format Email Salah (user2)
def test_reg_invalid_email():
    driver.get(BASE_URL + "register.php")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("user2")
    driver.find_element(By.ID, "name").send_keys("user2")
    driver.find_element(By.ID, "InputEmail").send_keys("user2")  # Format email salah
    driver.find_element(By.ID, "InputPassword").send_keys("user2")
    driver.find_element(By.ID, "InputRePassword").send_keys("user2")
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)
    # Expected: Muncul pesan error "Format email salah" atau pesan sejenis, misalnya "sertakan @ pada email"
    assert "sertakan @" in driver.page_source, "Error: Validasi format email gagal."

# TC_REG_04: Registrasi dengan Password Tidak Cocok (user3)
def test_reg_password_mismatch():
    driver.get(BASE_URL + "register.php")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("user3")
    driver.find_element(By.ID, "name").send_keys("user3")
    driver.find_element(By.ID, "InputEmail").send_keys("user3@gmail.com")
    driver.find_element(By.ID, "InputPassword").send_keys("user3")
    driver.find_element(By.ID, "InputRePassword").send_keys("user")  # Tidak sama dengan password
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)
    # Expected: Muncul pesan error "Password dan konfirmasi tidak cocok" / "Password tidak sama"
    assert "Password tidak sama" in driver.page_source, "Error: Validasi password tidak cocok gagal."

# TC_REG_05: Registrasi dengan Data Duplikat (user1 sudah ada)
def test_reg_duplicate():
    driver.get(BASE_URL + "register.php")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("user1")
    driver.find_element(By.ID, "name").send_keys("user1")
    driver.find_element(By.ID, "InputEmail").send_keys("user1@gmail.com")
    driver.find_element(By.ID, "InputPassword").send_keys("user1")
    driver.find_element(By.ID, "InputRePassword").send_keys("user1")
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)
    # Expected: Muncul pesan error "Username/email sudah ada"
    assert "Username sudah terdaftar" in driver.page_source, "Error: Duplikasi data tidak terdeteksi."

# TC_REG_06: Keamanan Registrasi – SQL Injection
def test_reg_sql_injection():
    driver.get(BASE_URL + "register.php")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("' OR '1'='1")
    driver.find_element(By.ID, "name").send_keys("' OR '1'='1")
    driver.find_element(By.ID, "InputEmail").send_keys("hacker@example.com")
    driver.find_element(By.ID, "InputPassword").send_keys("' OR '1'='1")
    driver.find_element(By.ID, "InputRePassword").send_keys("' OR '1'='1")
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)
    # Expected: Sistem mencegah SQL Injection; pendaftaran gagal (tidak muncul pesan sukses)
    assert "Pendaftaran berhasil" not in driver.page_source, "Error: SQL Injection berhasil pada registrasi."

# =======================
# Test Case Login
# =======================

# TC_LOGIN_01: Login dengan Data Valid (user1)
def test_login_valid():
    driver.get(BASE_URL + "login.php")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("user1")
    driver.find_element(By.ID, "InputPassword").send_keys("user1")
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)
    # Expected: Pengguna berhasil login, misalnya muncul pesan "Selamat datang" atau dashboard
    assert "Selamat datang" in driver.page_source, "Error: Login valid tidak berhasil."

# TC_LOGIN_02: Login dengan Password Salah
def test_login_wrong_password():
    driver.get(BASE_URL + "login.php")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("user1")
    driver.find_element(By.ID, "InputPassword").send_keys("user")  # Password salah
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)
    # Expected: Muncul pesan error "Login gagal" atau "Password salah"
    assert ("Login gagal" in driver.page_source or "Password salah" in driver.page_source), "Error: Tidak muncul pesan error untuk password salah."

# TC_LOGIN_03: Login dengan Field Kosong
def test_login_empty():
    driver.get(BASE_URL + "login.php")
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)
    # Expected: Muncul pesan error "Username dan password harus diisi" atau "Data tidak boleh kosong"
    assert "Data tidak boleh kosong" in driver.page_source, "Error: Pesan error untuk field kosong tidak muncul."

# TC_LOGIN_04: Login dengan Username Tidak Terdaftar
def test_login_username_not_found():
    driver.get(BASE_URL + "login.php")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("user")
    driver.find_element(By.ID, "InputPassword").send_keys("user")
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)
    # Expected: Muncul pesan error "User tidak ditemukan" atau "Register User Gagal"
    assert ("User tidak ditemukan" in driver.page_source or "Register User Gagal" in driver.page_source), "Error: Pesan error user tidak ditemukan tidak muncul."

# TC_LOGIN_05: Keamanan Login – SQL Injection
def test_login_sql_injection():
    driver.get(BASE_URL + "login.php")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("' OR '1'='1")
    driver.find_element(By.ID, "InputPassword").send_keys("' OR '1'='1")
    driver.find_element(By.NAME, "submit").click()
    time.sleep(2)
    # Expected: Sistem mencegah SQL Injection; login gagal dan tidak muncul pesan "Selamat datang"
    assert "Selamat datang" not in driver.page_source, "Error: SQL Injection berhasil pada login."

# Daftar semua test case
test_cases = [
    # Registrasi
    test_reg_valid,
    test_reg_empty,
    test_reg_invalid_email,
    test_reg_password_mismatch,
    test_reg_duplicate,
    test_reg_sql_injection,
    # Login
    test_login_valid,
    test_login_wrong_password,
    test_login_empty,
    test_login_username_not_found,
    test_login_sql_injection
]

# Eksekusi semua test case
for test in test_cases:
    run_test(test)

# Tampilkan hasil pengujian
print("\n=== TEST RESULTS ===")
print(f"{'Test Case':<30} {'Status':<10} {'Message'}")
print("=" * 80)
for name, status, message in test_results:
    print(f"{name:<30} {status:<10} {message}")

# Tutup browser setelah pengujian selesai
driver.quit()
