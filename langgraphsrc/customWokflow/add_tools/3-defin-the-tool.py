import os

# 需要在终端输入tavily_api_key
# def _set_env(var: str):
#     if not os.environ.get(var):
#         os.environ[var] = getpass.getpass(f"{var}: ")
#
# _set_env("TAVILY_API_KEY")

from dotenv import load_dotenv

load_dotenv()
os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")


from langchain_tavily import TavilySearch

tool = TavilySearch(max_results=2)
tools = [tool]
result = tool.invoke("What's a 'node' in LangGraph?")

print(result)

result ={'query': "What's a 'node' in LangGraph?",
         'follow_up_questions': None,
         'answer': None,
         'images': [],
         'results': [
             {'url': 'https://medium.com/@cplog/introduction-to-langgraph-a-beginners-guide-14f9be027141',
              'title': "Introduction to LangGraph: A Beginner's Guide - Medium",
              'content': '*   **Stateful Graph:** LangGraph revolves around the concept of a stateful graph, where each node in the graph represents a step in your computation, and the graph maintains a state that is passed around and updated as the computation progresses. LangGraph supports conditional edges, allowing you to dynamically determine the next node to execute based on the current state of the graph. Image 10: Introduction to AI Agent with LangChain and LangGraph: A Beginner’s Guide Image 18: How to build LLM Agent with LangGraph\u200a—\u200aStateGraph and Reducer Image 20: Simplest Graphs using LangGraph Framework Image 24: Building a ReAct Agent with Langgraph: A Step-by-Step Guide Image 28: Building an Agentic RAG with LangGraph: A Step-by-Step Guide',
              'score': 0.65252984,
              'raw_content': None
              },
             {'url': 'https://www.linkedin.com/pulse/fast-explain-langgraph-l%C6%B0u-v%C3%B5-7u2qc',
              'title': 'Understanding LangGraph: A Brief Guide - LinkedIn',
              'content': '(Assuming InterviewState, node functions, graph definition, and \'memory\' checkpointer from above) # Let\'s re-compile without interrupts for this demo to see more steps automatically app_for_timetravel = workflow.compile(checkpointer=memory) thread_id_tt = "my_timetravel_session_1" config_tt = {"configurable": {"thread_id": thread_id_tt}} # Let\'s run the graph for a couple of steps print("--- Running graph for Time Travel Demo (Step 1) ---") # No input needed initially for ask_question app_for_timetravel.invoke(None, config=config_tt) # ask_question_node runs # Now it\'s expecting an answer for get_human_answer app_for_timetravel.invoke({"answer": "Initial Answer"}, config=config_tt) # get_human_answer runs, then ask_question again print("\\n--- Current State History ---") history = app_for_timetravel.get_state_history(config_tt) for i, state_snapshot in enumerate(history): print(f"Snapshot {i}:") print(f" Timestamp (thread_ts): {state_snapshot.config[\'configurable\'][\'thread_ts\']}") print(f" State Values: {state_snapshot.values}") print(f" Next to run: {state_snapshot.next}") # What would run if we resume from here # Let\'s say we want to go back to the state after the first question was asked, # but before "Initial Answer" was provided.',
              'score': 0.4116553,
              'raw_content': None
              }
         ],
         'response_time': 1.46
         }