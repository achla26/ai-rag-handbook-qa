import streamlit as st
import requests
from datetime import datetime
from src.config.settings import settings

st.set_page_config(
    page_title="Handbook Q&A",
    page_icon="📚",
    layout="wide"
)

# Header
st.title("📚 Handbook Q&A")
st.markdown("*Ask questions about company policies with cited answers*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    top_k = st.slider("Sources to retrieve", 1, 10, 3)
    show_sources = st.checkbox("Show source details", value=True)
    show_guardrails = st.checkbox("Show guardrail checks", value=True)
    
    st.divider()
    
    # Health Check
    if st.button("🏥 Health Check"):
        try:
            response = requests.get(f"{settings.api_url}/health")
            health = response.json()
            
            if health["status"] == "healthy":
                st.success("All systems healthy!")
            else:
                st.warning("System degraded")
            
            st.json(health["components"])
        except Exception as e:
            st.error(f"Health check failed: {e}")
    
    st.divider()
    
    # Ingest
    st.header("📥 Ingest Documents")
    if st.button("🔄 Re-ingest Documents"):
        try:
            response = requests.post(f"{settings.api_url}/ingest")
            result = response.json()
            
            if result["success"]:
                st.success(f"✅ Ingested {result['documents_loaded']} docs → {result['chunks_created']} chunks")
            else:
                st.error(f"Errors: {result['errors']}")
        except Exception as e:
            st.error(f"Ingest failed: {e}")

# Main Chat
st.divider()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        if msg["role"] == "assistant" and "metadata" in msg:
            meta = msg["metadata"]
            
            # Sources
            if show_sources and meta.get("sources"):
                with st.expander("📚 Sources"):
                    for src in meta["sources"]:
                        st.markdown(f"**[{src['id']}]** {src['source']} (score: {src['score']:.2f})")
            
            # Guardrails
            if show_guardrails and meta.get("guardrails"):
                gr = meta["guardrails"]
                with st.expander("🛡️ Guardrails"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Confidence", gr["confidence_level"])
                    col2.metric("Citations", "✅" if gr["citations_valid"] else "❌")
                    col3.metric("Grounded", "✅" if gr["is_grounded"] else "❌")
                    
                    if gr["warnings"]:
                        st.warning("\n".join(gr["warnings"]))

# Chat input
if prompt := st.chat_input("Ask a question about company policies..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{settings.api_url}/query",
                    json={"question": prompt, "top_k": top_k}
                )
                result = response.json()
                
                st.markdown(result["answer"])
                
                metadata = {
                    "sources": result["sources"],
                    "guardrails": result["guardrails"]
                }
                
                # Sources
                if show_sources and result["sources"]:
                    with st.expander("📚 Sources"):
                        for src in result["sources"]:
                            st.markdown(f"**[{src['id']}]** {src['source']} (score: {src['score']:.2f})")
                
                # Guardrails
                if show_guardrails:
                    gr = result["guardrails"]
                    with st.expander("🛡️ Guardrails"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Confidence", gr["confidence_level"])
                        col2.metric("Citations", "✅" if gr["citations_valid"] else "❌")
                        col3.metric("Grounded", "✅" if gr["is_grounded"] else "❌")
                        
                        if gr["warnings"]:
                            st.warning("\n".join(gr["warnings"]))
                
                # Latency
                st.caption(f"⚡ {result['latency_seconds']:.2f}s | 🎟️ {result['token_usage'].get('total_tokens', 0)} tokens")
                
                # Save to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"],
                    "metadata": metadata
                })
                
            except Exception as e:
                st.error(f"Error: {e}")