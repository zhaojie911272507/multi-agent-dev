import os

from crewai import LLM
from crewai.project import agent
from dotenv import load_dotenv
from sympy import print_glsl

load_dotenv()
# 定义 DeepSeek 模型实例
LLM_DS = LLM(
    model="deepseek/deepseek-chat",  # 或 "deepseek/deepseek-reasoner"
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 替换为实际 API Key
    stream=True,
)

from crewai import Agent

@agent
def researcher(self) -> Agent:
    return Agent(
        role="需求分析师",
        goal="分析用户需求并生成测试场景",
        llm=LLM_DS,  # 指定使用 DeepSeek 模型
        verbose=True,
        allow_delegation=False
    )


from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama

# 通过 Ollama 本地部署 DeepSeek-R1
# qllm = Ollama(model="deepseek-r1:14b")

# 定义测试分析师 Agent（使用 DeepSeek）
analyst = Agent(
    role="测试分析师",
    goal="从需求文档提取测试场景",
    backstory="分析需求并生成测试用例",
    llm=LLM_DS,  # 绑定 DeepSeek-R1
    temperature=0,
    verbose=True
)

# 定义自动化专家 Agent
expert = Agent(
    role="自动化专家",
    goal="生成 Selenium 测试脚本",
    llm=LLM_DS,  # 同样使用 DeepSeek
    tools=[]  # 可搭配工具
)

# 任务定义（分析师生成用例 -> 专家编写脚本）
testcases_task = Task(description="分析登录需求生成用例", agent=analyst)
scripts_task = Task(description="转换为 Python 脚本", agent=expert)

# 组建设备
crew = Crew(
    agents=[analyst, expert],
    tasks=[testcases_task, scripts_task],
    process=Process.sequential
)
result = crew.kickoff(inputs={"requirement": "用户登录功能需求文档..."})

print(result)
