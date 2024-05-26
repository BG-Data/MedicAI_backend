import sys

import requests
from loguru import logger

logger.add(
    sys.stderr,
    colorize=True,
    format="<yellow>{time}</yellow> {level} <green>{message}</green>",
    filter="FLowise API",
    level="INFO",
)


# Puramente para testes. Funciona! TODO -> refatorar para incorporar infos sensíves, .env e ajustar essa API para ser mais elegante.
class FlowiseApi:
    # API_URL = cfg.FLOWISE_URL
    # headers = {"Authorization": f"Bearer {cfg.FLOWISE_HEADER}"}

    def __init__(self, cfg):
        self.API_URL = cfg.FLOWISE_URL
        self.headers = {"Authorization": f"Bearer {cfg.FLOWISE_TOKEN}"}

    def query_model(self, question: str) -> dict:
        logger.info(f"Question made to ai: {question}")
        response = requests.post(
            self.API_URL, headers=self.headers, json={"question": question}, timeout=120
        )
        logger.info(f"BOT response>>> {response}")
        return response.json()

    def retrieve_response(self, response: dict) -> str:
        return response.get("text")

    def ask_bot(self, question: str) -> str:
        answer = self.query_model(question)
        return self.retrieve_response(answer)
