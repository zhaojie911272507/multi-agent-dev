from pprint import pprint

from duckduckgo_search import DDGS

results2 = DDGS().text(
    keywords="tesla的今天的股票？",  # 输入中文查询词
    region="cn-zh",           # 指定中国-中文区域
    max_results=10
)
print("搜索结果：")
pprint(results2)


