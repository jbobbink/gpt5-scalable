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
                            tools=[{"type": "web_search"}],
                            tool_choice="auto",  # let GPT decide when to search
                        )

                        # Get model's answer
                        answer = response.choices[0].message.content
                        st.markdown("**Response:**")
                        st.write(answer)

                        # Show web search sources if available
                        sources = getattr(response.choices[0].message, "refusal", None)
                        if hasattr(response, "output") and hasattr(response.output, "references"):
                            refs = response.output.references
                            if refs:
                                st.markdown("**Sources:**")
                                for ref in refs:
                                    st.write(f"- {ref['url']}")

                    except Exception as e:
                        st.error(f"Error: {e}")
else:
    st.info("👆 Please enter your API key to begin.")
