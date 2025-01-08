import requests
import os
from urllib.parse import urlparse
from pathlib import Path
from PIL import Image, ImageEnhance

class ImageDownloader:
    def __init__(self, save_folder='product_images'):
        self.save_folder = save_folder
        Path(save_folder).mkdir(parents=True, exist_ok=True)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.aveopt.com.ua/'
        }

    def enhance_image(self, image_path):
        """Улучшает качество изображения"""
        try:
            with Image.open(image_path) as img:
                # Конвертируем в RGB если нужно
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Увеличиваем резкость
                sharpener = ImageEnhance.Sharpness(img)
                img = sharpener.enhance(1.5)

                # Увеличиваем контрастность
                contraster = ImageEnhance.Contrast(img)
                img = contraster.enhance(1.2)

                # Немного увеличиваем яркость
                brightener = ImageEnhance.Brightness(img)
                img = brightener.enhance(1.1)

                # Увеличиваем насыщенность
                colorer = ImageEnhance.Color(img)
                img = colorer.enhance(1.2)

                # Изменяем размер если изображение слишком маленькое
                if img.size[0] < 800 or img.size[1] < 800:
                    ratio = max(800/img.size[0], 800/img.size[1])
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Сохраняем с высоким качеством
                img.save(image_path, 'JPEG', quality=95, optimize=True)
                print(f"Изображение улучшено: {os.path.basename(image_path)}")

        except Exception as e:
            print(f"Ошибка при обработке изображения {image_path}: {str(e)}")

    def download_product_image(self, product_data):
        try:
            img_url = product_data['фото']
            if not img_url:
                return product_data

            safe_name = "".join(x for x in product_data['название'] if x.isalnum() or x in (' ', '-', '_'))
            safe_name = safe_name[:50].strip()
            
            # Всегда сохраняем в JPEG для консистентности
            filename = f"{safe_name}.jpg"
            filepath = os.path.join(self.save_folder, filename)

            response = requests.get(img_url, headers=self.headers, stream=True)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            # Улучшаем качество изображения
            self.enhance_image(filepath)

            product_data['фото'] = filepath
            print(f"Скачано и обработано изображение: {filename}")

        except Exception as e:
            print(f"Ошибка при скачивании изображения для {product_data['название']}: {str(e)}")
            product_data['фото'] = None
        
        return product_data

    def process_products(self, products):
        print("\nНачинаю скачивание и обработку изображений...")
        processed_products = []
        total = len(products)
        
        for i, product in enumerate(products, 1):
            print(f"Обработка {i}/{total}: {product['название']}")
            processed_products.append(self.download_product_image(product))
            
        print("Обработка изображений завершена")
        return processed_products 