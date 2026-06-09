import streamlit as st
import requests
import json
import uuid

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700&display=swap');

.main-header {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FECA57, #FF9FF3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Poppins', sans-serif;
    font-size: 4rem;
    font-weight: 700;
    text-align: center;
    animation: glow 2s ease-in-out infinite alternate;
}

.powered-by {
    text-align: center;
    font-weight: 900;
    background: linear-gradient(45deg, #FF6B35, #F7931E, #FF0080, #7928CA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-family: 'Poppins', sans-serif;
    font-size: 2.5rem;
    margin: 3rem 0;
    animation: pulse 1.5s infinite;
    text-shadow: 0 0 20px rgba(255,107,53,0.6);
}

.vacation-input {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: 3px solid transparent;
    border-radius: 25px;
    padding: 2.5rem;
    margin: 2rem 0;
    box-shadow: 0 15px 40px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.2);
    background-clip: padding-box;
    position: relative;
}

.vacation-input::before {
    content: '';
    position: absolute;
    top: -3px;
    left: -3px;
    right: -3px;
    bottom: -3px;
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4, #FECA57, #FF9FF3);
    border-radius: 25px;
    z-index: -1;
    animation: borderGlow 3s ease-in-out infinite alternate;
}

@keyframes borderGlow {
    0% { opacity: 0.7; transform: scale(1); }
    100% { opacity: 1; transform: scale(1.02); }
}

@keyframes glow {
    from { text-shadow: 0 0 20px rgba(255,107,107,0.5); }
    to { text-shadow: 0 0 30px rgba(78,205,196,0.8); }
}

@keyframes pulse {
    0% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.15); opacity: 1; }
    100% { transform: scale(1); opacity: 0.8; }
}

textarea {
    font-size: 1.1rem !important;
    min-height: 80px !important;
}
</style>
""", unsafe_allow_html=True)

# Generate a valid AgentCore session ID
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4().hex}"

# Initialize destination
if "destination" not in st.session_state:
    st.session_state.destination = ""

# Sidebar
with st.sidebar:
    st.markdown("### 🌎 Menu")

    menu = st.selectbox(
        "Navigation",
        ["Plan Vacation", "About", "Contact"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 👤 Who are you?")

    username = st.text_input(
        "Enter your name to remember your preferences:",
        placeholder="e.g. Dominic"
    )

    if username:
        clean_username = (
            username.lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        if "user_session_id" not in st.session_state:
            st.session_state.user_session_id = (
                f"user_{clean_username}_{uuid.uuid4().hex}"
            )

        st.session_state.session_id = st.session_state.user_session_id

        st.success(
            f"Welcome back, {username}! 🧠 Your travel preferences are remembered."
        )
    else:
        st.caption(
            f"🔑 Temporary session: {st.session_state.session_id[:20]}..."
        )

st.markdown(
    '<h1 class="main-header">✈️ Vacation Planner</h1>',
    unsafe_allow_html=True
)

st.markdown(
    '<p class="powered-by">Powered by Amazon Bedrock AgentCore</p>',
    unsafe_allow_html=True
)

# API endpoint
API_URL = "https://xhslwu8kc4.execute-api.us-west-2.amazonaws.com/prod/vacationplannerappfromscratch"

if menu == "Plan Vacation":

    st.markdown("### 🔥 Popular Destinations")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🗼 Paris", use_container_width=True):
            st.session_state.destination = "Paris"

    with col2:
        if st.button("🗾 Tokyo", use_container_width=True):
            st.session_state.destination = "Tokyo"

    with col3:
        if st.button("🏛️ Rome", use_container_width=True):
            st.session_state.destination = "Rome"

    with col4:
        if st.button("🏖️ Bali", use_container_width=True):
            st.session_state.destination = "Bali"

    st.markdown('<div class="vacation-input">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        destination = st.text_area(
            "🌍 Dream Destination:",
            value=st.session_state.destination,
            placeholder="✨ Bucharest, London, Salzburg, Rome...",
            height=80,
            key="destination_input"
        )

        st.session_state.destination = destination

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 Plan My Dream Vacation", type="primary"):

        if destination:

            with st.spinner("Planning your vacation... ✈️"):

                try:
                    response = requests.post(
                        API_URL,
                        json={
                            "prompt": destination,
                            "session_id": st.session_state.session_id
                        }
                    )

                    if response.status_code == 200:

                        data = response.json()

                        # Recursively unwrap the response until we find a
                        # non-empty string, trying every common key name.
                        TEXT_KEYS = (
                            "result", "response", "output", "message",
                            "text", "content", "answer", "plan", "body"
                        )

                        def extract_text(obj, _depth=0):
                            if _depth > 6:
                                return None
                            if isinstance(obj, str) and obj.strip():
                                return obj.strip()
                            if isinstance(obj, dict):
                                # Try known keys first, in priority order
                                for key in TEXT_KEYS:
                                    if key in obj:
                                        val = obj[key]
                                        # body is often a JSON string
                                        if isinstance(val, str):
                                            try:
                                                val = json.loads(val)
                                            except (json.JSONDecodeError, ValueError):
                                                pass
                                        result = extract_text(val, _depth + 1)
                                        if result:
                                            return result
                                # Fall back: walk every value
                                for val in obj.values():
                                    result = extract_text(val, _depth + 1)
                                    if result:
                                        return result
                            if isinstance(obj, list):
                                for item in obj:
                                    result = extract_text(item, _depth + 1)
                                    if result:
                                        return result
                            return None

                        result_text = extract_text(data)

                        st.success("🎉 Your vacation plan is ready!")
                        st.markdown("## ✈️ Your Personalized Vacation Plan")

                        if result_text:
                            st.markdown(result_text)
                        else:
                            st.error(
                                "We received a response but couldn't read the plan. "
                                "Please try again or contact support."
                            )

                    else:
                        st.error(
                            "Unable to generate your vacation plan. Please try again later."
                        )

                except Exception:
                    st.error(
                        "Something went wrong. Please check your connection and try again."
                    )

        else:
            st.warning("Please enter a destination first. ✈️")

elif menu == "About":

    st.markdown("## 🎆 About Vacation Planner")
    st.write(
        "AI-powered vacation planning using Amazon Bedrock AgentCore."
    )

elif menu == "Contact":

    st.markdown("## 📞 Contact Us")
    st.write("📧 Email: support@vacationplanner.ai")