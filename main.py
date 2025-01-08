from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

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
        print(f"Начинаю парсинг сайта: {url}")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        print("Инициализация браузера...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        all_products = []
        page = 1
        
        while True:
            current_url = f"{url}page/{page}/" if page > 1 else url
            print(f"\nОбработка страницы {page}: {current_url}")
            
            driver.get(current_url)
            time.sleep(5)
            
            # Прокручиваем страницу
            scroll_page(driver)
            
            # Ищем товары на текущей странице
            products_elements = driver.find_elements(By.CSS_SELECTOR, '.product, .type-product, article.product')
            
            if not products_elements:
                print(f"Товары не найдены на странице {page}. Завершаем парсинг.")
                break
                
            print(f"Найдено товаров на странице {page}: {len(products_elements)}")
            
            for product in products_elements:
                try:
                    name = product.find_element(By.CSS_SELECTOR, '.woocommerce-loop-product__title, h2.woocommerce-loop-product__title').text
                    price = product.find_element(By.CSS_SELECTOR, '.price, .woocommerce-Price-amount').text
                    link = product.find_element(By.CSS_SELECTOR, 'a.woocommerce-LoopProduct-link').get_attribute('href')
                    img = product.find_element(By.CSS_SELECTOR, 'img').get_attribute('src')
                    
                    if name:
                        product_data = {
                            'название': name,
                            'цена': price,
                            'ссылка': link,
                            'фото': img
                        }
                        all_products.append(product_data)
                        print(f"Обработан товар: {name}")
                    
                except Exception as e:
                    print(f"Ошибка при обработке товара: {str(e)}")
                    continue
            
            # Проверяем наличие следующей страницы
            try:
                next_page = driver.find_element(By.CSS_SELECTOR, '.pagination li.active').find_element(By.XPATH, 'following-sibling::li')
                if not next_page:
                    print("Достигнут конец пагинации")
                    break
            except:
                print("Пагинация не найдена или достигнут конец")
                break
                
            page += 1
        
        driver.quit()
        print(f"\nВсего собрано товаров: {len(all_products)}")
        
        # Добавляем скачивание изображений
        from image_downloader import ImageDownloader
        downloader = ImageDownloader()
        all_products = downloader.process_products(all_products)
        
        return all_products
        
    except Exception as e:
        print(f"Ошибка при парсинге: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return None

def save_to_csv(products, filename='products.csv'):
    try:
        df = pd.DataFrame(products)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Данные сохранены в файл: {filename}")
        print(f"Всего сохранено товаров: {len(products)}")
    except Exception as e:
        print(f"Ошибка при сохранении в CSV: {e}")

if __name__ == "__main__":
    url = 'https://www.aveopt.com.ua/all-products/'
    print("Начало работы программы")
    products = parse_website(url)
    if products:
        save_to_csv(products)
    print("Программа завершена")
