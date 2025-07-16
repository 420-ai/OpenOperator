def trim_user_message(message):
    trimmed_message = message.copy()

    for item in trimmed_message["content"]:
        if item.get("type") == "text":
            original_text = item.get("text", "")
            cutoff_marker = "\n=========================\n\nAttached"
            if cutoff_marker in original_text:
                item["text"] = original_text.split(cutoff_marker)[0]
                break  # assuming only one relevant text field to trim

    return trimmed_message