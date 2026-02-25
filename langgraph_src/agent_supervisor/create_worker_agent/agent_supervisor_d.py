import os

from langgraph.prebuilt import create_react_agent

from dotenv import load_dotenv
load_dotenv()
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
from langchain_tavily import TavilySearch


web_search = TavilySearch(max_results=3)
# web_search_results = web_search.invoke("who is the mayor of NYC?")

# print(web_search_results["results"][0]["content"])

research_agent = create_react_agent(
    model="deepseek-chat",
    tools=[web_search],
    prompt=(
        "You are a research agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with research-related tasks, DO NOT do any math\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="research_agent",
)

from langchain_core.messages import convert_to_messages


def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")


if __name__ == "__main__":
    for chunk in research_agent.stream(
        {"messages": [{"role": "user", "content": "上海市的市长是谁?"}]}
    ):
        pretty_print_messages(chunk)


#
# Update from node agent:
#
#
# ================================== Ai Message ==================================
# Name: research_agent
# Tool Calls:
#   tavily_search (call_0_6230f9cc-84f6-4e13-aa4f-94f4b3038034)
#  Call ID: call_0_6230f9cc-84f6-4e13-aa4f-94f4b3038034
#   Args:
#     query: 上海市的市长是谁
#     search_depth: basic
#
#
# Update from node tools:
#
#
# ================================= Tool Message =================================
# Name: tavily_search
#
# {"query": "上海市的市长是谁", "follow_up_questions": null, "answer": null, "images": [], "results": [{"url": "https://zh.wikipedia.org/zh-hans/%E4%B8%8A%E6%B5%B7%E5%B8%82%E5%B8%82%E9%95%BF%E5%88%97%E8%A1%A8", "title": "上海市市长列表- 维基百科，自由的百科全书", "content": "现任 龚正 2020年3月23日就职 ; 现任 龚正 2020年3月23日就职 · 5年 · 黄郛（特别市市长） 张群（上海市市长） 陈毅（上海市人民政府市长） · 1927年（上海特别市） 1930年（上海市）", "score": 0.8286204, "raw_content": null}, {"url": "https://zh.wikipedia.org/zh-hans/%E9%BE%9A%E6%AD%A3", "title": "龚正- 维基百科，自由的百科全书", "content": "2020年3月23日，任上海市副市长、代理市长。7月21日，上海市十五届人大四次会议正式选举龚正为上海市市长。 2022年6月28日，中国共产党上海市第十二届委员会", "score": 0.68798697, "raw_content": null}, {"url": "https://www.shanghai.gov.cn/nw48867/index.html", "title": "龚正_上海市人民政府", "content": "龚正，男，汉族，1960年3月生，在职研究生，经济学博士，中共党员。 我的分工. 领导市政府全面工作。", "score": 0.4766533, "raw_content": null}], "response_time": 1.5}
#
#
# Update from node agent:
#
#
# ================================== Ai Message ==================================
# Name: research_agent
#
# 龚正
