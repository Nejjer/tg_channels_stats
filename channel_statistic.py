from dataclasses import dataclass

from telethon import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerChannel


@dataclass
class ChannelStatistic:
    """
    Класс для хранения статистики Telegram-канала.

    Атрибуты:
        name (str): Название канала.
        count_subs (int): Количество подписчиков канала.
        average_views (float): Среднее количество просмотров на пост.
        average_reacts (float): Среднее количество реакций на пост (лайки, репосты и т.д.).
        freq_posts_per_week (float): Средняя частота публикаций в неделю.
        average_comments (float): Среднее количество комментариев на пост.
        average_message_length (float): Среднее длина сообщения.
        engagement_rate (float): Вовлеченность.
    """
    name: str = ""
    count_subs: int = -1
    average_views: float = -1
    average_reacts: float = -1
    freq_posts_per_week: float = -1
    average_comments: float = -1
    average_message_length: float = -1
    engagement_rate: float = -1


class ChannelScraper:
    def __init__(self, client: TelegramClient, channel_identifier: int, count_last_posts: int = 20):
        """Инициализирует объект ChannelStatistic с переданным client."""
        self.client = client
        self.channel_identifier = channel_identifier
        self.count_last_posts = count_last_posts
        self.statistic = ChannelStatistic()

    async def scrap_stats(self) -> ChannelStatistic:
        try:
            channel = await self.client.get_entity(PeerChannel(self.channel_identifier))

            # Получаем полную информацию о канале
            full_channel = await self.client(GetFullChannelRequest(channel))

            # Количество подписчиков
            subscribers_count = full_channel.full_chat.participants_count

            print(f"\nСтатистика для канала {channel.title}:")
            self.statistic.name = channel.title
            self.statistic.count_subs = subscribers_count

            # Получаем последние 20 сообщений
            messages = await self.client.get_messages(channel, limit=self.count_last_posts)

            # Анализируем сообщения
            if not messages:
                print("Нет сообщений для анализа.")
                raise

            total_views = 0
            total_reactions = 0
            total_comments = 0
            first_date = messages[-1].date
            last_date = messages[0].date
            message_lengths = []

            for message in messages:
                total_views += message.views or 0
                total_reactions += len(message.reactions.results) if message.reactions else 0
                if message.replies:
                    total_comments += message.replies.replies or 0
                message_lengths.append(len(message.message or ""))

            # Количество точек после запятой
            decimal_places = 2

            # Среднее количество постов в неделю
            date_diff = (last_date - first_date).days + 1
            weeks_count = max(1, date_diff / 7)
            avg_posts_per_week = round(len(messages) / weeks_count, decimal_places)

            # Средние показатели
            avg_views = round(total_views / len(messages), decimal_places)
            avg_reactions = round(total_reactions / len(messages), decimal_places)
            avg_comments = round(total_comments / len(messages), decimal_places)

            # Длина сообщений
            avg_message_length = round(sum(message_lengths) / len(message_lengths), decimal_places)
            engagement_rate = round(((avg_views + avg_reactions + avg_comments) / subscribers_count) * 100,
                                    2) if subscribers_count > 0 else 0

            self.statistic.average_comments = avg_comments
            self.statistic.average_views = avg_views
            self.statistic.average_reacts = avg_reactions
            self.statistic.freq_posts_per_week = avg_posts_per_week
            self.statistic.average_message_length = avg_message_length
            self.statistic.engagement_rate = engagement_rate
            print(self.statistic)
            return self.statistic
        except Exception as e:
            print("Не удалось собрать статистику для", self.channel_identifier)
            print(e)
