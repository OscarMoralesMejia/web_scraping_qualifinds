from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from fastapi import FastAPI,HTTPException
import json
import time

app = FastAPI()

class URLRequest(BaseModel):
    url: str
@app.get("/")
def read_root():
    return {"message": "Bienvenido a mi challenge API!, para ver los metodos que hay disponibles, escribe /docs al final de la url (http://127.0.0.1:8000/docs)"}
    
@app.post("/get_products")
def scraping_url(url: str):
    """_summary_
        Obtiene los primeros 15 productos de la url que recibe como parametro
    Args:
        Recibe una url
        Ejemplos:
            https://www.jumbocolombia.com/supermercado/despensa/enlatados-y-conservas-
            https://www.tiendasjumbo.co/supermercado/despensa/harinas-y-mezclas-para-preparar-
            https://www.tiendasjumbo.co/supermercado/despensa/bebida-achocolatada-en-polvo-
            https://www.tiendasjumbo.co/supermercado/despensa/aceite

    Returns:
        json: estructura json
    """
    try:
        options = Options()
        options.add_argument('--headless')  # Modo sin interfaz gráfica
        options.add_argument('--no-sandbox')  # Necesario en entornos Docker
        options.add_argument('--disable-dev-shm-usage')  # Usa /tmp en lugar de /dev/shm
        options.add_argument('--disable-gpu')  # Deshabilita la GPU (recomendado en headless)
        options.add_argument('--window-size=1920x1080')  # Simula una pantalla grande
        options.add_argument('--remote-debugging-port=9222')  # Habilita debugging

        # Configurar el driver con la versión correcta de Chrome en Docker
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        data={}
        driver.get(url)
        time.sleep(5)    
    
        productos = []
        elementos_encontrados = 0
        altura_anterior = 0
        while elementos_encontrados < 15:
            driver.execute_script("window.scrollBy(0, 250);")  # Desplazar 250 píxeles hacia abajo
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR,'div[class="tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem--gallery-css tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem--normal tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem--gallery-css--normal tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem--grid tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem--gallery-css--grid pa4"]')))

            elementos = driver.find_elements(By.CSS_SELECTOR,'div[class="tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem--gallery-css tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem--normal tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem--gallery-css--normal tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem--grid tiendasjumboqaio-cmedia-integration-cencosud-0-x-galleryItem--gallery-css--grid pa4"]')
            nuevos_elementos = elementos[elementos_encontrados:]
            for item in nuevos_elementos:
                try:
                    product = {}
                    product['name'] = item.find_element(By.CLASS_NAME, 'vtex-product-summary-2-x-productBrand.vtex-product-summary-2-x-brandName.t-body').text
                    product['price'] = item.find_element(By.CLASS_NAME, 'tiendasjumboqaio-jumbo-minicart-2-x-price').text
                    product['promo_price'] = item.find_element(By.CSS_SELECTOR, 'div[class="tiendasjumboqaio-jumbo-minicart-2-x-price tiendasjumboqaio-jumbo-minicart-2-x-price--product-prime"').text
                    productos.append(product)
                    elementos_encontrados += 1
                    if elementos_encontrados >= 15:
                        break
                except Exception as e:
                    productos.append(product)
                    elementos_encontrados += 1
                    continue
            
            altura_actual = driver.execute_script("return window.pageYOffset;")
            if altura_actual == altura_anterior:
                break
            altura_anterior = altura_actual  
        
        data = {
        "url": url,
        "products": productos
        }
        
        driver.quit()
    except Exception as e:
        print(e)
    
    return JSONResponse(content=data)