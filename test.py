from Crawler.hacom_crawler import Handler
import asyncio,json

async def main():
    test = Handler()
    await test.init()
    result = await test.process()
    
    await asyncio.sleep(10)
    
    await test.close()
    
asyncio.run(main())