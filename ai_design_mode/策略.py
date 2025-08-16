# 策略模式 (Strategy)
# 场景：
# 动态选择模型（如根据设备类型选择移动端/云端模型）
# A/B测试不同算法（BERT vs. LSTM文本分类）
# 降级策略（CPU量化模型备用方案）

# 动态选择AI模型
class ModelStrategy:
    def execute(self, data):
        pass


class GPTStrategy(ModelStrategy):
    def execute(self, data):
        return f"GPT: {len(data.split())} tokens"


class BERTStrategy(ModelStrategy):
    def execute(self, data):
        return f"BERT: {data.upper()}"


class ModelRouter:
    def __init__(self):
        self.strategies = {
            'gpt': GPTStrategy(),
            'bert': BERTStrategy()
        }

    def route_request(self, model_type, data):
        if model_type not in self.strategies:
            raise ValueError(f"Unsupported model: {model_type}")
        return self.strategies[model_type].execute(data)


# 使用路由
router = ModelRouter()
print(router.route_request('gpt', "Hello AI world"))  # GPT: 3 tokens
print(router.route_request('bert', "Hello AI world"))  # BERT: HELLO AI WORLD
