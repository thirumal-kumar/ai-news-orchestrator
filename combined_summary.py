import re

def combine_snippets(snippets):
    clean = []

    for snip in snippets:
        if not isinstance(snip, str):
            continue

        s = re.sub(r"\s+", " ", snip).strip()
        if len(s) < 40:
            continue

        clean.append(s)

    if not clean:
        return "No meaningful content available for summary."

    joined = "\n\n".join(clean)
    return f"### Unified AI Summary\n\n{joined}"
