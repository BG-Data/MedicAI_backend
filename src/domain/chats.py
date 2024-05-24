from schemas.chats import ChatsInsert


class ChatsDomain:
    def check_message_content(self, insert_schema: ChatsInsert) -> str:
        if insert_schema.chat_id:
            return "insert_new_message"
        if not insert_schema.chat_id:
            return "insert_new_chat"
        raise ValueError("Algo falhou em check_chat")
