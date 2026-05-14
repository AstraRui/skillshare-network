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
    # количество завершенных сделок как инициатора и участника
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

        # Жёсткий фильтр пересечения навыков которые предлагает кандидат с навыками которые я хочу получить
        matched_for_me = set(c_offered.keys()) & set(my_wanted.keys())
        coverage = len(matched_for_me) / len(my_wanted)
        if coverage < 0.5:
            continue

        # S_навыки
        A = coverage
        matched_for_him = set(my_offered.keys()) & set(c_wanted.keys())
        B = len(matched_for_him) / len(c_wanted) if c_wanted else 0.0
        s_skills = A * 0.6 + B * 0.4

        # S_уровень
        level_scores: list[float] = []
        for skill_id in matched_for_me:
            level_scores.append(
                1.0 - abs(c_offered[skill_id] - my_wanted[skill_id]) / 3.0
            )
        s_level = sum(level_scores) / len(level_scores) if level_scores else 0.0

        # S_активность
        last_active = candidate.last_active_at
        if last_active is None:
            s_activity = 0.5
        else:
            if last_active.tzinfo is None:
                last_active = last_active.replace(tzinfo=UTC)
            days_passed = (datetime.now(UTC) - last_active).days
            s_activity = math.exp(-days_passed / 30)

        # S_репутация
        reviews = candidate_reviews.get(cid, [])
        if not reviews:
            s_reputation = 0.5
        else:
            n = len(reviews)

            avg_rating = sum(reviews) / n
            rating_norm = avg_rating / 5.0
            if n < 5:
                rating_norm -= (5 - n) / 5 * 0.2
                rating_norm = max(0.0, rating_norm)

            # опыт(завершенные сделки)
            exp_count = exchange_counts.get(cid, 0)
            # логарифм количества сделок(чем их больше тем сильнее замедляется рост опыта), деление на math.log(201)
            # нужно чтобы нормировать опыт от 0 до 1 для конечной формулы
            exp_norm = math.log(1 + exp_count) / math.log(201)

            # генератор.доля положительных отзывов
            positive = sum(1 for r in reviews if r >= 4)
            pos_share = positive / n
            # * 0.8 — сжимает диапазон, не даёт достигать крайних значений 0 и 1
            # + 0.18 — сдвигает вверх, дает минимальный кредит доверия даже при 0% положительных
            # Математически: при любом pos_share результат будет в диапазоне [0.18, 0.98] — никогда не 0 и не 1.
            if n < 10:
                pos_share = pos_share * 0.8 + 0.18

            # вес рейтинга 0.4 тк он важнее всего, остальные по 0.3 равноценно
            s_reputation = 0.4 * rating_norm + 0.3 * exp_norm + 0.3 * pos_share

        # Чем выше степень — тем сильнее низкая оценка "тянет вниз" финальный результат.
        score = (
            s_skills**1.4 *
            s_level**0.9 *
            s_activity**0.5 *
            s_reputation**0.8
        )

        exp_count = exchange_counts.get(cid, 0)
        if exp_count < 3:
            created = candidate.created_at
            if created.tzinfo is None:
                created = created.replace(tzinfo=UTC)
            days_since_reg = (datetime.now(UTC) - created).days
            bonus = 0.1 * max(0.0, 1.0 - days_since_reg / 30.0)
            score *= (1.0 + bonus)

        completeness = [
            bool(candidate.full_name),
            bool(candidate.avatar_url),
            bool(c_offered),
            bool(c_wanted)
        ]
        if sum(completeness) / 4 < 0.5:
            score *= 0.85
        score = min(score, 1.0)

        # Запускается итератор по множеству, и берет первый элемент
        primary_skill_id = next(iter(matched_for_me))
        category_id = skill_categories_id.get(primary_skill_id)

        results.append({
            "user_id": cid,
            "score": score,
            "category_id": category_id,
            "matched_skills": sorted(matched_for_me),
            "s_skills": round(s_skills, 4),
            "s_level": round(s_level, 4),
            "s_activity": round(s_activity, 4),
            "s_reputation": round(s_reputation, 4),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    results = [r for r in results if r["score"] >= 0.2]

    category_counts: dict[int | None, int] = {}
    final: list[dict] = []

    for r in results:
        category_current_candidate = r["category_id"]
        cnt = category_counts.get(category_current_candidate, 0)
        if cnt < 2:
            final.append(r)
            category_counts[category_current_candidate] = cnt + 1
        if len(final) >= 20:
            break

    return final