# Digikala Crawler

## Setup steps:
  * Create **`outputs`** directory.
  * Install requirements:
    ```shell
    pip install -r requirements.txt
    ```
  * Copy the env template:
    ```shell
    cp env.sample.json env.json
    ```
    Modify the content of env as needed.
    
    Note: `executable_path` should follow the specified format and contains **#thread_cnt** number of chromedrivers:
    <br>chromedriver#1, chromedriver#2, ...
    <br>Read [this](https://googlechromelabs.github.io/chrome-for-testing/) for installing chromedriver.

## Run
In order to run the program:
```shell
python main.py
```
