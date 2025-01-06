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
output_file = os.getenv('OUTPUT_FILE')


async def fetch_channel_stats():
    async with TelegramClient("anon", api_id, api_hash) as client:
        # Получаем объект канала
        # await ChannelScraper(client, channel_identifier, count_last_posts=20).scrap_stats()

        filters = await client(GetDialogFiltersRequest())

        # Выводим полученные фильтры
        for idx, filt in enumerate(filters.filters):
            if idx == 0: continue
            print(f"{idx + 1}. Фильтр: {filt.title}")

        # Спрашиваем пользователя, какие фильтры он хочет выбрать (ввод через пробел)
        selected_filters_input = input("Введите номера фильтров через пробел для анализа: ")

        # Преобразуем ввод в список номеров фильтров
        selected_filter_idxs = [int(idx) - 1 for idx in selected_filters_input.split()]
        # Создаем переменную для хранения статистики
        stats = []
        errors_count: int = 0
        # Выводим выбранные фильтры
        for selected_filter_idx in selected_filter_idxs:
            if 0 <= selected_filter_idx < len(filters.filters):
                selected_filter = filters.filters[selected_filter_idx]
                print(f"Анализ для папки: {selected_filter.title}")

                # Получаем список каналов в выбранной папке
                channels = selected_filter.include_peers  # Это список каналов в выбранной папке

                # Прогоняем каналы через метод scrap_stats
                for channel in channels:
                    # Пример вызова ChannelScraper
                    channel_scraper = ChannelScraper(client, channel.channel_id, count_last_posts=20)
                    channel_stats = await channel_scraper.scrap_stats()

                    # Добавляем результат в список stats
                    if channel_stats is not None:
                        stats.append(channel_stats)
                    else:
                        errors_count = errors_count + 1
            else:
                print("Неверный номер папки.")

        unique_stats = {}
        for scraper in stats:
            unique_stats[scraper.name] = scraper

        # Получаем список уникальных объектов
        unique_stats_list = list(unique_stats.values())

        save_to_excel_with_formatting(unique_stats_list, filename=f"{output_file}")
        print('Статистика сохранена в ', output_file)
        print('Ошибок при парсинге каналов: ', errors_count)


# Запуск основного кода
if __name__ == "__main__":
    asyncio.run(fetch_channel_stats())
