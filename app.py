import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="GPT-5 Prompt Runner", layout="wide")
st.title("GPT-5 Prompt Runner with Web Search Function Tool")

api_key = st.text_input("Enter your OpenAI API key:", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    st.subheader("Prompts")
    prompt_input = st.text_area("Enter prompts (one per line):")

    if st.button("Run Prompts"):
        prompts = [p.strip() for p in prompt_input.split("\n") if p.strip()]
        if not prompts:
            st.warning("Enter at least one prompt.")
        else:
            for i, prompt in enumerate(prompts, 1):
                st.markdown(f"### Prompt {i}")
                st.markdown(f"> {prompt}")

                with st.spinner("Running..."):
                    try:
                        response = client.chat.completions.create(
                            model="gpt-5",
                            messages=[
                                {"role": "system", "content": "You are helpful assistant."},
                                {"role": "user", "content": prompt}
                            ],
                            functions=[
                                {
                                    "name": "web_search",
                                    "description": "Search the web for recent information relevant to the query",
                                    "parameters": {
                                        "type": "object",
                                        "properties": {
                                            "query": {"type": "string"}
                                        },
                                        "required": ["query"]
                                    }
                                }
                            ],
                            function_call="auto"  # or handle manually
                        )

                        message = response.choices[0].message

                        if message.get("function_call"):
                            # GPT-5 decided to call the function
                            func_name = message["function_call"]["name"]
                            arguments = message["function_call"]["arguments"]
                            # Do your function: e.g. call a web search API using arguments['query']
                            search_query = arguments.get("query")
                            # Here implement search, e.g. via requests to search engine:
                            search_results = your_web_search_api(search_query)

                            # Then send another message containing the function result
                            follow_up = client.chat.completions.create(
                                model="gpt-5",
                                messages=[
                                    {"role": "system", "content": "You are helpful assistant."},
                                    {"role": "user", "content": prompt},
                                    {
                                        "role": "function",
                                        "name": func_name,
                                        "content": search_results
                                    }
                                ]
                            )
                            final_answer = follow_up.choices[0].message.content
                            st.markdown("**Response:**")
                            st.write(final_answer)
                            st.markdown("**Web search results:**")
                            st.text(search_results)

                        else:
                            # No function call, normal answer
                            st.markdown("**Response:**")
                            st.write(message["content"])

                    except Exception as e:
                        st.error(f"Error: {e}")
