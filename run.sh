docker run -d -p 6379:6379 redislabs/redisearch:2.6.0
pip install -r requirements.txt
jina auth login
streamlit run main.py