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
    API_URL = (
        "http://flowise:3000/api/v1/prediction/0b64be2d-6c5f-4eed-a5b3-7d3ff4c77c30"
    )
    headers = {"Authorization": "Bearer qvQgnW1Cw7JIcF+iKGb5hwNsJhWqCVQ+kR4slFoN5oY="}

    def __init__(self):
        pass

    def query_model(self, question: str) -> dict:
        response = requests.post(
            self.API_URL, headers=self.headers, json={"question": question}, timeout=120
        )
        return response.json()

    def retrieve_response(self, response: dict) -> str:
        return response.get("text")

    def ask_bot(self, question: str) -> str:
        answer = self.query_model(question)
        return self.retrieve_response(answer)
