from __future__ import annotations

from decimal import Decimal
from random import Random

from faker import Faker


fake = Faker("ru_RU")
random = Random(42)


def generate_full_name() -> str:
    return fake.name()


def generate_email(index: int) -> str:
    return f"test.user.{index}@example.com"


def generate_phone(index: int) -> str:
    return f"+7999{index:07d}"


def generate_rating() -> Decimal:
    return Decimal(str(round(random.uniform(4.2, 5.0), 2)))


def generate_avatar_url(full_name: str) -> str:
    return f"https://api.dicebear.com/7.x/initials/svg?seed={full_name}"


def generate_listing_description() -> str:
    return fake.text(max_nb_chars=160)


def generate_interest_message() -> str:
    messages = [
        "Здравствуйте! Мне интересно ваше предложение. Готов обсудить обмен навыками.",
        "Привет! Хочу попробовать обмен, думаю, мы можем быть полезны друг другу.",
        "Добрый день! Интересное предложение, готов обсудить детали.",
        "Здравствуйте! Могу помочь со своей стороны и хотел бы получить ваш навык.",
    ]
    return random.choice(messages)


def generate_chat_messages() -> list[str]:
    return [
        "Привет! Увидел твой отклик, давай обсудим обмен навыками.",
        "Привет! Да, мне интересно. Что удобнее разобрать сначала?",
        "Предлагаю начать с короткого созвона и плана занятий.",
        "Отлично, тогда договорились. Я подготовлю вопросы.",
    ]


def generate_completed_message() -> str:
    messages = [
        "Спасибо за обмен! Всё прошло отлично.",
        "Спасибо, было полезно. Думаю, сделку можно завершать.",
        "Отличная работа, я доволен результатом обмена.",
    ]
    return random.choice(messages)


def generate_cancelled_message() -> str:
    messages = [
        "Пока не получается продолжить, давай отменим сделку.",
        "К сожалению, сейчас не смогу продолжить обмен.",
        "Предлагаю отменить сделку и вернуться к обмену позже.",
    ]
    return random.choice(messages)


def generate_review_comment() -> str:
    comments = [
        "Отличный обмен навыками. Всё объяснено понятно и по делу.",
        "Хороший участник, быстро отвечает и выполняет договоренности.",
        "Обмен прошёл успешно, было комфортно работать вместе.",
        "Понравился подход к обучению и обратная связь.",
    ]
    return random.choice(comments)
