from cs329z_hw1.types import Email, LMCallable
from cs329z_hw1.pipelines.email_prioritizer import prioritize_email
from concurrent.futures import ThreadPoolExecutor
import json




def daily_digest(emails: list[Email], lm: LMCallable) -> str:
    """Problem (daily_digest).

    ``emails`` is a list of emails from one calendar day (UTC date); it may
    be empty. Return the morning summary as a string.

    Rules the tests check:
    * Returns a string for every model reply, and for an empty day.
    * The function does not modify ``emails``.
    * Live (tests/fixtures/digest_days.json): the digest is not empty and
      at most 300 words (``len(digest.split())``) as the model wrote it; for
      each gold urgent email it contains the name of the company, project or
      site that email is about; it contains no term listed for the gold
      ignore emails.
    """
    def classify(email):
        result = prioritize_email(email, lm)
        if result["category"] == "unknown":
            result["category"] = "normal"
        return result
    
    with ThreadPoolExecutor(max_workers=5) as pool:
        priorities = list(pool.map(classify, emails))
    rank = {"urgent": 0, "normal": 1, "ignore": 2} 
    thread_group = {}
    for email, priority in zip(emails, priorities):
        match priority["category"]:
            case "ignore":
                continue
            case "normal" | "urgent":
                thread_id = email["thread_id"]
                current = thread_group.get(thread_id)

                if current is None or (
                    rank[priority["category"]] < rank[current["priority"]["category"]]
                ):
                    thread_group[thread_id] = {"email": email, "priority": priority}
    ordered_items = sorted(
        thread_group.values(),
        key=lambda item: rank[item["priority"]["category"]],
    )
    system_prompt = """You're an daily email summary assistant. 
                        Given the emails of one day, write a morning email digest for a business employee. 
                        Please control word count <= 300. Put urgent items first. Explicitly name the company, project, or site mentioned in each urgent item."""
    items_text = json.dumps(ordered_items, ensure_ascii=False, indent=2)
    reply = lm([{"role": "system", "content": system_prompt},
                    {"role": "user", "content": items_text}])

    return reply
