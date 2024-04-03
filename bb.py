from selenium import webdriver
from selenium.webdriver.common.by import By

# WebDriver'ı başlatın (örneğin, Chrome)
driver = webdriver.Chrome()

# Web sayfasını yükleyin
driver.get("https://www.6pm.com/p/michael-kors-mk9102-lennox-chronograph-gunmetal/product/9902667/color/411")

# MSRP değerini çekmek için CSS sınıflarını kullanarak elementi bulun
msrp_element = driver.find_element(By.CLASS_NAME, "ao-z.bo-z")

# Elementin metnini alın
msrp_text = msrp_element.text

# Sonucu yazdırın
print("MSRP:", msrp_text)

# WebDriver'ı kapatın
driver.quit()
