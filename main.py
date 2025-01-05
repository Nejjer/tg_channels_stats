import asyncio
import os

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.messages import GetDialogFiltersRequest

from channel_statistic import ChannelScraper
from excel import save_to_excel_with_formatting

# Загружаем переменные окружения из файла .env
load_dotenv()

# Use your own values from my.telegram.org
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')


async def fetch_channel_stats():
    async with TelegramClient("anon", api_id, api_hash) as client:
        # Получаем объект канала
        # await ChannelScraper(client, channel_identifier, count_last_posts=20).scrap_stats()

        filters = await client(GetDialogFiltersRequest())

        # Выводим полученные фильтры
        for idx, filt in enumerate(filters.filters):
            if idx == 0: continue
            print(f"{idx + 1}. Фильтр: {filt.title}")

        # Спрашиваем пользователя, какой фильтр он хочет выбрать
        selected_filter_idx = int(input("Введите номер папки для анализа: ")) - 1

        if 0 <= selected_filter_idx < len(filters.filters):
            selected_filter = filters.filters[selected_filter_idx]
            print(f"Выбрана папка: {selected_filter.title}")

            # Получаем список каналов в выбранной папке
            channels = selected_filter.include_peers  # Это список каналов в выбранной папке

            # Создаем переменную для хранения статистики
            stats = []

            stop = 0
            # Прогоняем каналы через метод scrap_stats
            for channel in channels:
                # Пример вызова ChannelScraper
                # Примечание: предположим, что ChannelScraper имеет метод scrap_stats для обработки каналов
                channel_scraper = ChannelScraper(client, channel.channel_id, count_last_posts=20)
                channel_stats = await channel_scraper.scrap_stats()
                stop = stop + 1

                # Добавляем результат в список stats
                if channel_stats is not None:
                    stats.append(channel_stats)
                # if stop > 10:
                #     break

            save_to_excel_with_formatting(stats, filename=f"{selected_filter.title}.xlsx")

        else:
            print("Неверный номер папки.")


# Запуск основного кода
if __name__ == "__main__":
    asyncio.run(fetch_channel_stats())
