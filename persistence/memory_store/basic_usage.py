import uuid

from langgraph.store.memory import InMemoryStore
in_memory_store = InMemoryStore()

user_id = "1"
namespace_for_memory = (user_id, "memories")


memory_id = str(uuid.uuid4())
memory = {"food_preference" : "I like pizza"}
in_memory_store.put(namespace_for_memory, memory_id, memory)


memories = in_memory_store.search(namespace_for_memory)
print(memories[-1].dict())

# {'namespace': ['1', 'memories'],
# 'key': '8bc67bdc-cc18-4c19-beb6-19c63271f0c0',
# 'value': {'food_preference': 'I like pizza'},
# 'created_at': '2025-08-02T08:38:45.751271+00:00',
# 'updated_at': '2025-08-02T08:38:45.751382+00:00',
# 'score': None}



# {'value': {'food_preference': 'I like pizza'},
#  'key': '07e0caf4-1631-47b7-b15f-65515d4c1843',
#  'namespace': ['1', 'memories'],
#  'created_at': '2024-10-02T17:22:31.590602+00:00',
#  'updated_at': '2024-10-02T17:22:31.590605+00:00'}