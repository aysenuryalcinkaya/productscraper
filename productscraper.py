import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options  # Headless modu etkinleştirmek için Options ekleyin
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

# Headless tarayıcı seçeneklerini ayarlayın
chrome_options = Options()
chrome_options.add_argument('--headless') 
# URL listesi
urls = [
    {"name": "watches", "url": "https://www.6pm.com/watches/CLHXAeICAQE.zso?s=isNew%2Fdesc%2FgoLiveDate%2Fdesc%2FrecentSalesStyle%2Fdesc%2F"},
    {"name": "handbags", "url": "https://www.6pm.com/handbags/COjWARCS1wHiAgIBAg.zso?s=isNew%2Fdesc%2FgoLiveDate%2Fdesc%2FrecentSalesStyle%2Fdesc%2F"}
]

# Tarayıcıyı başlat
driver = webdriver.Chrome()

for url_info in urls:
    url_name = url_info["name"]
    base_url = url_info["url"]

    # CSV dosyasını oluştur
    with open(f"{url_name}.csv", "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Brand Name", "Product Name", "Colors", "Sizes", "Product Description", "UPC", "Custom Field", "Product Images","SalePrice","ActualPrice"])

        if url_name == "handbags":
            driver.get(base_url)

                # "b1-z" sınıfına sahip a etiketlerini bul
            elements = driver.find_elements(By.CSS_SELECTOR, "a.b1-z")
            hrefs = [element.get_attribute("href") for element in elements]
            # 25 sayfaya kadar sayfa dolaş
            for page_number in range(1, 26):
                url = f"{base_url}&p={page_number}"
                driver.get(url)

                # "b1-z" sınıfına sahip a etiketlerini bul
                elements = driver.find_elements(By.CSS_SELECTOR, "a.b1-z")
                page_hrefs = [element.get_attribute("href") for element in elements]
                hrefs.extend(page_hrefs)

                for href in hrefs:
                    driver.get(href)
                    brand_name = driver.find_element(By.CSS_SELECTOR, "#productRecap > div.Ya-z > div.ya-z > div > div.Ba-z > h1 > div > span.hm-z > a > span").text
                    product_name = driver.find_element(By.CSS_SELECTOR, "#productRecap > div.Ya-z > div.ya-z > div > div.Ba-z > h1 > div > span.im-z").text
                    price_element = driver.find_element(By.CSS_SELECTOR, "#productRecap > div.Ya-z > div.ya-z > div > div.Ba-z > div.Xn-z > div > span > span:nth-child(1)")
                    price_text = price_element.text
                    sale_price = price_text.replace('\n', '').replace('$', '')
                    try:
                        
                        actualprice_element = driver.find_element(By.CLASS_NAME, "ao-z.bo-z")
                        actualprice_text = actualprice_element.text
                        actual_price = price_text.replace('\n', '').replace('$', '')
                    except NoSuchElementException:
                        actual_price = " "
                    div_element = driver.find_element(By.CSS_SELECTOR, "div.mZ-z")
                    span_elements = div_element.find_element(By.CSS_SELECTOR,"span.oZ-z")
                    color =span_elements.text
                    description_element = driver.find_element(By.XPATH, '//div[@itemprop="description"]')
                    description = description_element.text

                    # Sayfada measurements verisini al
                    try:
                        one_size_element = driver.find_element(By.XPATH, '//div[@id="sizingChooser"]//span[@class="OY-z"]')
                        size = one_size_element.text
                        size=size.replace(':', '')
                    except NoSuchElementException:
                        size = " "
                    sku_element = driver.find_element(By.XPATH, '//span[@itemprop="sku"]')
                    custom_field ="6pm SKU:#"+ sku_element.text
                    upc = None
                    try:
                        upc_script = driver.find_element(By.XPATH, '//script[contains(text(),"upc")]').get_attribute("innerHTML")
                        upc_start = upc_script.find('"upc":"') + len('"upc":"')
                        upc_end = upc_script.find('"', upc_start)
                        upc = upc_script[upc_start:upc_end]
                    except NoSuchElementException:
                        upc = "UPC not found"


                    # Sayfanın sonuna kadar yavaşça kaydırarak tüm resimleri yükle
                    scroll_speed = 1  # Scroll hızını burada ayarlayabilirsiniz (daha yavaş bir kaydırma için 1'e yakın bir değer kullanın)
                    scroll_pause_time = 1  # Scroll işlemi arasında beklemek istediğiniz süreyi ayarlayabilirsiniz
                    max_scrolls = 3  # Maksimum kaydırma sayısı

                    scroll_count = 0  # Kaydırma sayacı
                    while scroll_count < max_scrolls:
                        # Sayfanın sonuna kaydır
                        actions = ActionChains(driver)
                        actions.send_keys(Keys.PAGE_DOWN)
                        actions.perform()
                        time.sleep(scroll_pause_time)
                        
                        # Sayfanın sonuna ulaşıp ulaşmadığını kontrol edin
                        if "All images loaded" in driver.page_source:
                            break
                        
                        scroll_count += 1

                    # 1 saniye bekle
                    time.sleep(1)

                    image_urls = driver.execute_script("""
                        var imageElements = document.querySelectorAll('div.nW-z button[data-media="image"] img[itemprop="image"]');
                        var urls = [];
                        for (var i = 0; i < imageElements.length; i++) {
                            urls.push(imageElements[i].getAttribute("src"));
                        }
                        return urls;
                    """)

                    # Image URL'lerini sıralı bir şekilde ayrı sütunlarda sakla
                    image1 = image2 = image3 = image4 = ""
                    for i, img_url in enumerate(image_urls, start=1):
                        if i == 1:
                            image1 = img_url
                        elif i == 2:
                            image2 = img_url
                        elif i == 3:
                            image3 = img_url
                        elif i == 4:
                            image4 = img_url

                    # CSV dosyasına verileri yaz
                    csv_writer.writerow([brand_name, product_name, color, size, description, upc, custom_field, image1, image2, image3,
                         image4, sale_price, actual_price])

        elif url_name == "watches":
            # Sadece tek sayfa işlem yap
            driver.get(base_url)
            elements = driver.find_elements(By.CSS_SELECTOR, "a.b1-z")
            hrefs = [element.get_attribute("href") for element in elements]
            
            for href in hrefs:
                driver.get(href)
                brand_name = driver.find_element(By.CSS_SELECTOR, "#productRecap > div.Ya-z > div.ya-z > div > div.Ba-z > h1 > div > span.hm-z > a > span").text
                product_name = driver.find_element(By.CSS_SELECTOR, "#productRecap > div.Ya-z > div.ya-z > div > div.Ba-z > h1 > div > span.im-z").text
                price_element = driver.find_element(By.CSS_SELECTOR, "#productRecap > div.Ya-z > div.ya-z > div > div.Ba-z > div.Xn-z > div > span > span:nth-child(1)")
                price_text = price_element.text
                sale_price = price_text.replace('\n', '').replace('$', '')
                try:
                    actualprice_element = driver.find_element(By.CLASS_NAME, "ao-z.bo-z")
                    actualprice_text = actualprice_element.text
                    actual_price = actualprice_text.replace('\n', '').replace('$', '')
                except NoSuchElementException:
                    actual_price = " "
                
                div_element = driver.find_element(By.CSS_SELECTOR, "div.mZ-z")
                span_elements = div_element.find_element(By.CSS_SELECTOR,"span.oZ-z")
                color =span_elements.text 
                description_element = driver.find_element(By.XPATH, '//div[@itemprop="description"]')
                description = description_element.text

                # Sayfada measurements verisini al
                try:
                    one_size_element = driver.find_element(By.XPATH, '//div[@id="sizingChooser"]//span[@class="OY-z"]')
                    size = one_size_element.text
                    size=size.replace(':', '')
                except NoSuchElementException:
                    size = " "
                sku_element = driver.find_element(By.XPATH, '//span[@itemprop="sku"]')
                custom_field ="6pm SKU:#"+ sku_element.text
                upc = None
                try:
                    upc_script = driver.find_element(By.XPATH, '//script[contains(text(),"upc")]').get_attribute("innerHTML")
                    upc_start = upc_script.find('"upc":"') + len('"upc":"')
                    upc_end = upc_script.find('"', upc_start)
                    upc = upc_script[upc_start:upc_end]
                except NoSuchElementException:
                    upc = "UPC not found"

                # Sayfanın sonuna kadar yavaşça kaydırarak tüm resimleri yükle
                scroll_speed = 1  # Scroll hızını burada ayarlayabilirsiniz (daha yavaş bir kaydırma için 1'e yakın bir değer kullanın)
                scroll_pause_time = 1  # Scroll işlemi arasında beklemek istediğiniz süreyi ayarlayabilirsiniz
                max_scrolls = 3  # Maksimum kaydırma sayısı

                scroll_count = 0  # Kaydırma sayacı
                while scroll_count < max_scrolls:
                        # Sayfanın sonuna kaydır
                        actions = ActionChains(driver)
                        actions.send_keys(Keys.PAGE_DOWN)
                        actions.perform()
                        time.sleep(scroll_pause_time)
                        
                        # Sayfanın sonuna ulaşıp ulaşmadığını kontrol edin
                        if "All images loaded" in driver.page_source:
                            break
                        
                        scroll_count += 1

                    # 1 saniye bekle
                time.sleep(1)

                image_urls = driver.execute_script("""
                        var imageElements = document.querySelectorAll('div.nW-z button[data-media="image"] img[itemprop="image"]');
                        var urls = [];
                        for (var i = 0; i < imageElements.length; i++) {
                            urls.push(imageElements[i].getAttribute("src"));
                        }
                        return urls;
                    """)
                
                    # Image URL'lerini sıralı bir şekilde ayrı sütunlarda sakla
                image1 = image2 = image3 = image4 = ""
                for i, img_url in enumerate(image_urls, start=1):
                        if i == 1:
                            image1 = img_url
                        elif i == 2:
                            image2 = img_url
                        elif i == 3:
                            image3 = img_url
                        elif i == 4:
                            image4 = img_url    
                    
                

                # CSV dosyasına verileri yaz
                csv_writer.writerow([brand_name, product_name, color, size, description, upc, custom_field, image1, image2, image3,
                         image4, sale_price, actual_price])

# Tarayıcıyı kapat
driver.quit()
