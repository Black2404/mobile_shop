from django.apps import AppConfig

class ChatbotConfig(AppConfig):
    name = 'chatbot'

    def ready(self):
        # Import signals để kích hoạt tính năng lắng nghe
        import chatbot.signals
        print("Chatbot Signals đã được kích hoạt!")