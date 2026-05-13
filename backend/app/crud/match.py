from __future__ import annotations

import math
from datetime import UTC, datetime

from app.models import Exchange, ExchangeStatus, ListingInterest, ListingInterestStatus
from app.models.review import Review
from app.models.user import User
from app.models.skill import UserSkillsWanted, UserSkillsOffered, Skill

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

async def find_matches(db: AsyncSession, user_id: int) -> list[dict]:
    # Навыки текущего пользователя
    my_offered_rows = list(await db.execute(
        select(UserSkillsOffered.skill_id, UserSkillsOffered.level)
        .where(UserSkillsOffered.user_id == user_id)
    ))
    my_offered: dict[int, int] = {r.skill_id: r.level for r in my_offered_rows}

    my_wanted_rows = list(await db.execute(
        select(UserSkillsWanted.skill_id, UserSkillsWanted.desired_level)
        .where(UserSkillsWanted.user_id == user_id)
    ))
    my_wanted: dict[int, int] = {r.skill_id: r.desired_level for r in my_wanted_rows}

    if not my_wanted:
        return []

    my_wanted_ids = list(my_wanted.keys())
    my_offered_ids = list(my_offered.keys())

    # Поиск кандидатов

    # предлагает ли этот кандидат навыки которые я хочу?
    offers_what_i_want = (
        select(UserSkillsOffered.user_id)
        .where(
            UserSkillsOffered.user_id == User.id,
            UserSkillsOffered.skill_id.in_(my_wanted_ids),
        )
        .correlate(User)
        .exists()
    )

    # Условия попадания в кандидаты
    conditions = [
        User.id != user_id,
        User.is_deleted.is_(False), # is False?
        offers_what_i_want
    ]

    # хочет ли этот кандидат навыки которые я предлагаю?
    if my_offered_ids:
        wants_what_i_offer = (
            select(UserSkillsWanted.user_id)
            .where(
                UserSkillsWanted.user_id == User.id,
                UserSkillsWanted.skill_id.in_(my_offered_ids)
            )
            .correlate(User)
            .exists()
        )
        conditions.append(wants_what_i_offer)

    # внешний запрос на который указывали в подзапросе (.correlate(User))
    candidates: list[User] = list(await db.scalars( # scalars потому что мы хотим получить все данные, с execute получаем только те которые сами запросили
        select(User).where(*conditions) # * распаковывает список на отдельные аргументы (a, b, c) условно
    ))
    if not candidates:
        return []

    candidate_ids = [c.id for c in candidates]

    # Пакетная загрузка данных

    # Навыки который кандитат может предложить и получить

    # получаем навыки кандидата если он есть в списке кандидатов
    c_offered_rows = list(await db.execute(
        select(
            UserSkillsOffered.user_id,
            UserSkillsOffered.skill_id,
            UserSkillsOffered.level
        )
        .where(UserSkillsOffered.user_id.in_(candidate_ids))
    ))
    candidate_offers: dict[int, dict[int, int]] = {}
    for r in c_offered_rows:
        if r.user_id not in candidate_offers:
            candidate_offers[r.user_id] = {}
        candidate_offers[r.user_id][r.skill_id] = r.level

    c_wanted_rows = list(await db.execute(
        select(
            UserSkillsWanted.user_id,
            UserSkillsWanted.skill_id,
            UserSkillsWanted.desired_level
        )
        .where(UserSkillsWanted.user_id.in_(candidate_ids))
    ))
    candidate_wanted: dict[int, dict[int, int]] = {}
    for r in c_wanted_rows:
        if r.user_id not in candidate_wanted:
            candidate_wanted[r.user_id] = {}
        candidate_wanted[r.user_id][r.skill_id] = r.desired_level

    # Отзывы кандидатов
    review_rows = list(await db.execute(
        select(Review.reviewed_id, Review.rating)
        .where(
            Review.reviewed_id.in_(candidate_ids),
            Review.is_deleted.is_(False),
            Review.is_hidden.is_(False),
        )
    ))
    candidate_reviews: dict[int, list[int]] = {}
    for r in review_rows:
        if r.reviewed_id not in candidate_reviews:
            candidate_reviews[r.reviewed_id] = []
        candidate_reviews[r.reviewed_id].append(r.rating)

    initiator_rows = list(await db.execute(
        select(Exchange.initiator_id, func.count().label("cnt"))
        .where(
            Exchange.initiator_id.in_(candidate_ids),
            Exchange.status == ExchangeStatus.completed,
            Exchange.is_deleted.is_(False),
        )
        .group_by(Exchange.initiator_id)
    ))
    # количество завершенных сделок как инициатора
    exchange_counts: dict[int, int] = {r.initiator_id: r.cnt for r in initiator_rows}

    participant_rows = list(await db.execute(
        select(ListingInterest.responder_id, func.count().label("cnt"))
        .join(Exchange, Exchange.listing_id == ListingInterest.listing_id)
        .where(
            ListingInterest.responder_id.in_(candidate_ids),
            ListingInterest.status == ListingInterestStatus.accepted,
            Exchange.status == ExchangeStatus.completed,
            Exchange.is_deleted.is_(False),
        )
        .group_by(ListingInterest.responder_id)
    ))
    for r in participant_rows:
        exchange_counts[r.responder_id] = (
            exchange_counts.get(r.responder_id, 0) + r.cnt
        )
    skill_cat_rows = list(await db.execute(
        select(Skill.id, Skill.category_id)
        .where(Skill.id.in_(my_wanted_ids))
    ))
    skill_categories_id: dict[int, int] = {r.id: r.category_id for r in skill_cat_rows}

    # Доделать после добавления updated_at в UserSkillsOffered
    fraudulent_user_ids: frozenset[int] = frozenset()

    results: list[dict] = []

    for candidate in candidates:
        cid = candidate.id
        if cid in fraudulent_user_ids:
            continue

        c_offered = candidate_offers.get(cid, {})
        c_wanted = candidate_wanted.get(cid, {})