from Crawler.anphat_crawler_lap import Handler as Anphat
from Crawler.fpt_cralwer_lap import Handler as FPT
from Crawler.hacom_crawler_lap import Handler as Hacom
from Crawler.intel_crawler import Handler as Intel
from Crawler.nvidia_crawler import Handler as Nvidia
import asyncio,json

mapping = {
    'Anphat' : Anphat,
    'FPT' : FPT,
    'Hacom' : Hacom,
    'Intel' : Intel,
    'Nvidia' : Nvidia
}

async def main(input_type : str):
    test = mapping[input_type]()
    await test.init()
    await test.process()
    
    await asyncio.sleep(5)
    
    await test.close()
    
asyncio.run(main('Anphat'))