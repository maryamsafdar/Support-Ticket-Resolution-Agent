import argparse, json, os
from dotenv import load_dotenv
from graph import graph

def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject", required=True)
    parser.add_argument("--description", required=True)
    args = parser.parse_args()

    inputs = {
        "subject": args.subject,
        "description": args.description,
        # initialize required state keys
        "attempts": 0,
        "drafts_history": [],
        "reviews_history": [],
        "context_docs": [],
        "retrieval_query": "",
        "draft": "",
        "final_response": "",
        "escalated": False,
        "category": "General",
        "review": {"approved": False, "feedback": "", "reasons": []},
    }

    # stream=False for simple run; you can stream events if needed
    result = graph.invoke(inputs)
    print("\n=== FINAL RESPONSE ===\n")
    print(result.get("final_response", ""))
    print("\n---")
    print("Category:", result.get("category"))
    print("Attempts:", result.get("attempts"))
    print("Escalated:", result.get("escalated"))

if __name__ == "__main__":
    main()
