import asyncio
import json
from tortoise import Tortoise
from models.models import Users


async def get_user_referrals(telegram_id):
    try:
        referrals = await Users.filter(ref_id=telegram_id).all()
        print(f"Referrals for {telegram_id}: {[user.telegram_id for user in referrals]}")
        return referrals
    except Exception as e:
        print(f"Error in getting referrals {telegram_id}: {e}")
        return []


async def build_referral_tree(telegram_id, depth=0, max_depth=None, visited=None):
    if visited is None:
        visited = set()
    if telegram_id in visited:
        print(f"Cycle detected in user {telegram_id}, stop recursion.")
        return {}
    visited.add(telegram_id)

    tree = {}
    try:
        referrals = await get_user_referrals(telegram_id)
    except Exception as e:
        print(f"Error in building tree for user {telegram_id}: {e}")
        return tree

    if not referrals:
        return tree

    for referral in referrals:
        if max_depth is not None and depth >= max_depth:
            continue
        try:
            subtree = await build_referral_tree(
                referral.telegram_id,
                depth=depth + 1,
                max_depth=max_depth,
                visited=visited
            )
            tree[referral.telegram_id] = subtree
        except Exception as e:
            print(f"Error in processing a referral {referral.telegram_id}: {e}")
            continue

    return tree


async def main():
    try:
        await Tortoise.init(
            db_url='postgres://myuser:12345@localhost/raptor',
            modules={'models': ['models.models']}
        )

        target_telegram_id = 'dev'
        referral_tree = await build_referral_tree(target_telegram_id)

        print(json.dumps({target_telegram_id: referral_tree}, indent=2))


    except Exception as e:
        print(f"Error: {e}")
    finally:
        await Tortoise.close_connections()


if __name__ == '__main__':
    asyncio.run(main())
