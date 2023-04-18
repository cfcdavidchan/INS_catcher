# INS_catcher

This repo is to download the videos or images a list of targeted instagram username.


## Parameter
Please edit the parameter`crawler_param.json` before running it
1. store_dir: the target directory that you want to store the `videos` and `pictures`. The script will create a directory with the username and subdirectories, video and picture, inside it.
2. target_username: the list of target instagram username.
3. crawl_sleep_time: the sleep time of every request, which is to prevent being block by the host


## Execution
1. Docker compose<br>
    Just simply run the following command based on `docker-compose.yml` to run the crawler with docker compose:<br>
    `docker compose up`
2. python<br>
    Installing all the necessary package is needed before running the crawler<br>
    `pip install -r requirements.txt`<br>
    Then you may run the crawl with:<br>
    `python main.py`