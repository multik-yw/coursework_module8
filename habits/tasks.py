import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import Habit
import logging


logger = logging.getLogger(__name__)


class TelegramBot:
    @staticmethod
    def send_message(chat_id, text):
        """Отправка сообщения через Telegram Bot """
        if not chat_id:
            logger.warning("Telegram ID not provided")
            return None

        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not bot_token:
            logger.error("Telegram bot token not configured")
            return None

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        params = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(
                url,
                params=params,
                timeout=(5, 10))

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error("Telegram API timeout error")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Telegram API connection error: {str(e)}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Telegram API request error: {str(e)}")
            return None
        except (ValueError, KeyError) as e:
            logger.error(f"Telegram API response parsing error: {str(e)}")
            return None


@shared_task(bind=True, max_retries=3)
def send_telegram_notification(self, telegram_id, message):
    if not telegram_id:
        logger.warning("Telegram ID not provided")
        return False

    try:
        result = TelegramBot.send_message(
            chat_id=int(telegram_id),
            text=message
        )
        if result and result.get('ok'):
            return True
        raise self.retry(exc=Exception(f"Telegram error: {result}"))
    except Exception as e:
        logger.error(f"Error: {e}")
        raise self.retry(exc=e)


@shared_task
def check_habits_and_notify():
    """Проверка привычек и отправка уведомлений"""
    now = timezone.now()
    current_time = now.time()

    habits = Habit.objects.filter(
        time__hour=current_time.hour,
        time__minute=current_time.minute
    ).exclude(
        last_completed__date=now.date()
    ).select_related('user')

    for habit in habits:
        if habit.user.telegram_id:
            message = (
                f"⏰ Напоминание о привычке:\n"
                f"*Действие:* {habit.action}\n"
                f"*Место:* {habit.place}\n"
                f"*Время выполнения:* {habit.duration} сек."
            )

            send_telegram_notification.delay(
                habit.user.telegram_id,
                message
            )
            logger.info(f"Scheduled notification for habit {habit.id} to user {habit.user.id}")