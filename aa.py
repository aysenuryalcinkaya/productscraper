from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

# WebDriver'ı başlat
driver = webdriver.Chrome()  # veya başka bir tarayıcı kullanabilirsiniz

# Hedef URL
url = "https://www.6pm.com/p/michael-kors-mk9102-lennox-chronograph-gunmetal/product/9902667/color/411"

# Sayfayı aç
driver.get(url)

# Sayfanın sonuna kadar yavaşça kaydırarak tüm resimleri yükle
scroll_speed = 1  # Scroll hızını burada ayarlayabilirsiniz (daha yavaş bir kaydırma için 1'e yakın bir değer kullanın)
scroll_pause_time = 1  # Scroll işlemi arasında beklemek istediğiniz süreyi ayarlayabilirsiniz
max_scrolls = 6  # Maksimum kaydırma sayısı

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

# JavaScript ile tüm resim URL'lerini toplamak için bir işlevi çalıştır
image_urls = driver.execute_script("""
    var imageElements = document.querySelectorAll('div.nW-z button[data-media="image"] img[itemprop="image"]');
    var urls = [];
    for (var i = 0; i < imageElements.length; i++) {
        urls.push(imageElements[i].getAttribute("src"));
    }
    return urls;
""")

# Image URL'lerini yazdır
for i, img_url in enumerate(image_urls, start=1):
    print(f"Image {i} URL: {img_url}")

# Tarayıcıyı kapat
driver.quit()
