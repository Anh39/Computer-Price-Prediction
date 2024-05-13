from Crawler.intel_crawler import Handler
import asyncio,json

async def main():
    test = Handler()
    await test.init()
    await test.process()
    
    await asyncio.sleep(5)
    
    await test.close()
    
asyncio.run(main())