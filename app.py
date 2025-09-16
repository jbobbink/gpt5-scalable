import streamlit as st
import json
import time
from typing import List, Optional
from openai import OpenAI

st.set_page_config(page_title="GPT-5 Prompt Runner", layout="wide")
st.title("🔎 GPT-5 Prompt Runner with Web Search & Debug Info")

# --- API Key input ---
api_key = st.text_input("Enter your OpenAI API Key:", type="password")

def ask_gpt5_with_web_search(
    client: OpenAI,
    prompt: str,
    allowed_domains: Optional[List[str]] = None,
    reasoning_effort: str = "low"
):
    """
    Ask GPT-5 with built-in web search, return answer + sources + full response dict.
    """
    tools = [{"type": "web_search"}]
    if allowed_domains:
        tools[0]["filters"] = {"allowed_domains": allowed_domains}

    start_time = time.time()
    response = client.responses.create(
        model="gpt-5",
        reasoning={"effort": reasoning_effort},
        tools=tools,
        tool_choice="auto",  # let the model decide if/when to search
        include=["web_search_call.action.sources"],  # include sources for preview
        input=prompt,
    )
    duration = time.time() - start_time

    # --- Extract sources ---
    sources = []
    try:
        resp_dict = json.loads(json.dumps(response, default=lambda o: getattr(o, "__dict__", str(o))))
        for item in resp_dict.get("output", []):
            if item.get("type") == "web_search_call":
                action = item.get("action") or {}
                for src in action.get("sources", []) or []:
                    title = src.get("title") or src.get("url") or "Untitled source"
                    url = src.get("url")
                    sources.append((title, url))

        # Fallback: citations inside messages
        if not sources:
            for item in resp_dict.get("output", []):
                if item.get("type") == "message":
                    for c in item.get("content", []):
                        for ann in c.get("annotations", []) or []:
                            if ann.get("type") == "url_citation" and ann.get("url"):
                                title = ann.get("title") or ann["url"]
                                sources.append((title, ann["url"]))
    except Exception:
        pass

    # Convert response to plain JSON for inspection
    full_json = json.loads(json.dumps(response, default=lambda o: getattr(o, "__dict__", str(o))))

    return response.output_text, sources, duration, full_json


if api_key:
    client = OpenAI(api_key=api_key)

    st.subheader("Prompts")
    prompts_text = st.text_area(
        "Enter prompts (one per line):",
        placeholder="Example:\nWho is Jan-Willem Bobbink?\nWhat's the capital of France?"
    )

    if st.button("Run Prompts"):
        if not prompts_text.strip():
            st.warning("Please enter at least one prompt.")
        else:
            prompts = [p.strip() for p in prompts_text.split("\n") if p.strip()]
            for i, prompt in enumerate(prompts, 1):
                st.markdown(f"## Prompt {i}")
                st.markdown(f"> {prompt}")

                with st.spinner("Asking GPT-5..."):
                    try:
                        answer, sources, duration, full_json = ask_gpt5_with_web_search(client, prompt)

                        st.markdown("**Response:**")
                        st.write(answer)

                        if sources:
                            st.markdown("**Web Search Sources:**")
                            for j, (title, url) in enumerate(sources, 1):
                                st.markdown(f"{j}. [{title}]({url})")

                        st.caption(f"⏱️ Duration: {duration:.2f} seconds")

                        # --- Debug: full JSON output ---
                        with st.expander("🔍 Full API Response (JSON)"):
                            st.json(full_json)

                    except Exception as e:
                        st.error(f"Error: {e}")
else:
    st.info("👆 Please enter your API key to begin.")
