import asyncio
import time,json,os
from playwright.async_api import async_playwright,Playwright,Browser,Page
from asyncio import Task
from bs4 import BeautifulSoup
import folder_path

class Handler:
    def __init__(self) -> None:
        self.interval = 0.1
        self.driver : Playwright.chromium = None
        self.browser : Browser = None
        self.base_url = "https://fptshop.com.vn"
        self.exception_log = []
    async def init(self):
        self.playwright_content_manager= async_playwright()
        self.playwright = await self.playwright_content_manager.start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        
    async def process(self):
        jobs = {
            'lap' : {
                'download_directory' : folder_path.fpt.lap,
                'family_url' : 'https://fptshop.com.vn/may-tinh-xach-tay'
            }
        }
        for job_key in jobs:
            job = jobs[job_key]
            self.exception_log = []
            
            raw_links_list = await self._get_urls(job['family_url'])
            links = []
            for raw_links in raw_links_list:
                link_list = self._urls_parser(raw_links)
                links.extend(link_list)
            with open(folder_path.join(job['download_directory'],'links.json'),'w') as file:
                file.write(json.dumps(links))
            
            for link in links:
                await self.save_spec(link,job['download_directory'])
            if (self.exception_log != []):
                with open(folder_path.join(job['download_directory'],'exception.json'),'w') as file:
                    file.write(json.dumps(self.exception_log))
           
    async def close(self):
        await self.browser.close()
        await self.playwright_content_manager.__aexit__()
    async def _get_urls(self,family_url):
        page = await self.browser.new_page()
        await page.goto(family_url,timeout=600000)
        while (True):
            load_more = await page.query_selector('.cdt-product--loadmore')
            try:
                await load_more.click()
            except:
                product_list = await page.query_selector('.cdt-product-wrapper')
                result = await product_list.inner_html()
                await page.close()
                break
        return [result]

    def _urls_parser(self,content : str):
        soup = BeautifulSoup(content,'html.parser')
        elements = soup.find_all(recursive=False)
        result = []
        for element in elements:
            inner_elements = element.find_all(recursive=False)
            for inner_element in inner_elements:
                try:
                    result.append(inner_element.find('a')['href'])
                    break
                except:
                    pass
                break
        return result
    async def _get_info(self,url : str):        
        url = self.base_url + url
        page = await self.browser.new_page()
        await page.goto(url,timeout=60000)
        warrant_xpaths = [
            '//html/body/div[2]/main/div/div[1]/div[2]/div[2]/div[1]/div[5]/div[2]/p'
        ]
        for warrant_xpath in warrant_xpaths:
            warrent_element = await page.query_selector(warrant_xpath)
            if (warrent_element != None):
                break

        price_xpaths = [
            '//html/body/div[2]/main/div/div[1]/div[2]/div[2]/div[2]/div[1]/div/div[1]',
            '//html/body/div[2]/main/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/div[1]'
        ]
        for price_xpath in price_xpaths:
            price_element = await page.query_selector(price_xpath)
            if (price_element != None):
                break
        detail_info_button = await page.query_selector('.js--open-modal')
        try:
            await detail_info_button.click()
        except:
            pass
        detail_info_xpaths = [
            '//html/body/div[2]/main/div/div[2]/div/div[1]/div[2]/div[2]/div/div/div/div/div[3]'
        ]
        for detail_info_xpath in detail_info_xpaths:
            detail_info_table = await page.query_selector(detail_info_xpath)
            if (detail_info_table != None):
                break
        info_xpaths = [
            "//html/body/div[2]/main/div/div[2]/div/div[1]/div[2]/div[1]/div/table/tbody",
            "//html/body/div[2]/main/div/div[2]/div/div[1]/div[2]/div/div/table/tbody",
        ]
        info_xpaths2 = [
            '//html/body/div[2]/main/div/div[1]/div[2]/div[2]/div[1]/div[4]/ul'
        ]
        for info_xpath in info_xpaths:
            info_table = await page.query_selector(info_xpath)
            if (info_table != None):
                break
        for info_xpath2 in info_xpaths2:
            info_table2 = await page.query_selector(info_xpath2)
            if (info_table2 != None):
                break
        if (info_table2 == None):
            print('AAAAAAAAAAAAAAAAAAAAAAAAAA')
        if ((info_table == None and info_table2 == None) or price_element == None):
            # if (info_table == None and detail_info_table == None):
            #     print('All Info null')
            # if (info_table == None):
            #     print('Info null')
            # elif(price_element == None):
            #     print('Price null')
            # elif(warrent_element == None):
            #     print('Warrant null')
            print(url)
            if (info_table == None and detail_info_table == None):
                print('All Info null')
            if (info_table == None):
                print('Info null')
            if(price_element == None):
                print('Price null')
            if(warrent_element == None):
                print('Warrant null')
            await page.close()
            return {
                'Info' : None,
                'Detail Info' : None,
                'Price' : None,
                'Warrant' : None
            }
        if (info_table != None):
            info_html = await info_table.inner_html()
            info = self._info_parser(info_html)
        else:
            info = []
        if (info_table2 != None):
            info_html = await info_table.inner_html()
            info.extend(self._info_parser(info_html))
        else:
            info = None
        if (detail_info_table != None):
            detail_info_html = await detail_info_table.inner_html()
            detail_info = self._info_parser_detail(detail_info_html)
        else:
            detail_info = None
            
        price = await price_element.inner_html()   
        warrent = "Bảo hành theo linh kiện"    
        if (warrent_element != None):
            warrent_info = await warrent_element.inner_html()
            if (warrent_info != "Bảo hành theo linh kiện"):
                warrent = warrent_info
                
        await page.close()
        return {
            'Info' : info,
            'Detail Info' : detail_info,
            'Price' : price,
            'Warrant' : warrent
        }
    def _info_parser_detail(self,content : str):
        soup = BeautifulSoup(content,'html.parser')
        elements = soup.find_all('li')
        result = []
        for element in elements:
            # col_1 = element.select('span')[0]
            # col_2 = element.select('div')[0]
            new_ele = [element.get_text()]
            result.append(new_ele)
        return result
    def _info_parser(self,content : str):
        soup = BeautifulSoup(content,'html.parser')
        elements = soup.select('tr')
        result = []
        for element in elements:
            result.append(element.get_text())
        return result
    def _info_parser2(self,content : str):
        soup = BeautifulSoup(content,'html.parser')
        elements = soup.find_all('li')
        result = []
        for element in elements:
            # col_1 = element.select('span')[0]
            # col_2 = element.select('div')[0]
            new_ele = element.get_text()
            result.append(new_ele)
        return result

    async def save_spec(self,url,download_directory):
        path = os.path.join(download_directory,url.split('/')[-1]+'.json').replace('=','').replace('?','')
        if (not os.path.exists(path)):
            try:
                spec_info = await self._get_info(url)
                spec_info['Link'] = self.base_url+url
                if ((spec_info['Info'] == None and spec_info['Detail Info'] == None) or spec_info['Price'] == None or spec_info['Warrant'] == None):
                    self.exception_log.append({
                        'url' : url,
                        'exception' : 'NULL'
                    })
                    with open('exception.json','w') as file:
                        file.write(json.dumps(self.exception_log))
                    return
                with open(path,'w') as file:
                    file.write(json.dumps(spec_info))
            except Exception as e:
                print(e)
                self.exception_log.append({
                    'url' : url,
                    'exception' : str(e)
                })
        else:
            print('File {} aldready exits.'.format(url.split('/')[-1]+'.json'))
    async def batch_test(self):
        raw_links = await self._get_urls()
        links = self._urls_parser(raw_links)
        result = []
        for link in links:
            print(link)
            info = await self._get_info(link)
            result.append(info)
            print(info)
        return result