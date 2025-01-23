# app.py

import streamlit as st
from backend.threat_lookup import get_threat_actor_techniques
from backend.ollama_integration import generate_emulation_plan
import logging
import time

# Configure logging
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Streamlit UI
st.title("Adversary Threat Emulation Plan Generator")

# User inputs
actor_name = st.text_input("Enter Threat Actor Name (e.g., APT29)")
desired_impact = st.selectbox(
    "Select Desired Impact", 
    ["Data Exfiltration", "Credential Theft", "System Disruption"]
)

@st.cache_data(show_spinner=True)
def cached_get_threat_actor_techniques(actor_name):
    """ Cached function to fetch threat actor techniques """
    return get_threat_actor_techniques(actor_name)

def format_markdown(actor_name, impact, plan):
    """Format the emulation plan as Markdown."""
    md_content = f"""
# Adversary Threat Emulation Plan

**Threat Actor:** {actor_name}  
**Desired Impact:** {impact}

## Emulation Plan

{plan}

---

*Generated by Adversary Threat Emulation Planner*
    """
    return md_content

def format_html(actor_name, impact, plan):
    """Format the emulation plan as HTML."""
    html_content = (
        "<html>"
        "<head><title>Adversary Emulation Plan</title></head>"
        "<body>"
        "<h1>Adversary Threat Emulation Plan</h1>"
        "<p><strong>Threat Actor:</strong> {}</p>"
        "<p><strong>Desired Impact:</strong> {}</p>"
        "<h2>Emulation Plan</h2>"
        "<p>{}</p>"
        "<hr>"
        "<footer><i>Generated by Adversary Threat Emulation Planner</i></footer>"
        "</body>"
        "</html>"
    ).format(actor_name, impact, plan.replace("\n", "<br>"))
    return html_content


if st.button("Generate Plan"):
    with st.spinner("Generating threat emulation plan..."):
        start_time = time.time()

        # Get techniques (with caching)
        techniques = cached_get_threat_actor_techniques(actor_name)

        if techniques:
            # Generate emulation plan
            plan = generate_emulation_plan(actor_name, desired_impact, techniques)

            # Log success
            logging.info(f"Plan generated for {actor_name} in {time.time() - start_time:.2f}s")

            st.success("Emulation Plan Generated Successfully!")

            # Display generated plan
            st.text_area("Generated Plan", plan, height=400)

            # Prepare content for download
            md_content = format_markdown(actor_name, desired_impact, plan)
            html_content = format_html(actor_name, desired_impact, plan)

            # Download buttons for Markdown and HTML
            st.download_button(
                label="Download as Markdown",
                data=md_content,
                file_name=f"{actor_name}_emulation_plan.md",
                mime="text/markdown"
            )

            st.download_button(
                label="Download as HTML",
                data=html_content,
                file_name=f"{actor_name}_emulation_plan.html",
                mime="text/html"
            )

        else:
            st.error("Failed to generate emulation plan. No techniques found for the specified actor.")
            logging.error(f"No techniques found for threat actor: {actor_name}")
