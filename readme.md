# QUIZ BOT
This code contains two bots, one for Telegram and one for VK. You are provided with questions that you can answer, and you can skip the current question by calling for the next one or by giving up. In this way, you will be shown the correct answer before a new question is provided.

## Installation
1. Clone `git clone ...`
2. Install venv `python3 -m venv venv`
3. Activate venv `source venv/bin/python`
4. Install dependencies `pip install -r requirements.txt`
5. Create `.env` file in the project root directory and enter the env vars
6. Run the script(s)
   * `python3 tg.py`
   * `python3 vk.py`

## Required env vars
`TELEGRAM_TOKEN`  
`REDIS_PASSWORD`  
`VK_TOKEN`  

## Deployed bots
[tg_bot](https://t.me/frqhero_quiz_bot)  
[vk_bot](https://vk.com/public222171772)