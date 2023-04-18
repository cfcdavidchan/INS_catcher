import asyncio
from instagram_crawler import instagram_crawler
import os
import json
from datetime import datetime
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))

print("Preparing to start the crawler")
# Retrieving all crawler parameter
crawler_param_json = "crawler_param.json"
CRAWLER_PARAM_JSON_PATH = os.path.join(SCRIPT_PATH,crawler_param_json)
with (open(CRAWLER_PARAM_JSON_PATH)) as f:
    crawler_param_json = json.load(f)
# Retrieving target storage directory
crawler_store_dir = crawler_param_json["store_dir"]
CRAWLED_DATA = os.path.join(SCRIPT_PATH,crawler_store_dir)
# Retrieving target username
username_list = crawler_param_json['target_username']
page_sleep_time = crawler_param_json['crawl_sleep_time']
print(f"\n\nTarget username: {username_list}\n\n")

if asyncio.get_event_loop().is_closed():
    asyncio.set_event_loop(asyncio.new_event_loop())
loop = asyncio.get_event_loop()
# Creating async crawler task
tasks = []
for username in username_list:
    test_case = instagram_crawler(username=username, store_folder=CRAWLED_DATA, page_sleep_time=page_sleep_time)
    tasks.append(test_case.async_main())
# Retrieving the start time
start_time = datetime.now()
start_time_str = start_time.strftime("%m/%d/%Y, %H:%M:%S")
print(f"{start_time_str} Start crawling...")
loop.run_until_complete(asyncio.gather(*tasks))
loop.close()
# Retrieving the end time
end_time = datetime.now()
end_time_str = end_time.strftime("%m/%d/%Y, %H:%M:%S")
print(f"{end_time_str} Finished crawling")
print(f'Total run time: {end_time - start_time}')

# # username = "ckykylie"
# username_list = ["ckykylie", "kylie.yim"]
# def normal_crawl():
#     for username in username_list:
#         test_case = instagram_crawler(username= username, store_folder="normal_crawled_data")
#         test_case.main()
#
# def async_crawl():
#     if asyncio.get_event_loop().is_closed():
#         asyncio.set_event_loop(asyncio.new_event_loop())
#     loop = asyncio.get_event_loop()
#     tasks = []
#     for username in username_list:
#         test_case = instagram_crawler(username=username, store_folder="async_crawled_data")
#         tasks.append(test_case.async_main())
#     all_request = asyncio.gather(*tasks)
#     result = loop.run_until_complete(all_request)
#     loop.close()
#
# print("Testing normal request speed --------")
# normal_testing = timeit.timeit(normal_crawl, number=1)
# print("Finished normal request speed testing --------")
# print("Testing async request speed --------")
# async_testing = timeit.timeit(async_crawl, number=1)
# print("Finished async request speed testing --------")
# print(f'Average run time of normal loop request: {normal_testing}')
# print(f'Average run time of async loop request: {async_testing}')