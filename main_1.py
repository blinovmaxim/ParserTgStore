# import pandas as pd
# import os
# import requests
# from urllib.parse import unquote
# import time
# from PIL import Image, ImageEnhance

# def enhance_image(image_path):
#     try:
#         # Открываем изображение
#         img = Image.open(image_path)
        
#         # Конвертируем в RGB если изображение в другом формате
#         if img.mode != 'RGB':
#             img = img.convert('RGB')
        
#         # Улучшаем качество изображения
#         # Увеличиваем резкость
#         enhancer = ImageEnhance.Sharpness(img)
#         img = enhancer.enhance(1.5)
        
#         # Увеличиваем контрастность
#         enhancer = ImageEnhance.Contrast(img)
#         img = enhancer.enhance(1.2)
        
#         # Немного увеличиваем яркость
#         enhancer = ImageEnhance.Brightness(img)
#         img = enhancer.enhance(1.1)
        
#         # Увеличиваем насыщенность цветов
#         enhancer = ImageEnhance.Color(img)
#         img = enhancer.enhance(1.2)
        
#         # Изменяем размер, если изображение слишком маленькое
#         if img.size[0] < 800 or img.size[1] < 800:
#             img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
#         # Сохраняем с высоким качеством
#         img.save(image_path, 'JPEG', quality=95)
#         print(f"Изображение улучшено: {image_path}")
#         return True
#     except Exception as e:
#         print(f"Ошибка при обработке изображения {image_path}: {str(e)}")
#         return False

# def download_image(url, folder, filename):
#     try:
#         url = url.strip()
        
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#             'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
#             'Referer': 'https://google.com'
#         }
        
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code == 200:
#             os.makedirs(folder, exist_ok=True)
#             file_path = os.path.join(folder, filename)
            
#             # Сохраняем оригинальное изображение
#             with open(file_path, 'wb') as f:
#                 f.write(response.content)
            
#             # Улучшаем качество изображения
#             if enhance_image(file_path):
#                 print(f"Скачано и улучшено: {filename}")
#                 return True
#             else:
#                 print(f"Изображение скачано, но не удалось улучшить: {filename}")
#                 return True
#         else:
#             print(f"Ошибка при скачивании {filename}: статус {response.status_code}")
#             return False
#     except Exception as e:
#         print(f"Ошибка при скачивании {filename}: {str(e)}")
#         return False

# def analyze_and_download_images():
#     try:
#         encodings = ['utf-8', 'cp1251', 'latin1']
#         separators = [',', ';', '\t']
        
#         for encoding in encodings:
#             for sep in separators:
#                 try:
#                     df = pd.read_csv('ExportWebskladCSV (1).csv', 
#                                    encoding=encoding, 
#                                    sep=sep)
                    
#                     print(f"\nУспешно прочитано с кодировкой {encoding} и разделителем '{sep}'")
#                     print("\nКолонки в файле:", df.columns.tolist())
                    
#                     if 'Изображения' in df.columns:
#                         for i, row in df.head(10).iterrows():
#                             # Разделяем строку с URL на отдельные ссылки
#                             urls = row['Изображения'].split(',')
                            
#                             # Скачиваем первое изображение для каждого товара
#                             if urls:
#                                 first_url = urls[0]  # Берём первое изображение
#                                 filename = f"product_{i+1}.jpg"
#                                 download_image(first_url, 'downloaded_images', filename)
#                                 time.sleep(1)  # пауза между скачиваниями
#                     else:
#                         print("\nКолонка с URL изображений не найдена. Доступные колонки:", df.columns.tolist())
                    
#                     return df
                    
#                 except Exception as e:
#                     continue
                    
#         print("Не удалось прочитать файл с известными кодировками и разделителями")
        
#     except FileNotFoundError:
#         print("Файл не найден. Убедитесь, что файл находится в правильной директории")
#         print("Текущая директория:", os.getcwd())

# if __name__ == "__main__":
#     analyze_and_download_images()