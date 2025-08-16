
# 责任链 + 策略 + 装饰器 + 代理
from test.装饰器 import log_execution
from test.责任链 import TextCleaner, ResultFormatter


class CompositeAISystem:
    def __init__(self):
        self.pipeline = self._create_pipeline()
        self.cache = {}

    def _create_pipeline(self):
        # 创建处理链
        return TextCleaner(
            self._create_strategy_router(
                ResultFormatter()
            )
        )

    def _create_strategy_router(self, successor):
        # 策略选择器
        class StrategyRouter(Handler):
            def handle(self, request):
                model_type = 'complex' if len(request['clean_text']) > 10 else 'simple'
                # 根据长度选择不同策略
                strategies = {
                    'simple': lambda x: sum(ord(c) for c in x) / len(x),
                    'complex': lambda x: max(ord(c) for c in x)
                }
                request['prediction'] = strategies[model_type](request['clean_text'])
                print(f"Used {model_type} model")
                if successor:
                    return successor.handle(request)

        return StrategyRouter()

    @log_execution
    def process(self, text):
        # 缓存检查
        if text in self.cache:
            print("Using cached result")
            return self.cache[text]

        # 执行处理链
        result = self.pipeline.handle({'text': text})
        self.cache[text] = result
        return result


# 使用复合系统
system = CompositeAISystem()
print("Result:", system.process("Short text"))
print("----")
print("Result:", system.process("Longer text for complex processing"))
print("----")
print("Result:", system.process("Short text"))  # 缓存命中