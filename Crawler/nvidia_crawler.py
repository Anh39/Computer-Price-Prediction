import asyncio
import json
import os
import time
from playwright.async_api import async_playwright,Playwright,Browser,Page
from asyncio import Task
from bs4 import BeautifulSoup
import folder_path
import csv,re
import pandas as pd

def extract_number(input_str):
    if (type(input_str) == int):
        return input_str
    numbers = re.findall(r'\d+', input_str)
    if (numbers) :
        return int(numbers[0])
    else:
        return None

class Handler:
    def __init__(self) -> None:
        self.interval = 0.1
        self.driver : Playwright.chromium = None
        self.browser : Browser = None
        self.base_url = "https://www.nvidia.com/en-us/geforce/graphics-cards/compare/"
        self.download_directory = folder_path.nvidia.gpu
        self.exception_log = []

    async def process(self):
        self.exception_log = []
        
        raw_tables = await self._get_tables(self.base_url)
        parsed_tables = []
        for raw_table in raw_tables:
            parsed_tables.append(self._table_parser(raw_table))
        
        rows = []
        
        for parsed_table in parsed_tables:
            rows.extend(parsed_table)
            
        df = pd.DataFrame(columns=rows[0].keys())
        for i in range(len(rows)):
            df.loc[i] = rows[i]
        
        df.to_csv(folder_path.join(self.download_directory,'result.csv'),index=False)    

        if (self.exception_log != []):
            with open(folder_path.join(self.download_directory,'exception.json'),'w') as file:
                file.write(json.dumps(self.exception_log))
                        

           
    async def init(self):
        self.playwright_content_manager= async_playwright()
        self.playwright = await self.playwright_content_manager.start()
        self.browser = await self.playwright.chromium.launch(headless=False)
    async def close(self):
        await self.browser.close()
        await self.playwright_content_manager.__aexit__()
    async def _get_tables(self,family_url):
        page = await self.browser.new_page()
        await page.goto(family_url)
        result = []
        s40_xpath = '//html/body/div[1]/div/div[3]/section/div/div/div[2]/div/div[1]/div/div[2]/div/table'
        s30_xpath = '//html/body/div[1]/div/div[5]/div/div/section/div/div/div[2]/div/div[1]/div/div[2]/div/table'
        s20_xpath = '//html/body/div[1]/div/div[7]/section/div/div/div[2]/div/div[1]/div/div[2]/div/table'
        s16_xpath = '//html/body/div[1]/div/div[9]/section/div/div/div[2]/div/div[1]/div/div[2]/div/table'
        table_xpaths = [s40_xpath,s30_xpath,s20_xpath,s16_xpath]
        for table_xpath in table_xpaths:
            table_element = await page.query_selector(table_xpath)
            table_content = await table_element.inner_html()
            result.append(table_content)
        await page.close()
        return result
    def _table_parser(self,content : str):
        soup = BeautifulSoup(content,'html.parser')
        head_elements = soup.select('th')
        heads = []
        for i in range(1,len(head_elements)):
            head_element = head_elements[i]
            local_result = (head_element.getText())
            # local_result = ''
            # for data_element in data_elements:
            #     local_result += data_element.text
            heads.append(local_result)
        category_elements = soup.select_one('tbody').select('tr')
        results = []
        for head in heads:
            results.append({
                'Name' : head
            })
        for category_element in category_elements:
            rows = category_element.select('td')
            category = rows[0].getText()
            for i in range(len(results)):
                if len(rows) > i+1:
                    results[i][category] = rows[i+1].getText()

        return results

