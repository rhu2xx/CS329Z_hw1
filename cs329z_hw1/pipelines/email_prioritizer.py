from cs329z_hw1.types import Email, LMCallable
import json

def prioritize_email(email: Email, lm: LMCallable)-> dict:
    """Problem (priority).

    Classify one email for its recipient, calling the model through ``lm``.
    Return {"category": "urgent" | "normal" | "ignore" | "unknown", "reason": str}.
    ``unknown`` means the reply stated no label.

    Rules the tests check:
    * Whatever the model replies, ``category`` is one of the four lower-case
      values and ``reason`` is a non-empty string.
    * A reply with no label word in it (empty, whitespace, text that names
      none of the three) gives "unknown", not a guess.
    * Live: the real model never gets "unknown".
    * The function does not raise and does not modify ``email``.
    * Live: at least 85% agreement with tests/fixtures/priority_gold.json.
    """
    priority_tag =["urgent", "normal", "ignore", "unknown"]
    email_body = email["body"]
    system_prompt = f"""You're an email priority assistant. Classify each email into one of four categories:
          {priority_tag}. Each email gets exactly one of four categories: {priority_tag}. 
          Please return the json result : ["category": #1, "reason": #2]  that #1 and #2 are the blanks you need to fill where #1 is the category the email is classified into and #2 is the reason why the email belongs to that category.
      """
    user_prompt = "Based on the following text, classify the email body into one of four labels. The content:\n"
    reply = lm([{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt + email_body}])
    result = json.loads(reply)

    return {"category": result["category"],  "reason" : result[ "reason"]}