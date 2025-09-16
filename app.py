import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="GPT-5 Prompt Runner", layout="wide")

st.title("🔎 GPT-5 Prompt Runner with Web Search")

# --- API Key input ---
api_key = st.text_input("Enter your OpenAI API Key:", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    # --- Prompt input ---
    st.subheader("Prompts")
    prompts_text = st.text_area(
        "Enter prompts (one per line):",
        placeholder="Example:\nWhat's the latest news on AI?\nCompare Fintiba and Expatrio for blocked accounts in Germany"
    )

    if st.button("Run Prompts"):
        if not prompts_text.strip():
            st.warning("Please enter at least one prompt.")
        else:
            prompts = [p.strip() for p in prompts_text.split("\n") if p.strip()]
            
            for i, prompt in enumerate(prompts, start=1):
                st.markdown(f"### Prompt {i}: {prompt}")

                with st.spinner("Thinking..."):
                    try:
                        response = client.chat.completions.create(
                            model="gpt-5",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant."},
                                {"role": "user", "content": prompt}
                            ],
                            tools=[{"type": "web_search"}],  # enable web search tool
                            tool_choice="auto",  # let GPT decide
                            include=["web_search_call.action.sources"],  # include sources
                        )

                        answer = response.choices[0].message.content
                        st.markdown("**Response:**")
                        st.write(answer)

                        # --- Show sources if available ---
                        if hasattr(response.choices[0].message, "tool_calls"):
                            for tool_call in response.choices[0].message.tool_calls:
                                if tool_call.function.name == "web_search":
                                    st.markdown("**Sources:**")
                                    st.json(tool_call.function.arguments)

                    except Exception as e:
                        st.error(f"Error: {e}")
else:
    st.info("👆 Please enter your API key to begin.")
