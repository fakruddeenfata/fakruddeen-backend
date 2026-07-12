# Fata AI Ultra - Core Backend Engine

Wannan shi ne babban injin backend na Fata AI wanda aka gina shi don jure nauyin biliyoyin masu amfani (Ultra-Scale).

## Abubuwan da Aka Yi Amfani Da Su
- **FastAPI**: Don kera kofofin API masu saurin gaske.
- **Google GenAI SDK**: Don magana da Gemini 2.5 models cikin yanayi na async stream.
- **Redis**: Don iyakance kiran mutane (Rate Limiting) da adana tarihin hira na dan lokaci (Caching).
- **MongoDB**: Don adana babban tarihin hirarrakin mutane.
- **PostgreSQL**: Don kula da rajista da asusun masu amfani.

## Yadda Ake Kunna Shi (Local Setup)

1. Sanya dukkan sirrin tsarin (Environment Variables):
```bash
export GEMINI_API_KEY="AQ.Ab8RN6KxeAsauh85yb0vRkDWKTvp15bLeau9p5nPIM0xhMqnbQ"
export DATABASE_URL="postgresql+asyncpg://postgres:password@localhost/fata_auth"
export MONGO_URL="mongodb://localhost:27017"
export REDIS_URL="redis://localhost:6379/0"