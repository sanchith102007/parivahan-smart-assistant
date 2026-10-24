import streamlit as st
from datetime import datetime, timedelta
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Vahan Chalak Seva",
    page_icon="🚗",
    layout="wide"
)

# --- GEMINI API CONFIGURATION ---
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

# --- JURISDICTION RULE PACKS (VERSIONED & SOURCED) ---
RULE_PACKS = {
    "Andhra Pradesh (AP)": {
        "version": "AP-RTO-2026.2",
        "renewal_fee": 400,
        "address_change_fee": 300,
        "transfer_fee": 500,
        "slot_wait_days": 7,
        "task_durations": {
            "challan": 1,
            "pending_req": 5,
            "address_change": 4,
            "renewal": 2
        },
        "late_fee_per_month": 500,
        "official_url": "https://aptransport.org",
        "last_checked": "01 Oct 2026"
    },
    "Telangana (TG)": {
        "version": "TG-RTO-2026.1",
        "renewal_fee": 450,
        "address_change_fee": 350,
        "transfer_fee": 550,
        "slot_wait_days": 10,
        "task_durations": {
            "challan": 1,
            "pending_req": 7,
            "address_change": 5,
            "renewal": 3
        },
        "late_fee_per_month": 600,
        "official_url": "https://transport.telangana.gov.in",
        "last_checked": "15 Sep 2026"
    }
}

# --- HEADER & BANNER ---
st.title("🚗 Vahan Chalak Seva")
st.caption("Challenge 09: Cross-Jurisdiction Dependency Engine, Safe-Date Calculator & Exception Handler")
st.info("🔒 **Data Privacy & Simulation Notice:** Identifiers are masked by default. Portal data is simulated. Official rule sources and estimate freshness labels are displayed for compliance.")

# --- SCENARIO PRESET CALLBACK FUNCTION ---
def apply_scenario_preset():
    choice = st.session_state.get("scenario_choice")
    if choice == "Scenario 1: Ravi's Full Dilemma (Pending + Challan + 21 Days)":
        st.session_state["from_state"] = "Telangana (TG)"
        st.session_state["to_state"] = "Andhra Pradesh (AP)"
        st.session_state["days_to_expiry"] = 21
        st.session_state["has_challan"] = True
        st.session_state["challan_amount"] = 1000
        st.session_state["has_pending"] = True
        st.session_state["simulate_rejection"] = False
        st.session_state["slot_scarcity"] = False
        st.session_state["address_invalidated"] = False
    elif choice == "Scenario 2: Normal Clean Cross-State Transfer":
        st.session_state["from_state"] = "Telangana (TG)"
        st.session_state["to_state"] = "Andhra Pradesh (AP)"
        st.session_state["days_to_expiry"] = 40
        st.session_state["has_challan"] = False
        st.session_state["challan_amount"] = 0
        st.session_state["has_pending"] = False
        st.session_state["simulate_rejection"] = False
        st.session_state["slot_scarcity"] = False
        st.session_state["address_invalidated"] = False
    elif choice == "Scenario 3: Mid-Demo Rejection Exception":
        st.session_state["from_state"] = "Telangana (TG)"
        st.session_state["to_state"] = "Andhra Pradesh (AP)"
        st.session_state["days_to_expiry"] = 21
        st.session_state["has_challan"] = True
        st.session_state["challan_amount"] = 1000
        st.session_state["has_pending"] = True
        st.session_state["simulate_rejection"] = True
        st.session_state["slot_scarcity"] = False
        st.session_state["address_invalidated"] = False
    elif choice == "Scenario 4: Synthetic Appointment Collapse (Slot Scarcity)":
        st.session_state["from_state"] = "Telangana (TG)"
        st.session_state["to_state"] = "Andhra Pradesh (AP)"
        st.session_state["days_to_expiry"] = 21
        st.session_state["has_challan"] = False
        st.session_state["challan_amount"] = 0
        st.session_state["has_pending"] = False
        st.session_state["simulate_rejection"] = False
        st.session_state["slot_scarcity"] = True
        st.session_state["address_invalidated"] = False
    elif choice == "Scenario 5: Unknown Jurisdiction (Degraded Fallback)":
        st.session_state["from_state"] = "Telangana (TG)"
        st.session_state["to_state"] = "Karnataka (KA) [No Rule Pack]"
        st.session_state["days_to_expiry"] = 30
        st.session_state["has_challan"] = False
        st.session_state["challan_amount"] = 0
        st.session_state["has_pending"] = False
        st.session_state["simulate_rejection"] = False
        st.session_state["slot_scarcity"] = False
        st.session_state["address_invalidated"] = False

# --- STATE INITIALIZATION ---
initial_defaults = {
    "scenario_choice": "Scenario 1: Ravi's Full Dilemma (Pending + Challan + 21 Days)",
    "from_state": "Telangana (TG)",
    "to_state": "Andhra Pradesh (AP)",
    "days_to_expiry": 21,
    "has_challan": True,
    "challan_amount": 1000,
    "has_pending": True,
    "simulate_rejection": False,
    "slot_scarcity": False,
    "address_invalidated": False
}

for key, default_val in initial_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_val

# --- SIDEBAR: INPUT & SCENARIO SELECTION ---
with st.sidebar:
    st.header("🧪 Test Scenarios")
    st.selectbox(
        "Select Test Scenario",
        [
            "Scenario 1: Ravi's Full Dilemma (Pending + Challan + 21 Days)",
            "Scenario 2: Normal Clean Cross-State Transfer",
            "Scenario 3: Mid-Demo Rejection Exception",
            "Scenario 4: Synthetic Appointment Collapse (Slot Scarcity)",
            "Scenario 5: Unknown Jurisdiction (Degraded Fallback)",
            "Custom Setup"
        ],
        key="scenario_choice",
        on_change=apply_scenario_preset
    )

    st.markdown("---")
    st.header("📋 Case Parameters")
    
    st.selectbox(
        "Source Jurisdiction",
        ["Telangana (TG)", "Andhra Pradesh (AP)"],
        key="from_state"
    )
    st.selectbox(
        "Target Jurisdiction",
        ["Andhra Pradesh (AP)", "Telangana (TG)", "Karnataka (KA) [No Rule Pack]"],
        key="to_state"
    )

    st.slider("Days Until DL Expiry", 1, 90, key="days_to_expiry")
    st.checkbox("Unpaid Penalty Item (Challan)", key="has_challan")
    st.number_input("Challan Amount (₹)", key="challan_amount")
    st.checkbox("Pending Ownership Request Active", key="has_pending")

    st.markdown("---")
    st.subheader("⚡ Live Circumstance Triggers")
    st.toggle("Ownership Request REJECTED", key="simulate_rejection")
    st.toggle("Appointment Availability Collapsed", key="slot_scarcity")
    st.toggle("Address Proof Invalidated by Cross-Update", key="address_invalidated")

# Pull active variables from session state
from_state = st.session_state["from_state"]
to_state = st.session_state["to_state"]
days_to_expiry = st.session_state["days_to_expiry"]
has_challan = st.session_state["has_challan"]
challan_amount = st.session_state["challan_amount"]
has_pending = st.session_state["has_pending"]
simulate_rejection = st.session_state["simulate_rejection"]
slot_scarcity = st.session_state["slot_scarcity"]
address_invalidated = st.session_state["address_invalidated"]

# --- UNKNOWN JURISDICTION FALLBACK ---
if to_state not in RULE_PACKS:
    st.error(f"🛑 **Jurisdiction Unknown:** No verified rule pack found for '{to_state}'.")
    st.warning("⚠️ **Degraded Execution Mode Activated:** To avoid guessing statutory fees or deadlines, automated scheduling is suspended.")
    
    st.markdown("""
    ### Official Recourse Guidance:
    * **Step 1:** Visit the official central portal: [Parivahan Sewa (National Portal)](https://parivahan.gov.in).
    * **Step 2:** Check State-Specific Citizen Charters under **Online Services > Driving Licence Related Services**.
    * **Step 3:** Contact the regional RTO Helpdesk before filing conflicting address modifications.
    """)
    st.stop()

rules = RULE_PACKS[to_state]

# --- DYNAMIC RECALCULATION & TASK-BY-TASK SAFE DATES ---
today = datetime.now()
expiry_date = today + timedelta(days=days_to_expiry)

appointment_wait = 24 if slot_scarcity else rules["slot_wait_days"]

tasks = []
if has_challan:
    tasks.append({
        "id": "challan",
        "name": "Clear Unpaid Challan",
        "duration": rules["task_durations"]["challan"],
        "reason": "Vahan national portal restricts NOC and transfer requests when an active challan is pending.",
        "cost": challan_amount,
        "type": "Penalty"
    })

if has_pending:
    if simulate_rejection:
        tasks.append({
            "id": "pending_reject",
            "name": "Withdraw / Re-file Rejected Ownership",
            "duration": rules["task_durations"]["pending_req"] + 3,
            "reason": "Previous transfer was rejected by source RTO. Must be formally withdrawn or updated with valid sale deed before new applications.",
            "cost": 100,
            "type": "Resolution"
        })
    else:
        tasks.append({
            "id": "pending",
            "name": "Resolve & Clear Ownership Transfer",
            "duration": rules["task_durations"]["pending_req"],
            "reason": "RC records are locked by source RTO until ownership transfer achieves final clearance.",
            "cost": rules["transfer_fee"],
            "type": "Statutory"
        })

tasks.append({
    "id": "address",
    "name": "Update Address on Records",
    "duration": rules["task_durations"]["address_change"] + (3 if address_invalidated else 0),
    "reason": "Address proof must be recognized in target jurisdiction before renewal application can be filed." + (" [RE-VERIFICATION REQUIRED: Prior proof invalidated]" if address_invalidated else ""),
    "cost": rules["address_change_fee"],
    "type": "Prerequisite"
})

tasks.append({
    "id": "renewal",
    "name": "Book Slot & Submit DL Renewal",
    "duration": rules["task_durations"]["renewal"] + appointment_wait,
    "reason": "Final renewal action subject to biometric appointment slot wait buffer.",
    "cost": rules["renewal_fee"],
    "type": "Final Goal"
})

current_deadline = expiry_date
scheduled_tasks = []

for t in reversed(tasks):
    task_latest_safe = current_deadline - timedelta(days=t["duration"])
    days_left_for_task = (task_latest_safe - today).days
    
    scheduled_tasks.append({
        **t,
        "latest_safe_date": task_latest_safe,
        "days_left": days_left_for_task,
        "deadline_for_next": current_deadline
    })
    current_deadline = task_latest_safe

scheduled_tasks.reverse()

first_task_safe_date = scheduled_tasks[0]["latest_safe_date"]
days_to_first_deadline = (first_task_safe_date - today).days
total_statutory_fees = sum(t["cost"] for t in scheduled_tasks)

# --- DASHBOARD METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Target Jurisdiction", to_state, help=f"Rule Pack: {rules['version']}")
col2.metric("DL Expiry Date", expiry_date.strftime("%d %b %Y"))
col3.metric(
    "First Action Safe Date",
    first_task_safe_date.strftime("%d %b %Y"),
    f"{days_to_first_deadline} days remaining" if days_to_first_deadline >= 0 else "DEADLINE BREACHED",
    delta_color="normal" if days_to_first_deadline >= 0 else "inverse"
)
col4.metric(
    "Total Fees [ESTIMATE]",
    f"₹{total_statutory_fees}",
    help=f"Includes challans + RTO fees. Official verified date: {rules['last_checked']}"
)

# --- SOURCE AND FRESHNESS LABELS ---
st.caption(
    f"📋 **Rule Pack Metadata:** Verified Version: `{rules['version']}` | "
    f"Official Portal: [{rules['official_url']}]({rules['official_url']}) | "
    f"Last Checked: `{rules['last_checked']}` | "
    f"Slot Buffer: `{appointment_wait} days`"
)

# --- DEPENDENCY GRAPH ---
st.markdown("---")
st.subheader("🔄 Dynamic Dependency Flowchart")

dot_code = """
digraph G {
    rankdir=LR;
    node [shape=box, style="filled,rounded", fontname="Arial", margin=0.2];
"""

if has_challan:
    dot_code += f'    challan [label="1. Pay Traffic Challan\\n(₹{challan_amount})\\n[Deadline: {scheduled_tasks[0]["latest_safe_date"].strftime("%d %b")}]", fillcolor="#ffcccc", color="#cc0000"];\n'

if has_pending:
    if simulate_rejection:
        dot_code += '    pending_reject [label="2. Withdraw / Re-file\\nOwnership Transfer\\n[STATUS: REJECTED]", fillcolor="#ffe6cc", color="#d76b00"];\n'
    else:
        dot_code += '    pending [label="2. Clear Ownership Transfer\\n(Pending at Old RTO)", fillcolor="#fff2cc", color="#b58900"];\n'

dot_code += f"""
    address [label="3. Update Address Proof\\n(Target: {to_state})", fillcolor="#d5e8d4", color="#2e7d32"];
    renewal [label="4. Biometric Slot &\\nDL Renewal", fillcolor="#dae8fc", color="#1565c0"];
"""

if has_challan and has_pending:
    target_pending = "pending_reject" if simulate_rejection else "pending"
    dot_code += f'    challan -> {target_pending} [label="Locks registry"];\n'
    dot_code += f'    {target_pending} -> address [label="Must clear prior RC"];\n'
elif has_challan:
    dot_code += '    challan -> address [label="Locks registry"];\n'
elif has_pending:
    target_pending = "pending_reject" if simulate_rejection else "pending"
    dot_code += f'    {target_pending} -> address [label="Must clear prior RC"];\n'

dot_code += '    address -> renewal [label="Validates local residency"];\n}'

st.graphviz_chart(dot_code)

# --- PER-TASK SCHEDULE ---
st.markdown("---")
st.subheader("📅 Task-by-Task Safe Deadline Schedule")
st.write("Each task is scheduled backward from the expiry date to guarantee your renewal completes before statutory grace periods expire.")

task_cols = st.columns(len(scheduled_tasks))
for idx, (c, t) in enumerate(zip(task_cols, scheduled_tasks), start=1):
    with c:
        status_color = "🟢" if t["days_left"] >= 0 else "🔴"
        st.markdown(f"**{status_color} Step {idx}: {t['name']}**")
        st.markdown(f"*Type:* `{t['type']}`")
        st.markdown(f"*Est. Duration:* **{t['duration']} day(s)**")
        st.markdown(f"*Latest Safe Date:* **{t['latest_safe_date'].strftime('%d %b %Y')}**")
        st.markdown(f"*Days Left to Act:* `{t['days_left']} day(s)`")
        st.info(f"**Why blocked here:** {t['reason']}")

if days_to_first_deadline < 0:
    late_fee_est = rules["late_fee_per_month"]
    st.error(
        f"🚨 **Critical Deadline Breach:** Prerequisite steps will breach the renewal window. "
        f"Anticipated statutory penalty under {to_state} rules: **₹{late_fee_est} per month delayed**."
    )

# --- AI PLAIN-LANGUAGE EXPLAINER ---
st.markdown("---")
st.subheader("🤖 Citizen Assistant (Plain-English & Vernacular Guidance)")

if st.button("Generate Plain-English & Vernacular Guidance"):
    if not client:
        st.warning("No Gemini API key detected. Showing local automated brief:")
        st.markdown(f"""
        * **Immediate Action:** Pay your pending challan and resolve your stuck transfer by **{scheduled_tasks[0]['latest_safe_date'].strftime('%d %b %Y')}**.
        * **Critical Risk:** RTO appointment slots take **{appointment_wait} days**. Do not wait until the expiry date to begin.
        * **Official Source:** Review requirements at [{rules['official_url']}]({rules['official_url']}).
        """)
    else:
        with st.spinner("AI is generating clear citizen guidance..."):
            prompt = f"""
            You are a helpful, empathetic public transport officer assisting a citizen with an urgent driving licence and vehicle situation.
            Case Details:
            - Moving from {from_state} to {to_state}.
            - Licence expires on {expiry_date.strftime('%d %b %Y')} ({days_to_expiry} days away).
            - Unpaid penalty: ₹{challan_amount if has_challan else 0}.
            - Transfer status: {'REJECTED - action needed' if simulate_rejection else ('Pending at source RTO' if has_pending else 'Clear')}.
            - First critical task: {scheduled_tasks[0]['name']} must be initiated by {first_task_safe_date.strftime('%d %b %Y')}.
            - Slot waiting time: {appointment_wait} days.

            Provide 3 structured bullet points in plain, reassuring English (and add one short summary line in Telugu/Hindi for vernacular accessibility):
            1. What exact action they must take today.
            2. The single biggest mistake that will cause rejection.
            3. A timeline summary explaining whether they are currently on track.
            Keep the entire response under 120 words.
            """
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )
                st.write(response.text)
            except Exception as e:
                st.error(f"AI Generation Error: {e}")
