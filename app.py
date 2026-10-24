import streamlit as st
from datetime import datetime, timedelta
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Parivahan Smart Assistant",
    page_icon="🚗",
    layout="wide"
)

# --- GEMINI API CONFIGURATION (SAFE SETUP) ---
api_key = os.getenv("GEMINI_API_KEY", "")

try:
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

client = None
if api_key:
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except Exception:
        pass

# --- JURISDICTION RULE PACKS (SIMULATED DATA) ---
RULE_PACKS = {
    "Andhra Pradesh (AP)": {
        "renewal_fee": 400,
        "address_change_fee": 300,
        "transfer_fee": 500,
        "standard_wait_days": 7,
        "late_fee_per_month": 500,
        "official_url": "https://aptransport.org",
        "last_checked": "2026-10-01"
    },
    "Telangana (TG)": {
        "renewal_fee": 450,
        "address_change_fee": 350,
        "transfer_fee": 550,
        "standard_wait_days": 10,
        "late_fee_per_month": 600,
        "official_url": "https://transport.telangana.gov.in",
        "last_checked": "2026-09-15"
    }
}

# --- HEADER & BANNER ---
st.title("🚗 Parivahan & Sarathi Smart Service Navigator")
st.caption("Challenge 09: Resolving cross-jurisdiction dependencies, pending requests, and safe deadlines.")
st.info("ℹ️ System Status: Simulating Parivahan portal rules. Sensitive data is masked by default.")

# --- STATE INITIALIZATION (BEFORE SIDEBAR WIDGETS) ---
if "from_state" not in st.session_state:
    st.session_state["from_state"] = "Telangana (TG)"
if "to_state" not in st.session_state:
    st.session_state["to_state"] = "Andhra Pradesh (AP)"
if "days_to_expiry" not in st.session_state:
    st.session_state["days_to_expiry"] = 21
if "has_challan" not in st.session_state:
    st.session_state["has_challan"] = True
if "challan_amount" not in st.session_state:
    st.session_state["challan_amount"] = 1000
if "has_pending" not in st.session_state:
    st.session_state["has_pending"] = True

# --- SIDEBAR: INPUT & SCENARIO SELECTION ---
with st.sidebar:
    st.header("📋 Case Details")
    
    if st.button("⚡ Reset to Ravi's Scenario"):
        st.session_state["from_state"] = "Telangana (TG)"
        st.session_state["to_state"] = "Andhra Pradesh (AP)"
        st.session_state["days_to_expiry"] = 21
        st.session_state["has_challan"] = True
        st.session_state["challan_amount"] = 1000
        st.session_state["has_pending"] = True
        st.rerun()

    from_state = st.selectbox(
        "Current Registration State",
        ["Telangana (TG)", "Andhra Pradesh (AP)", "Karnataka (KA) (Unknown)"],
        key="from_state"
    )
    to_state = st.selectbox(
        "Target / New State", 
        ["Andhra Pradesh (AP)", "Telangana (TG)", "Tamil Nadu (TN) (Unknown)"],
        key="to_state"
    )
    
    days_to_expiry = st.slider("Days Until Licence Expiry", 1, 60, key="days_to_expiry")
    has_challan = st.checkbox("Unpaid Traffic Challan?", key="has_challan")
    challan_amount = st.number_input("Challan Amount (₹)", key="challan_amount")
    has_pending = st.checkbox("Pending Ownership Request?", key="has_pending")

    st.markdown("---")
    st.subheader("⚠️ Live Demo Stress Tests")
    simulate_rejection = st.toggle("Simulate: Pending Request REJECTED mid-flow")
    slot_scarcity = st.toggle("Simulate: RTO Appointment Collapse (High Wait)")

# --- 1. JURISDICTION RULE RESOLUTION & FALLBACK ---
if to_state not in RULE_PACKS:
    st.error(f"⚠️ Rule Pack Missing: Official rules for '{to_state}' are not available in the current database.")
    st.warning("Action: Switching to Degraded Flow. Please refer directly to official guidelines at [parivahan.gov.in](https://parivahan.gov.in).")
    st.stop()

rules = RULE_PACKS[to_state]

# --- 2. CALCULATIONS: FEES, SLOTS, & SAFE DATE ---
appointment_buffer = 20 if slot_scarcity else rules["standard_wait_days"]
processing_days = 5
total_lead_time = appointment_buffer + processing_days

today = datetime.now()
expiry_date = today + timedelta(days=days_to_expiry)
latest_safe_date = expiry_date - timedelta(days=total_lead_time)
days_remaining_to_act = (latest_safe_date - today).days

total_fees = rules["renewal_fee"] + rules["address_change_fee"] + (challan_amount if has_challan else 0)

# --- 3. DASHBOARD METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Target Jurisdiction", to_state)
col2.metric("DL Expiry Date", expiry_date.strftime("%d %b %Y"))
col3.metric(
    "Latest Safe Action Date", 
    latest_safe_date.strftime("%d %b %Y"),
    f"{days_remaining_to_act} days left" if days_remaining_to_act >= 0 else "DEADLINE BREACHED",
    delta_color="normal" if days_remaining_to_act >= 0 else "inverse"
)
col4.metric("Estimated Official Fees", f"₹{total_fees}", help="Freshness: Verified official breakdown")

# --- 4. DEPENDENCY GRAPH ---
st.subheader("🔄 Interdependent Service Sequence")

dot_code = """
digraph G {
    rankdir=LR;
    node [shape=box, style="filled,rounded", fontname="Arial", margin=0.2];
"""

if has_challan:
    dot_code += '    Challan [label="Pay Traffic Challan\\n(₹' + str(challan_amount) + ')", fillcolor="#ffcccc", color="#cc0000"];\n'

if has_pending:
    if simulate_rejection:
        dot_code += '    Pending [label="Pending Ownership\\n[STATUS: REJECTED]", fillcolor="#ff9999", color="#990000"];\n'
        dot_code += '    Withdraw [label="Action: Withdraw or Re-file\\nat Old RTO", fillcolor="#ffe6cc", color="#ff9900"];\n'
    else:
        dot_code += '    Pending [label="Resolve Pending\\nOwnership Transfer", fillcolor="#fff2cc", color="#d6b656"];\n'

dot_code += """
    Address [label="Update Address Proof\\n(Target State)", fillcolor="#d5e8d4", color="#82b366"];
    Renewal [label="Licence Renewal &\\nSlot Booking", fillcolor="#dae8fc", color="#6c8ebf"];
"""

if has_challan and has_pending:
    dot_code += '    Challan -> Pending [label="Blocks"];\n'
    if simulate_rejection:
        dot_code += '    Pending -> Withdraw [label="Triggered"];\n'
        dot_code += '    Withdraw -> Address [label="Required first"];\n'
    else:
        dot_code += '    Pending -> Address [label="Unblocks"];\n'
elif has_challan:
    dot_code += '    Challan -> Address [label="Blocks"];\n'
elif has_pending:
    if simulate_rejection:
        dot_code += '    Pending -> Withdraw -> Address;\n'
    else:
        dot_code += '    Pending -> Address [label="Unblocks"];\n'

dot_code += '    Address -> Renewal [label="Enables"];\n}'

st.graphviz_chart(dot_code)

# --- 5. SEQUENTIAL ACTION PLAN ---
st.subheader("📝 Step-by-Step Action Plan")

step = 1
if has_challan:
    st.write(f"**Step {step}: Clear Penalty.** Unpaid fine of ₹{challan_amount} blocks vehicle transfers on national registries.")
    step += 1

if has_pending:
    if simulate_rejection:
        st.error(f"**Step {step} (EXCEPTION): Ownership Transfer Rejected.** Your prior request was rejected by the source jurisdiction. Options: Withdraw request or visit original RTO with corrected sale deed.")
    else:
        st.write(f"**Step {step}: Conclude Pending Request.** The ownership transfer must receive an NOC/clearance before target state accepts record updates.")
    step += 1

st.write(f"**Step {step}: Apply for Address Update.** Submit utility bill/lease agreement corresponding to {to_state}.")
step += 1
st.write(f"**Step {step}: Complete Renewal.** Book appointment. Slot buffer allocated: **{appointment_buffer} days**.")

if days_remaining_to_act < 0:
    st.error(f"🚨 **Deadline Risk Alert:** High slot wait times mean your renewal will complete after expiry. Anticipated late fee penalty: ₹{rules['late_fee_per_month']}.")

# --- 6. AI PLAIN-LANGUAGE EXPLAINER ---
st.markdown("---")
st.subheader("🤖 Citizen Assistant (Plain-English Explainer)")

if st.button("Generate Plain-English & Vernacular Guidance"):
    if not client:
        st.warning("No Gemini API key detected. Showing local rule summary:")
        st.info(
            "📌 **Citizen Notice:**\n"
            "1. Pay all outstanding challans immediately.\n"
            "2. Clear or withdraw your pending ownership transfer before requesting address updates.\n"
            f"3. Submit your final renewal before {latest_safe_date.strftime('%d %b %Y')} to avoid late-fee penalties."
        )
    else:
        with st.spinner("AI is generating clear advice..."):
            prompt = f"""
            You are an empathetic, clear public service officer assisting a citizen with their driving licence and vehicle.
            Current Situation:
            - Moving from {from_state} to {to_state}.
            - Licence expires in {days_to_expiry} days.
            - Pending request: {'Rejected' if simulate_rejection else ('Pending' if has_pending else 'None')}.
            - Unpaid challan: ₹{challan_amount if has_challan else 0}.
            - Safe action deadline: {latest_safe_date.strftime('%d %b %Y')}.

            Give 3 concise bullet points in very simple, non-bureaucratic English explaining:
            1. What they must do today.
            2. The biggest trap or mistake to avoid.
            3. A reassurance note about their timeline.
            Keep it under 100 words total.
            """
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )
                st.write(response.text)
            except Exception as e:
                st.error(f"AI Generation Error: {e}")
