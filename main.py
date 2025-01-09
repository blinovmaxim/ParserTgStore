from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from image_downloader import ImageDownloader


def scroll_page(driver, wait_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Прокручиваем вниз
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Ждем загрузки контента
        time.sleep(wait_time)
        
        # Вычисляем новую высоту прокрутки
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # Если высота не изменилась, значит достигли конца страницы
        if new_height == last_height:
            break
            
        last_height = new_height
        print("Прокручиваю страницу...")

def parse_website(url):
    try:
        # Инициализация браузера
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        all_products = []
        page = 73  # Можно сделать параметром
        max_pages = 74  # Можно сделать параметром
        
        for page in range(page, max_pages + 1):
            current_url = f"{url}?product-page={page}"
            print(f"\nОбработка страницы {page}: {current_url}")
            
            driver.delete_all_cookies()
            driver.get(current_url)
            
            # Ждем загрузки товаров
            WebDriverWait(driver, 40).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.product')))
            
            products_container = driver.find_element(By.CSS_SELECTOR, '.products')
            products_elements = products_container.find_elements(By.CSS_SELECTOR, '.product')
            
            if len(products_elements) > 40 and page != max_pages:
                products_elements = products_elements[:40]
            
            for i, product in enumerate(products_elements):
                try:
                    name = product.find_element(By.CSS_SELECTOR, '.woocommerce-loop-product__title').text
                    
                    if name == "Нет в наличии":
                        print("Найден флаг конца каталога.")
                        driver.quit()
                        return process_images(all_products)
                    
                    if "В наявності" in product.text:
                        product_data = {
                            'название': name,
                            'цена': product.find_element(By.CSS_SELECTOR, '.price').text,
                            'ссылка': product.find_element(By.CSS_SELECTOR, 'a.woocommerce-LoopProduct-link').get_attribute('href'),
                            'фото': product.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                        }
                        all_products.append(product_data)
                        print(f"Обработан товар: {name}")
                    
                except Exception as e:
                    print(f"Ошибка при обработке товара: {str(e)}")
                    continue
        
        driver.quit()
        return process_images(all_products)
        
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None

def process_images(products):
    """Вынесли обработку изображений в отдельную функцию"""
    if not products:
        return None
    downloader = ImageDownloader()
    return downloader.process_products(products)

def save_to_csv(products, filename='products.csv'):
    if not products:
        print("Нет данных для сохранения")
        return
        
    try:
        df = pd.DataFrame(products)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Сохранено {len(products)} товаров в {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении в CSV: {e}")


if __name__ == "__main__":
    url = 'https://www.aveopt.com.ua/all-products/'
    products = parse_website(url)
    if products:
        save_to_csv(products)