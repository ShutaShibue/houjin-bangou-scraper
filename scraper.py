from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import pandas as pd
import time


class HoujinBangouScraper:
    """法人番号公表サイトのスクレイパークラス"""
    
    def __init__(self, headless=True):
        """
        ChromeDriverの初期化とヘッドレスモードの設定
        
        Args:
            headless (bool): ヘッドレスモードを有効にするかどうか
        """
        self.options = Options()
        if headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        # パフォーマンス最適化のオプションを追加
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--disable-images')
        self.options.add_argument('--blink-settings=imagesEnabled=false')
        self.options.page_load_strategy = 'eager'

        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 5)

    def search_company(self, company_name=None, prefecture=None, city=None, details=None):
        try:
            # メインページにアクセス
            self.driver.get('https://www.houjin-bangou.nta.go.jp/index.html')
            
            # 会社名が指定されている場合
            if company_name:
                name_input = self.wait.until(
                    EC.presence_of_element_located((By.NAME, 'houzinNmTxtf'))
                )
                name_input.send_keys(company_name)
            
            # 都道府県と市区町村が指定されている場合のみ詳細住所を入力可能
            if prefecture and city:
                # 都道府県の選択
                prefecture_select = Select(self.driver.find_element(
                    By.ID, 'addr_pref'
                ))
                prefecture_select.select_by_visible_text(prefecture)
                
                # 市区町村の選択
                # 市区町村のドロップダウンが更新されるのを明示的に待機
                city_select = self.wait.until(
                    EC.presence_of_element_located((By.ID, 'addr_city'))
                )
                # さらにオプションが読み込まれるのを待機
                self.wait.until(
                    lambda driver: len(Select(city_select).options) > 1
                )
                # 市区町村を選択
                Select(city_select).select_by_visible_text(city)
                
                # 詳細住所が指定されている場合
                if details:
                    details_button = self.driver.find_element(
                        By.CSS_SELECTOR, 'a.rs_preserve'
                    )
                    details_button.click()
                    
                    time.sleep(0.3)
                    
                    details_input = self.driver.find_element(
                        By.ID, 'addr_town'
                    )
                    details_input.send_keys(details)
            
            try:
                # JavaScriptによる直接実行を最初から試みる
                search_button = self.driver.find_element(
                    By.CSS_SELECTOR, 'button.submitBtn01#search_condition'
                )
                self.driver.execute_script("arguments[0].click();", search_button)
            except:
                # 失敗した場合のみフォームのsubmitを試行
                self.driver.execute_script("document.querySelector('form').submit();")
            
            # 検索結果テーブルの待機と取得
            table = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, 'fixed'))
            )
            
            # テーブルデータの取得
            headers = ['法人番号', '商号又は名称', '所在地', '変更履歴情報等']
            
            rows = []
            row_elements = table.find_elements(By.TAG_NAME, 'tr')[1:]
            for row in row_elements:
                cols = row.find_elements(By.TAG_NAME, 'td')
                houjin_num = row.find_element(By.TAG_NAME, 'th').text.strip()
                meishou = cols[0].text.strip()
                address = cols[1].text.strip()
                history = cols[2].find_element(By.CLASS_NAME, 'infolink').text.strip()
                row_data = [houjin_num, meishou, address, history]
                rows.append(row_data)
            
            df = pd.DataFrame(rows, columns=headers)
            return df
            
        except Exception as e:
            print(f'エラーが発生しました: {str(e)}')
            return None
        
        finally:
            self.close()
    
    def close(self):
        """ブラウザを終了する"""
        if self.driver:
            self.driver.quit()


def main():
    """メイン実行関数"""
    scraper = HoujinBangouScraper(headless=True) # ブラウザを表示しない
    
    # 例
    results = scraper.search_company(
        #company_name="XYZ"
        prefecture='東京都',
        city='千代田区',
        details='丸の内１丁目１－１パレスビル５階'
    )
    
    if results is not None:
        results.to_csv('search_results.csv', index=False, encoding='utf-8-sig')


if __name__ == '__main__':
    main() 