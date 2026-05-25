from __future__ import annotations

from app.models.exchange import Exchange, ExchangeStatus


def can_post_in_deal_chat(exchange: Exchange) -> bool:
    return exchange.status in (ExchangeStatus.discussion, ExchangeStatus.active)


def is_deal_chat_read_only(exchange: Exchange) -> bool:
    return exchange.status in (ExchangeStatus.completed, ExchangeStatus.cancelled)