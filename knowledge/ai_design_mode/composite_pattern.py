# 组合模式 (Composite) - 原文件: 组合模式.py
# 场景：集成多个AI服务构成决策系统
# 示例：风控系统组合：欺诈检测模型 + 信用评分模型 + 规则引擎


# AI系统组合：情感分析 + 关键词提取
class AIComponent:
    def process(self, text):
        pass


class SentimentAnalyzer(AIComponent):
    def process(self, text):
        return {"sentiment": "positive" if 'good' in text else "negative"}


class KeywordExtractor(AIComponent):
    def process(self, text):
        return {"keywords": text.split()[:2]}


class AIPipeline:
    def __init__(self):
        self._components = []

    def add(self, component):
        self._components.append(component)

    def process(self, text):
        result = {}
        for comp in self._components:
            result.update(comp.process(text))
        return result


# 构建组合服务
pipeline = AIPipeline()
pipeline.add(SentimentAnalyzer())
pipeline.add(KeywordExtractor())

# 执行组合处理
result = pipeline.process("This is a good example of AI design patterns")
print("Combined Result:", result)
# 输出: {'sentiment': 'positive', 'keywords': ['This', 'is']}
