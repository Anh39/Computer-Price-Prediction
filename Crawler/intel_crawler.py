import asyncio
import json
import os
import time
from playwright.async_api import async_playwright,Playwright,Browser,Page
from asyncio import Task
from bs4 import BeautifulSoup
import folder_path
import csv

class Handler:
    def __init__(self) -> None:
        self.interval = 0.1
        self.driver : Playwright.chromium = None
        self.browser : Browser = None
        self.base_url = "https://www.intel.com"
        self.exception_log = []
    async def process(self):
        jobs = {
            'i9' : {
                'download_directory' : folder_path.intel.i9,
                'family_url' : 'https://www.intel.com/content/www/us/en/products/details/processors/core/i9/products.html'
            },
            'i7' :  {
                'download_directory' : folder_path.intel.i7,
                'family_url' : 'https://www.intel.com/content/www/us/en/products/details/processors/core/i7/products.html'
            },
            'i5' : {
                'download_directory' : folder_path.intel.i5,
                'family_url' : 'https://www.intel.com/content/www/us/en/products/details/processors/core/i5/products.html'
            },
            'i3' : {
                'download_directory' : folder_path.intel.i3,
                'family_url' : 'https://www.intel.com/content/www/us/en/products/details/processors/core/i3/products.html'
            },
            'series-1' : {
                'download_directory' : folder_path.intel.series1,
                'family_url' : 'https://www.intel.com/content/www/us/en/products/details/processors/core/series-1/products.html'
            },
            'ultra' : {
                'download_directory' : folder_path.intel.ultra,
                'family_url' : 'https://www.intel.com/content/www/us/en/products/details/processors/core-ultra/products.html'
            }
        }
        for job_key in jobs:
            job = jobs[job_key]
            self.exception_log = []
            
            raw_links = await self._get_urls(job['family_url'])
            links = self._urls_parser(raw_links)
            
            with open(folder_path.join(job['download_directory'],'links.json'),'w') as file:
                file.write(json.dumps(links))
            
            for link in links:
                await self._download_spec(link,job['download_directory'])
            if (self.exception_log != []):
                with open(folder_path.join(job['download_directory'],'exception.json'),'w') as file:
                    file.write(json.dumps(self.exception_log))
           
    async def init(self):
        self.playwright_content_manager= async_playwright()
        self.playwright = await self.playwright_content_manager.start()
        self.browser = await self.playwright.chromium.launch(headless=True)
    async def close(self):
        await self.browser.close()
        await self.playwright_content_manager.__aexit__()
    async def _get_urls(self,family_url):
        page = await self.browser.new_page()
        await page.goto(family_url)
        result = None
        try:
            table_body = await page.query_selector('tbody')
            result = await table_body.inner_html()
        except:
            pass
        await page.close()
        return result
    def _urls_parser(self,content : str):
        soup = BeautifulSoup(content,'html.parser')
        elements = soup.select('.add-compare-wrap a')
        result = []
        for element in elements:
            result.append(element['href'])
        return result
    async def _download_spec(self,url : str,download_directory : str):
        url = self.base_url + url
        path = os.path.join(download_directory,url.split('/')[-2]+'.csv')
        if (not os.path.exists(path)):

            try:
                page = await self.browser.new_page()
                await page.goto(url)
                async with page.expect_download() as download_info:
                    selector_promp = '//html/body/main/div[3]/div/div[1]/div[2]/div/div/div/div/div[2]/section/div/div[2]/div[1]/div[2]/a'
                    await page.hover(selector_promp)
                    await page.locator(selector_promp).click()
                    download = await download_info.value
                    await download.save_as(path)
                    with open(path,'a',newline='') as csvfile:
                        csv_writer = csv.writer(csvfile)
                        csv_writer.writerow(['Link',url])
                    
            except Exception as e:
                print(e)
                self.exception_log.append({
                    'url' : url,
                    'exception' : str(e)
                })
            await page.close()
        else:
            print('File {} aldready exits.'.format(url.split('/')[-2]))