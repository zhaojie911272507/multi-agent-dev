

# 使用 Langfuse 跟踪数据创建监督意图分类模型的过程。
# 步骤包括获取跟踪数据，使用 scikit-learn 和 sentence transformers 构建和训练模型，预测意图，并在 Langfuse 中为跟踪数据打标签。
# 此方法需要标记数据，但可以确保对预定义意图的一致预测，适用于明确定义的意图识别。


import  langfusepr.LLMApplicationIntentClassification.__init__

from langfuse import Langfuse

langfuse = Langfuse()

sample_utterances = [
    "Hello again",
    "Can you do anything else?",
    "Could you recommend a good book?",
    "I'd like to watch a drama",
    "Please revert to the beginning"
]

# Create dummy traces
for utterance in sample_utterances:
    langfuse.trace(input={"message": utterance})

# Fetch data from your project
# 从项目中获取数据
traces = langfuse.fetfetch_traces()
traces.data[0].dict()

# 构建用于分析的 DataFrame：
traces_list = []
for trace in traces.data:
    trace_info = [trace.id, trace.input["message"]]
    traces_list.append(trace_info)

import pandas as pd

traces_df = pd.DataFrame(traces_list, columns=["trace_id", "message"])
traces_df.head()


