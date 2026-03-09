import time
import vk_api
from config import VK_TOKEN, VK_API_VERSION


class VKClient:
    def __init__(self):
        session = vk_api.VkApi(token=VK_TOKEN, api_version=VK_API_VERSION)
        self.api = session.get_api()

    def _call(self, method, **kwargs):
        try:
            return method(**kwargs)
        except vk_api.exceptions.ApiError as e:
            if e.code == 6:  # Too many requests
                time.sleep(1)
                return method(**kwargs)
            raise

    def get_user(self, user_id: str) -> dict:
        fields = (
            "about,activities,bdate,books,career,city,connections,contacts,"
            "country,domain,education,followers_count,games,home_town,"
            "interests,last_seen,military,movies,music,nickname,occupation,"
            "online,personal,photo_200,quotes,relatives,relation,schools,"
            "sex,site,status,tv,universities,verified,is_no_index"
        )
        result = self._call(
            self.api.users.get,
            user_ids=user_id,
            fields=fields,
        )
        return result[0] if result else {}

    def get_friends(self, user_id: int, count: int = 200) -> list[dict]:
        try:
            result = self._call(
                self.api.friends.get,
                user_id=user_id,
                fields="photo_50,city",
                count=count,
                order="hints",
            )
            return result.get("items", [])
        except vk_api.exceptions.ApiError:
            return []

    def get_mutual_friends(self, source_uid: int, target_uids: list[int]) -> dict:
        """Returns {target_uid: [mutual_friend_ids]}"""
        if not target_uids:
            return {}
        # batch by 100
        result = {}
        for i in range(0, len(target_uids), 100):
            batch = target_uids[i : i + 100]
            try:
                rows = self._call(
                    self.api.friends.getMutual,
                    source_uid=source_uid,
                    target_uids=batch,
                )
                for row in rows:
                    result[row["id"]] = row.get("common_friends", [])
            except vk_api.exceptions.ApiError:
                pass
            time.sleep(0.34)  # stay within 3 req/s
        return result

    def get_groups(self, user_id: int, count: int = 100) -> list[dict]:
        try:
            result = self._call(
                self.api.groups.get,
                user_id=user_id,
                extended=1,
                fields="members_count",
                count=count,
            )
            return result.get("items", [])
        except vk_api.exceptions.ApiError:
            return []

    def get_photos_with_geo(self, user_id: int, count: int = 200) -> list[dict]:
        try:
            result = self._call(
                self.api.photos.getAll,
                owner_id=user_id,
                count=count,
                extended=1,
                photo_sizes=0,
            )
            items = result.get("items", [])
            return [p for p in items if p.get("lat") and p.get("long")]
        except vk_api.exceptions.ApiError:
            return []

    def search_users(
        self,
        query: str,
        city_id: int = 0,
        count: int = 20,
    ) -> list[dict]:
        fields = "bdate,city,country,education,photo_50"
        kwargs = dict(q=query, fields=fields, count=count)
        if city_id:
            kwargs["city"] = city_id
        try:
            result = self._call(self.api.users.search, **kwargs)
            return result.get("items", [])
        except vk_api.exceptions.ApiError:
            return []

    def resolve_screen_name(self, screen_name: str) -> dict:
        return self._call(self.api.utils.resolveScreenName, screen_name=screen_name)

    def get_users_batch(self, user_ids: list[int]) -> list[dict]:
        if not user_ids:
            return []
        result = []
        for i in range(0, len(user_ids), 1000):
            batch = user_ids[i : i + 1000]
            try:
                rows = self._call(
                    self.api.users.get,
                    user_ids=batch,
                    fields="photo_50",
                )
                result.extend(rows)
            except vk_api.exceptions.ApiError:
                pass
            time.sleep(0.34)
        return result
