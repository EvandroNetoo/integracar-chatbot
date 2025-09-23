from pathlib import Path
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_voyageai import VoyageAIEmbeddings
from pydantic_settings import BaseSettings


class EnvSettings(BaseSettings):
    class Config:
        env_file = str(Path(__file__).parent / '.env')
        env_file_encoding = 'utf-8'
        case_sensitive = True

    OPENAI_API_KEY: str = ''
    GROQ_API_KEY: str = ''
    VOYAGE_API_KEY: str = ''

env = EnvSettings()


# chat_model = ChatOpenAI(
#     model='gpt-4.1-nano-2025-04-14',
#     temperature=0,
#     openai_api_key=env.OPENAI_API_KEY,
# )

chat_model = ChatGroq(
    model='openai/gpt-oss-120b',
    temperature=0,
    api_key=env.GROQ_API_KEY,
)

response = chat_model.invoke("oi")
print(response.content)


# embedding_model = OpenAIEmbeddings(
#     model="text-embedding-3-small",
#     openai_api_key=env.OPENAI_API_KEY,
# )

embedding_model = VoyageAIEmbeddings(
    model='voyage-3.5-lite',
    voyage_api_key=env.VOYAGE_API_KEY,
)

vector = embedding_model.embed_query("oi")
print(len(vector), vector)
