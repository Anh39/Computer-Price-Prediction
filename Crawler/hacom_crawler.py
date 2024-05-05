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
        self.base_url = "https://hacom.vn"
        self.exception_log = []
    async def init(self):
        self.playwright_content_manager= async_playwright()
        self.playwright = await self.playwright_content_manager.start()
        self.browser = await self.playwright.chromium.launch()
        
    async def process(self):
        jobs = {
            'pc_game' : {
                'download_directory' : folder_path.hacom.pc_game,
                'family_url' : 'https://hacom.vn/pc-gaming-streaming'
            },
            'pc_graphic' :  {
                'download_directory' : folder_path.hacom.pc_graphic,
                'family_url' : 'https://hacom.vn/pc-workstations'
            },
            'pc_work' : {
                'download_directory' : folder_path.hacom.pc_office,
                'family_url' : 'https://hacom.vn/may-tinh-de-ban'
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
        stop_value = '\n          \n  '
        results = []
        i = 1
        while (True):
            page = await self.browser.new_page()
            await page.goto(family_url+'/{}/'.format(str(i)))
            i+=1
            result = None
            try:
                case_list = await page.query_selector('.cate-list-prod')
                result = await case_list.inner_html()
                if (result == stop_value):
                    await page.close()
                    break
            except:
                pass
            await page.close()
            results.append(result)
        return results

    def _urls_parser(self,content : str):
        soup = BeautifulSoup(content,'html.parser')
        elements = soup.select('.p-img a')
        result = []
        for element in elements:
            result.append(element['href'])
        return result
    async def _get_info(self,url : str):        
        url = self.base_url + url
        page = await self.browser.new_page()
        await page.goto(url)
        warrant_xpaths = [
            '//html/body/div[6]/div[4]/div[1]/div[3]/div/div[1]/div[4]/div[2]/div[2]',
            '//html/body/div[6]/div[4]/div[1]/div[3]/div/div[1]/div[3]/div[2]/div[2]',
            '//html/body/div[6]/div[4]/div[1]/div[3]/div/div[1]/div[5]/div[2]/div[2]'
        ]
        for warrant_xpath in warrant_xpaths:
            warrent_element = await page.query_selector(warrant_xpath)
            if (warrent_element != None):
                break

        price_xpaths = [
            '//html/body/div[6]/div[4]/div[1]/div[3]/div/div[1]/div[3]/strong[1]',
            '//html/body/div[6]/div[4]/div[1]/div[3]/div/div[1]/div[4]/strong[1]',
            '//html/body/div[6]/div[4]/div[1]/div[3]/div/div[1]/div[5]/strong[1]'
        ]
        for price_xpath in price_xpaths:
            price_element = await page.query_selector(price_xpath)
            if (price_element != None):
                break
        
        info_xpaths = [
            '//html/body/div[6]/div[4]/div[3]/div[1]/div[2]/div[1]/div/div[1]/table/tbody',
            '//html/body/div[6]/div[4]/div[1]/div[3]/div/div[1]/div[3]/ul',
            '//html/body/div[6]/div[4]/div[1]/div[3]/div/div[1]/div[2]/ul'
        ]
        for info_xpath in info_xpaths:
            info_table = await page.query_selector(info_xpath)
            if (info_table != None):
                break
        
        if (info_table == None or price_element == None):
            if (info_table == None):
                print('Info null')
            elif(price_element == None):
                print('Price null')
            elif(warrent_element == None):
                print('Warrant null')
            await page.close()
            return {
                'Info' : None,
                'Price' : None,
                'Warrent' : None
            }
        content = await info_table.inner_html()
        if (info_xpath == '//html/body/div[6]/div[4]/div[3]/div[1]/div[2]/div[1]/div/div[1]/table/tbody'):
            info = self._info_parser(content)
        else:
            info = self._info_parser2(content)
        price = await price_element.evaluate('(element) => element.getAttribute("data-price")')    
        warrent = "Bảo hành theo linh kiện"    
        if (warrent_element != None):
            warrent_info = await warrent_element.inner_html()
            if (warrent_info != "Bảo hành theo linh kiện"):
                warrent = warrent_info


            
        await page.close()
        return {
            'Info' : info,
            'Price' : price,
            'Warrent' : warrent
        }
    def _info_parser(self,content : str):
        soup = BeautifulSoup(content,'html.parser')
        elements = soup.select('tr')
        result = []
        for element in elements:
            cols = element.select('td')
            new_ele = []
            for col in cols:
                new_ele.append(col.text)
            result.append(new_ele)
        return result
    def _info_parser2(self,content : str):
        soup = BeautifulSoup(content,'html.parser')
        elements = soup.select('li')
        result = []
        for element in elements:
            result.append(element.text)
        return result

    async def save_spec(self,url,download_directory):
        path = os.path.join(download_directory,url.split('/')[-1]+'.json')
        if (not os.path.exists(path)):
            try:
                spec_info = await self._get_info(url)
                spec_info['Link'] = self.base_url+url
                if (spec_info['Info'] == None or spec_info['Price'] == None):
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