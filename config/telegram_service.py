import requests
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

logger = logging.getLogger(__name__)


class TelegramBot:
    BASE_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/"

    @classmethod
    def send_message(cls, chat_id, text):
        url = f"{cls.BASE_URL}sendMessage"
        try:
            response = requests.post(
                url, json={"chat_id": chat_id, "text": str(text), "parse_mode": "Markdown"}, timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return None

    @classmethod
    def set_webhook(cls, webhook_url):
        url = f"{cls.BASE_URL}setWebhook"
        try:
            response = requests.post(url, json={"url": webhook_url})
            logger.info(f"Webhook set: {response.json()}")
            return response.json()
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return None

    @classmethod
    @method_decorator(csrf_exempt)
    def webhook_handler(cls, request):
        if request.method == "POST":
            data = request.json()
            chat_id = data["message"]["chat"]["id"]
            text = data["message"].get("text", "")

            if text == "/start":
                response_text = "Бот трекера привычек.\n" "Используй /help для списка команд."
                cls.send_message(chat_id, response_text)

            return JsonResponse({"status": "ok"})
        return JsonResponse({"status": "error"}, status=400)
