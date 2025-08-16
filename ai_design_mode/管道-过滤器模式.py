from abc import ABC, abstractmethod
import threading
import time
import concurrent.futures


class DataRecord:
    def __init__(self, id, content):
        self.id = id
        self.content = content
        self.metadata = {
            "created": time.time(),
            "processed": None,
            "stages": []
        }

    def add_metadata(self, stage, result):
        self.metadata["stages"].append({
            "stage": stage,
            "result": result,
            "timestamp": time.time()
        })
        self.metadata["processed"] = time.time()

    def __str__(self):
        return f"Record {self.id}: {self.content[:20]}..."


class Filter(ABC):
    @abstractmethod
    def process(self, data):
        pass


class TextCleaner(Filter):
    def process(self, data):
        """清洗文本：去除标点、转换为小写"""
        cleaned = data.content.translate(
            str.maketrans('', '', ',.!?:;')
        ).lower().strip()
        data.add_metadata("TextCleaner", cleaned)
        print(f"[Clean] Record {data.id} cleaned: {cleaned[:10]}...")
        return data


class SentimentAnalyzer(Filter):
    def process(self, data):
        """模拟情感分析：根据关键词判断情感"""
        positive_words = ['good', 'great', 'excellent', 'positive', 'happy']
        negative_words = ['bad', 'poor', 'terrible', 'negative', 'sad']

        score = 0
        for word in positive_words:
            if word in data.content:
                score += 1

        for word in negative_words:
            if word in data.content:
                score -= 1

        sentiment = "positive" if score > 0 else "negative" if score < 0 else "neutral"
        data.add_metadata("SentimentAnalyzer", sentiment)
        print(f"[Sentiment] Record {data.id} sentiment: {sentiment}")
        return data


class KeywordExtractor(Filter):
    def process(self, data):
        """关键词提取：简单的词频统计"""
        words = [word for word in data.content.split() if len(word) > 3]
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1

        keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:3]
        data.add_metadata("KeywordExtractor", dict(keywords))
        print(f"[Keywords] Record {data.id} top keywords: {keywords}")
        return data


class DataPipeline:
    def __init__(self):
        self.filters = []
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    def add_filter(self, filter):
        self.filters.append(filter)

    def process(self, data):
        """顺序执行所有过滤器处理"""
        for filter in self.filters:
            try:
                data = filter.process(data)
            except Exception as e:
                print(f"Error processing record {data.id} at {filter.__class__.__name__}: {e}")
        return data

    def parallel_process(self, records):
        """并行处理数据记录"""
        results = []
        futures = [self.executor.submit(self.process, record) for record in records]

        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

        return results


if __name__ == "__main__":
    # 创建测试数据
    sample_data = [
        DataRecord(1, "This is a great product! I'm very happy with its performance."),
        DataRecord(2, "Bad experience. Poor quality and terrible customer service."),
        DataRecord(3, "The event was positive overall, but there were some minor issues."),
        DataRecord(4, "Neutral opinion, neither good nor bad, just average."),
        DataRecord(5, "An excellent solution for our problems. Highly recommended!")
    ]

    # 构建流水线
    pipeline = DataPipeline()
    pipeline.add_filter(TextCleaner())
    pipeline.add_filter(SentimentAnalyzer())
    pipeline.add_filter(KeywordExtractor())

    # 顺序处理演示
    print("\n===== 顺序处理演示 =====")
    result = pipeline.process(sample_data[0])
    print("\n处理完成后数据:")
    print(f"ID: {result.id}")
    print(f"内容: {result.content}")
    print(f"元数据: {result.metadata}")

    # 并行处理演示
    print("\n===== 并行处理演示 =====")
    parallel_results = pipeline.parallel_process(sample_data[1:])
    print("\n并行处理完成:")
    for record in parallel_results:
        print(f"Record {record.id} sentiment: {record.metadata['stages'][1]['result']}")
