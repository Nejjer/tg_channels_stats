from transformers import pipeline

combined_text = "Документация и модели: Изучите доступные задачи и модели в официальной документации Transformers. Это поможет подобрать подходящую модель и оптимизировать её использование."


class Summarizer:
    def __init__(self):
        print('Start initialization model')
        self.llm_summarizer = pipeline("summarization", model="t5-3b")  # Инициализация локальной модели
        print('Initialization done!')

    def summarize(self):
        print('Start summarize!')
        summary = self.llm_summarizer(combined_text, max_length=100, min_length=30, do_sample=False)
        print('Summarize done!')
        # Сохраняем результат анализа
        summary_text = summary[0]['summary_text']
        print(f"Краткое описание контента: {summary_text}")


# Запуск основного кода
if __name__ == "__main__":
    Summarizer().summarize()
