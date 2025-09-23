from core.env import env
from langchain_groq import ChatGroq
from langchain_voyageai import VoyageAIEmbeddings

chat_model = ChatGroq(
    model='openai/gpt-oss-20b',
    temperature=0,
    api_key=env.GROQ_API_KEY,
)

embedding_model = VoyageAIEmbeddings(
    model='voyage-3.5-lite',
    output_dimension=1024,
    voyage_api_key=env.VOYAGE_API_KEY,
)
