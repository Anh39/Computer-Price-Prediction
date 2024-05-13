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
        self.base_url = "https://www.amd.com"
        self.exception_log = []
        self.column_mapping = [
            'Name',
            'Family',
            'Series',
            'Form Factor',
            '# of CPU Cores',
            '# of Threads',
            'Max. Boost Clock',
            'Base Clock',
            'L2 Cache',
            'L3 Cache',
            'Default TDP',
            'L1 Cache',
            'AMD Configurable TDP (cTDP)',
            'Processor Technology for CPU Cores',
            'Unlocked for Overclocking',
            'CPU Socket',
            'Thermal Solution (PIB)',
            'Recommended Cooler',
            'Thermal Solution (MPK)',
            'Max. Operating Temperature',
            'Launch Date',
            'Os Support',
            'PCIE Version',
            'System Memory Type',
            'Memory Channels',
            'System Memory Specification',
            'Graphics Model',
            'Graphics Core Count',
            'Graphics Frequency',
            'AMD Ryzen AI',
            'Product ID Boxed',
            'Product ID Tray',
            'Product ID MPK',
            'Supported Technologies'
        ]
    async def process(self):
        jobs = {
            'cpu' : {
                'download_directory' : folder_path.amd.cpu,
                'family_url' : 'https://www.amd.com/en/products/specifications/processors.html'
            }
        }
        for job_key in jobs:
            job = jobs[job_key]
            self.exception_log = []
            
            raw_tables = await self._get_tables(job['family_url'])
            parsed_tables = []
            for raw_table in raw_tables:
                parsed_tables.append(self._table_parser(raw_table))
            
            rows = []
            
            for parsed_table in parsed_tables:
                rows.extend(parsed_table)
                
            df = pd.DataFrame(columns=self.column_mapping)
            for i in range(len(rows)):
                df.loc[i] = rows[i]
            
            df.to_csv(folder_path.join(folder_path.amd.cpu,'result.csv'),index=False)    

            if (self.exception_log != []):
                with open(folder_path.join(job['download_directory'],'exception.json'),'w') as file:
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
        condition_xpath = '//html/body/div[1]/div/div/div/div/div[3]/div/div/div/div/div/div/div/div/div/div/div/div/div[3]'
        xpath = '//html/body/div[1]/div/div/div/div/div[3]/div/div/div/div/div/div/div/div/div/div/div/div/div[2]/div[2]/table/tbody'
        next_xpath = '//html/body/div[1]/div/div/div/div/div[3]/div/div/div/div/div/div/div/div/div/div/div/div/div[4]/ul/li[9]'
        def check_end(input_str : str):
            elements = input_str.split('to')[-1].split('of')
            num1 = extract_number(elements[0])
            num2 = extract_number(elements[1])
            return num1 == num2
        while (True):
            condition_element = await page.query_selector(condition_xpath)
            text = await condition_element.inner_text()
            if (check_end(text)):
                break
            table_body = await page.query_selector(xpath)
            local_result = await table_body.inner_html()
            result.append(local_result)
            next_element = await page.query_selector(next_xpath)
            await next_element.click()
        await page.close()
        return result
    def _table_parser(self,content : str):
        soup = BeautifulSoup(content,'html.parser')
        elements = soup.select('tr')
        results = []
        for element in elements:
            cols = element.select('td')
            new_ele = []
            for col in cols:
                new_ele.append(col.text)
            results.append(new_ele)
        final_results = []
        for result in results:
            final_result = {}
            for i in range(len(result)):
                final_result[self.column_mapping[i]] = result[i]
            final_results.append(final_result)
        return final_results

