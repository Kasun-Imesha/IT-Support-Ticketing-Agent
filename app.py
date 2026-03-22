import random
import string
import streamlit as st

from group_chat import user_agent, chat_manager_agent, notification_agent


# Ticket generator
def generate_ticket_id(prefix="TKT", length=6):
    """Generate a random alphanumeric ticket ID."""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}-{suffix}"

# Page config
st.set_page_config(page_title="IT Support AI Assist", page_icon="🤖", layout="centered")

# Load custom CSS
with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Title and subtitle block
st.markdown("""
<div class="title-container">
    <h1>🤖 IT Support AI Assist </h1>
</div>
<div class="subtitle">Your Personalized AI IT Support Assistant</div>
<div class="description"><em>Facing a tech issue? Describe it below and let IT Support AI Assist handle it for you.</em></div>
""", unsafe_allow_html=True)

# Session state setup
if "final_response" not in st.session_state:
    st.session_state.final_response = None
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "awaiting_feedback" not in st.session_state:
    st.session_state.awaiting_feedback = False
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False

# Input section
st.markdown('<div class="input-label">💬 <strong>Describe your IT issue:</strong></div>', unsafe_allow_html=True)
user_input = st.text_area("", value=st.session_state.user_input, height=150)

# Submit logic
if st.button("🚀 Resolve Now") and user_input.strip():
    with st.spinner("IT Support AI Assist is resolving your issue..."):
        st.session_state.user_input = user_input
        responses = []

        original_receive = user_agent.receive

        def receive_and_capture(*args, **kwargs):
            if len(args) >= 2:
                message = args[0]
                if isinstance(message, dict):
                    content = message.get("content", "").replace("TERMINATE", "").strip()
                    if content:
                        responses.append(content)
            return original_receive(*args, **kwargs)

        user_agent.receive = receive_and_capture
        user_agent.initiate_chat(recipient=chat_manager_agent, message=user_input)
        user_agent.receive = original_receive

        if responses:
            final = responses[-1]
            st.session_state.final_response = final
            st.session_state.awaiting_feedback = True
            st.session_state.feedback_given = False
            st.success("✅ **AI Response:**")
            st.markdown(final)
        else:
            st.warning("⚠️ No response received from the agents.")

# Feedback section
if st.session_state.awaiting_feedback and st.session_state.final_response and not st.session_state.feedback_given:
    st.markdown("### 🙋 Was this solution helpful?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, issue resolved"):
            st.session_state.feedback_given = True
            st.session_state.awaiting_feedback = False
            st.success("🎉 Great! We're glad your issue is resolved. Thank you!")

    with col2:
        if st.button("❌ No, not helpful"):
            st.session_state.feedback_given = True
            st.session_state.awaiting_feedback = False
            ticket_id = generate_ticket_id()
            st.warning(f"⚠️ We're escalating this issue to IT support.\n\n📄 **Ticket Created: `{ticket_id}`**")

            # Compose escalation message
            notification_message = (
                f"🚨 Unresolved IT Issue\n\n"
                f"User reported: '{st.session_state.user_input}'\n"
                f"📄 Ticket ID: {ticket_id}"
            )

            reply = notification_agent.generate_reply(
                messages=[{"role": "user", "content": notification_message}],
                sender=user_agent
            )

            final_reply = reply.get("content") if isinstance(reply, dict) else str(reply)
            st.info(f"📨 **Notification Agent Response:**\n\n{final_reply}")