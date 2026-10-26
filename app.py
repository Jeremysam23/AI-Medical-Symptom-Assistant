import streamlit as st
import subprocess

st.set_page_config(page_title="Medical Symptom Assistant", page_icon="🩺")
st.title("🩺 AI-Powered Medical Symptom Assistant")
st.caption("Educational health information — not a medical diagnosis.")

with st.form("symptom_form"):
    age = st.number_input("Age", min_value=1, max_value=120, value=22)
    symptoms = st.text_area("Describe your symptoms", placeholder="e.g. Fever, cough and sore throat")
    duration = st.text_input("Duration", placeholder="e.g. 2 days")
    severity = st.selectbox("Severity", ["Mild", "Moderate", "Severe"])
    history = st.text_input("Relevant medical conditions, medications or allergies (optional)")
    submitted = st.form_submit_button("Analyze Symptoms")

if submitted:
    if not symptoms.strip() or not duration.strip():
        st.warning("Enter your symptoms and their duration.")
    else:
        prompt = f"""
You are a cautious medical information assistant, not a doctor.
Analyze the information below. Do not claim to diagnose or prescribe.
Clearly communicate uncertainty and never invent patient information.

Age: {age}
Symptoms: {symptoms}
Duration: {duration}
Severity: {severity}
Relevant history, medications or allergies: {history or 'Not provided'}

Use these headings:
1. Reported Symptoms
2. Possible Conditions (possibilities only, not a diagnosis)
3. Why These Were Considered
4. Additional Information / Follow-up Questions
5. General Self-Care Information (only low-risk general advice)
6. Medical Attention (when to seek professional evaluation)
7. Disclaimer

If symptoms suggest an emergency, clearly advise urgent medical care.
Do not delay urgent care by asking follow-up questions.
"""
        with st.spinner("Analyzing symptoms..."):
            try:
                result = subprocess.run(
                    ["ollama", "run", "llama3.2", prompt],
                    capture_output=True, text=True, timeout=300
                )
                if result.returncode == 0 and result.stdout.strip():
                    st.session_state["report"] = result.stdout.strip()
                    st.session_state["patient"] = (
                        f"Age: {age}\nSymptoms: {symptoms}\n"
                        f"Duration: {duration}\nSeverity: {severity}\n"
                        f"History: {history or 'Not provided'}"
                    )
                else:
                    st.error(result.stderr or "Could not generate analysis.")
            except FileNotFoundError:
                st.error("Ollama is not available. Ensure Ollama is installed and running.")
            except subprocess.TimeoutExpired:
                st.error("Timed out. Please try again with shorter symptom details.")

if st.session_state.get("report"):
    st.subheader("Symptom Analysis")
    st.markdown(st.session_state["report"])
    st.download_button(
        "Download Report",
        st.session_state["patient"] + "\n\n" + st.session_state["report"],
        file_name="medical_symptom_report.txt",
        mime="text/plain"
    )

st.warning("For severe breathing difficulty, chest pain, confusion, or other emergency symptoms, seek urgent medical care.")
st.caption("AI-generated information can be inaccurate. Consult a qualified healthcare professional.")
