import jq
import json


if __name__ == "__main__":
    file_path = "../data/knowledge_base.json"
    with open(file_path) as f:
        data = json.load(f)

# res = jq.compile(".[]").input(data).all()
res = jq.compile(".[]").input(data).all()
print(res, res[-1], len(res))