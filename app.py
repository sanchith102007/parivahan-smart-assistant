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

# --- JURISDICTION RULE PACKS (SIMULATED SAMPLE PACKS) ---
RULE_PACKS = {
    "Andhra Pradesh (AP)": {
        "version": "AP-RTO-2026.2 (Simulated)",
        "renewal_fee": 400,
        "address_change_fee": 300,
        "transfer_fee": 500,
        "rejection_resolution_fee": 200,
        "slot_wait_days": 7,
        "task_durations": {
            "challan_sync": 1,
            "source_noc_clearance": 5,
            "rejection_rectify": 4,
            "address_change": 4,
            "address_recheck": 3,
            "dl_renewal": 2
        },
        "sample_late_fee_estimate": 500,
        "official_url": "https://aptransport.org",
        "last_checked": "01 Oct 2026 (Sample Reference)"
    },
    "Telangana (TG)": {
        "version": "TG-RTO-2026.1 (Simulated)",
        "renewal_fee": 450,
        "address_change_fee": 350,
        "transfer_fee": 550,
        "rejection_resolution_fee": 250,
        "slot_wait_days": 10,
        "task_durations": {
            "challan_sync": 1,
            "source_noc_clearance": 7,
            "rejection_rectify": 5,
            "address_change": 5,
            "address_recheck": 4,
            "dl_renewal": 3
        },
        "sample_late_fee_estimate": 600,
        "official_url": "https://transport.telangana.gov.in",
        "last_checked": "15 Sep 2026 (Sample Reference)"
    }
}

# --- HEADER & DISCLAIMER BANNER ---
st.title("🚗 Vahan Chalak Seva")
st.caption("Challenge 09: Cross-Jurisdiction Dependency Engine, Working Target Scheduler & Exception Handler")
st.info("🔒 **Data Privacy & Simulation Notice:** Identifiers are masked. All portal data, fees, and rules are simulated based on sample rule-packs for prototyping purposes.")

# --- SCENARIO PRESET CALLBACK ---
def apply_scenario_preset():
    choice = st.session_state.get("scenario_choice")
    if choice == "Scenario 1: Ravi's Full Dilemma (Pending + Challan + 21 Days)":
        st.session_state["from_state"] = "Telangana (TG)"
        st.session_state["to_state"] = "Andhra Pradesh (AP)"
        st.session_state["days_to_expiry"] = 21
        st.session_state["has_challan"] = True
        st.session_state["challan_amount"] = 1000
        st.session_state["ownership_status"] = "Pending (Normal Review)"
        st.session_state["slot_scarcity"] = False
        st.session_state["address_invalidated"] = False
    elif choice == "Scenario 2: Normal Clean Cross-State Transfer":
        st.session_state["from_state"] = "Telangana (TG)"
        st.session_state["to_state"] = "Andhra Pradesh (AP)"
        st.session_state["days_to_expiry"] = 40
        st.session_state["has_challan"] = False
        st.session_state["challan_amount"] = 0
        st.session_state["ownership_status"] = "Clear / None"
        st.session_state["slot_scarcity"] = False
        st.session_state["address_invalidated"] = False
    elif choice == "Scenario 3: Mid-Demo Rejection Exception":
        st.session_state["from_state"] = "Telangana (TG)"
        st.session_state["to_state"] = "Andhra Pradesh (AP)"
        st.session_state["days_to_expiry"] = 21
        st.session_state["has_challan"] = True
        st.session_state["challan_amount"] = 1000
        st.session_state["ownership_status"] = "Rejected by Source RTO"
        st.session_state["slot_scarcity"] = False
        st.session_state["address_invalidated"] = False
    elif choice == "Scenario 4: Synthetic Appointment Collapse (Slot Scarcity)":
        st.session_state["from_state"] = "Telangana (TG)"
        st.session_state["to_state"] = "Andhra Pradesh (AP)"
        st.session_state["days_to_expiry"] = 21
        st.session_state["has_challan"] = False
        st.session_state["challan_amount"] = 0
        st.session_state["ownership_status"] = "Clear / None"
        st.session_state["slot_scarcity"] = True
        st.session_state["address_invalidated"] = False
    elif choice == "Scenario 5: Unknown Jurisdiction (Degraded Fallback)":
        st.session_state["from_state"] = "Telangana (TG)"
        st.session_state["to_state"] = "Karnataka (KA) [No Rule Pack]"
        st.session_state["days_to_expiry"] = 30
        st.session_state["has_challan"] = False
        st.session_state["challan_amount"] = 0
        st.session_state["ownership_status"] = "Clear / None"
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
    "ownership_status": "Pending (Normal Review)",
    "slot_scarcity": False,
    "address_invalidated": False
}

for key, default_val in initial_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_val

# --- SIDEBAR ---
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
        ["Telangana (TG)", "Andhra Pradesh (AP)", "Odisha (OD) [No Rule Pack]"],
        key="from_state"
    )
    st.selectbox(
        "Target Jurisdiction",
        ["Andhra Pradesh (AP)", "Telangana (TG)", "Karnataka (KA) [No Rule Pack]"],
        key="to_state"
    )

    st.slider("Days Until DL Expiry", 1, 90, key="days_to_expiry")
    st.checkbox("Unpaid Penalty Item (Challan)", key="has_challan")
    
    # Issue 4 Fix: Minimum value set to 0 and validated
    st.number_input("Challan Amount (₹)", min_value=0, step=100, key="challan_amount")

    # Issue 1 Fix: Explicit, mutually-exclusive ownership states
    st.radio(
        "Vehicle Ownership Transfer Status",
        ["Clear / None", "Pending (Normal Review)", "Rejected by Source RTO"],
        key="ownership_status"
    )

    st.markdown("---")
    st.subheader("⚡ Live Circumstance Triggers")
    st.toggle("Simulate: Target RTO Slot Wait Collapse", key="slot_scarcity")
    st.toggle("Simulate: Invalidate Proof of Address Document", key="address_invalidated")

# Sync working variables
from_state = st.session_state["from_state"]
to_state = st.session_state["to_state"]
days_to_expiry = st.session_state["days_to_expiry"]
has_challan = st.session_state["has_challan"]
raw_challan_amount = st.session_state["challan_amount"]
challan_amount = max(0, int(raw_challan_amount)) if has_challan else 0
ownership_status = st.session_state["ownership_status"]
slot_scarcity = st.session_state["slot_scarcity"]
address_invalidated = st.session_state["address_invalidated"]

# --- JURISDICTION PACK CHECKS ---
missing_states = []
if from_state not in RULE_PACKS:
    missing_states.append(f"Source: {from_state}")
if to_state not in RULE_PACKS:
    missing_states.append(f"Target: {to_state}")

if missing_states:
    st.error(f"🛑 **Jurisdiction Unknown:** Missing verified sample rule pack for: {', '.join(missing_states)}.")
    st.warning("⚠️ **Degraded Execution Mode Activated:** To avoid guessing statutory rules, cross-jurisdiction scheduling is suspended.")
    st.markdown("""
    ### Official Recourse Guidance:
    * **Step 1:** Visit the central portal: [Parivahan Sewa](https://parivahan.gov.in).
    * **Step 2:** Check individual State Citizen Charters under **Online Services > Vehicle / Licence Services**.
    * **Step 3:** Source RTO must grant Form 28 NOC before the Target RTO can process registration.
    """)
    st.stop()

source_rules = RULE_PACKS[from_state]
target_rules = RULE_PACKS[to_state]

# --- DYNAMIC TASK CONSTRUCTION ---
today = datetime.now()
expiry_date = today + timedelta(days=days_to_expiry)
target_slot_wait = 24 if slot_scarcity else target_rules["slot_wait_days"]

tasks = []

# Task 1: Challan clearing
if has_challan and challan_amount > 0:
    tasks.append({
        "id": "challan",
        "name": f"Clear Unpaid Challan ({from_state})",
        "governing_jurisdiction": from_state,
        "duration": source_rules["task_durations"]["challan_sync"],
        "cost": challan_amount,
        "fee_category": "Pending Challan / Penalty",
        "reason": f"Source jurisdiction ({from_state}) national registry lock blocks Form 28 NOC issuance until cleared.",
        "type": "Penalty Clearance"
    })

# Task 2: Ownership handling
if ownership_status == "Rejected by Source RTO":
    tasks.append({
        "id": "rejection_appeal",
        "name": f"Resolve Rejection & Resubmit Form 29/30 ({from_state})",
        "governing_jurisdiction": from_state,
        "duration": source_rules["task_durations"]["source_noc_clearance"] + source_rules["task_durations"]["rejection_rectify"],
        "cost": source_rules["rejection_resolution_fee"],
        "fee_category": "Simulated Rejection Rectification Fee",
        "reason": f"Source RTO ({from_state}) flagged signature/documentation discrepancy on Form 29/30 transfer. Requires manual objection rectification before Form 28 NOC can issue.",
        "type": "Simulated Rejection-Resolution Step"
    })
elif ownership_status == "Pending (Normal Review)":
    tasks.append({
        "id": "pending",
        "name": f"Conclude Form 28 NOC & Transfer ({from_state})",
        "governing_jurisdiction": from_state,
        "duration": source_rules["task_durations"]["source_noc_clearance"],
        "cost": source_rules["transfer_fee"],
        "fee_category": "Source State Ownership / NOC Fee",
        "reason": f"RC record is held by source jurisdiction ({from_state}) pending ownership transfer verification and inter-state clearance.",
        "type": "Source Jurisdiction Prerequisite"
    })

# Task 3: Address update
# Issue 3 Fix: Dynamic days derived from target_rules['task_durations']['address_recheck']
recheck_days = target_rules["task_durations"]["address_recheck"]
addr_duration = target_rules["task_durations"]["address_change"]

if address_invalidated:
    addr_duration += recheck_days
    addr_reason = f"⚠️ DOCUMENT FAILED: Original Proof of Address for {to_state} rejected. Re-submitting local residence proof adds a {recheck_days}-day verification buffer."
else:
    addr_reason = f"Target jurisdiction ({to_state}) requires local residency verification before accepting DL renewal filings."

tasks.append({
    "id": "address",
    "name": f"Update Address Records ({to_state})",
    "governing_jurisdiction": to_state,
    "duration": addr_duration,
    "cost": target_rules["address_change_fee"],
    "fee_category": "Target State Address Update Fee",
    "reason": addr_reason,
    "type": "Target Jurisdiction Prerequisite"
})

# Task 4: DL Renewal & Biometric Slot
tasks.append({
    "id": "renewal",
    "name": f"Book Biometric Slot & DL Renewal ({to_state})",
    "governing_jurisdiction": to_state,
    "duration": target_rules["task_durations"]["dl_renewal"] + target_slot_wait,
    "cost": target_rules["renewal_fee"],
    "fee_category": "Target State DL Renewal Fee",
    "reason": f"Final renewal application subject to {to_state} appointment slot queue ({target_slot_wait}-day buffer).",
    "type": "Final Milestone"
})

# --- BACKWARD WORKING-TARGET SCHEDULING ---
current_target = expiry_date
scheduled_tasks = []

for t in reversed(tasks):
    calculated_safe_date = current_target - timedelta(days=t["duration"])
    raw_days_left = (calculated_safe_date - today).days

    is_breached = raw_days_left < 0
    display_target_date = calculated_safe_date if not is_breached else (today + timedelta(days=1))

    scheduled_tasks.append({
        **t,
        "calculated_safe_date": calculated_safe_date,
        "display_target_date": display_target_date,
        "raw_days_left": raw_days_left,
        "is_breached": is_breached,
        "deadline_for_next": current_target
    })
    current_target = calculated_safe_date

scheduled_tasks.reverse()

first_task = scheduled_tasks[0]
days_to_first_target = first_task["raw_days_left"]
overall_target_breached = any(t["is_breached"] for t in scheduled_tasks)
total_statutory_fees = sum(t["cost"] for t in scheduled_tasks)

# --- DASHBOARD METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Route", f"{from_state.split()[0]} ➔ {to_state.split()[0]}")
col2.metric("DL Expiry Date", expiry_date.strftime("%d %b %Y"))

if not overall_target_breached:
    col3.metric(
        "Earliest Action Target",
        first_task["display_target_date"].strftime("%d %b %Y"),
        f"{days_to_first_target} days remaining",
        delta_color="normal"
    )
else:
    col3.metric(
        "Earliest Action Target",
        "IMMEDIATE (Risk)",
        f"{abs(days_to_first_target)}d past safe buffer",
        delta_color="inverse"
    )

col4.metric(
    "Total Simulated Fees",
    f"₹{total_statutory_fees}",
    help="Breakdown shown in the Cost Transparency section below."
)

st.info("⚠️ **Scheduling Advisory:** Dates are estimated working targets, not statutory deadlines. They represent the practical operational milestones required to complete interdependent clearances prior to license expiry.")

# Rejection & Invalidation alerts
if ownership_status == "Rejected by Source RTO":
    st.error(
        f"⚠️ **Mid-Flow Exception Detected: Ownership Transfer Rejected at {from_state}.** "
        f"The system has inserted a **Simulated Rejection-Resolution Step** using {from_state} rule packs (+{source_rules['task_durations']['rejection_rectify']} days buffer). "
        "Form 29/30 notice and objection response must be filed at the source RTO."
    )

# Issue 5 Fix: Clarify full backward shift of earlier tasks
if address_invalidated:
    st.warning(
        f"📄 **Document Invalidation Alert:** Address proof rejected under {to_state} criteria (+{recheck_days} days). "
        "Because deadlines are scheduled backward from expiry, this added buffer also shifts earlier prerequisite targets forward."
    )

# --- TRANSPARENT FEE BREAKDOWN ---
st.markdown("---")
st.subheader("💰 Transparent Fee Breakdown")
st.caption("ℹ️ Fees are simulated based on sample rule-packs from source and target jurisdictions.")

fee_cols = st.columns(len(scheduled_tasks) + 1)
for i, t in enumerate(scheduled_tasks):
    with fee_cols[i]:
        st.markdown(f"**{t['fee_category']}**")
        st.markdown(f"₹{t['cost']}")
        st.caption(f"Rule: {t['governing_jurisdiction']}")

# Issue 2 Fix: Accurately labeled total
with fee_cols[-1]:
    st.markdown("**Total Simulated Cost Estimate**")
    st.markdown(f"**₹{total_statutory_fees}**")
    st.caption("Combined simulated estimate")

# --- DEPENDENCY GRAPH WITH DYNAMIC STEP NUMBERING (ISSUE 6 FIX) ---
st.markdown("---")
st.subheader("🔄 Cross-Jurisdiction Dependency Flowchart")

dot_code = """
digraph G {
    rankdir=LR;
    node [shape=box, style="filled,rounded", fontname="Arial", margin=0.2];
"""

# Dynamically assign node labels based on actual task position in scheduled_tasks
for step_num, task in enumerate(scheduled_tasks, start=1):
    t_id = task["id"]
    if t_id == "challan":
        dot_code += f'    challan [label="{step_num}. Pay Traffic Challan\\n({from_state})\\n[₹{challan_amount}]", fillcolor="#ffcccc", color="#cc0000"];\n'
    elif t_id == "rejection_appeal":
        dot_code += f'    rejection_appeal [label="{step_num}. Form 29/30 Rectification\\n({from_state})\\n[SIMULATED RECOVERY]", fillcolor="#ffe6cc", color="#d76b00"];\n'
    elif t_id == "pending":
        dot_code += f'    pending [label="{step_num}. Form 28 NOC & Transfer\\n({from_state})", fillcolor="#fff2cc", color="#b58900"];\n'
    elif t_id == "address":
        addr_label = f"{step_num}. Address Update\\n({to_state})\\n[DOC RE-VERIFICATION]" if address_invalidated else f"{step_num}. Address Update\\n({to_state})"
        addr_fill = "#ffeedd" if address_invalidated else "#d5e8d4"
        addr_border = "#e67e22" if address_invalidated else "#2e7d32"
        dot_code += f'    address [label="{addr_label}", fillcolor="{addr_fill}", color="{addr_border}"];\n'
    elif t_id == "renewal":
        dot_code += f'    renewal [label="{step_num}. Biometric Slot & DL Renewal\\n({to_state})", fillcolor="#dae8fc", color="#1565c0"];\n'

# Dynamically link consecutive tasks in the schedule
for i in range(len(scheduled_tasks) - 1):
    curr_id = scheduled_tasks[i]["id"]
    next_id = scheduled_tasks[i + 1]["id"]
    
    if curr_id == "challan":
        edge_label = "Registry lock"
    elif curr_id in ["rejection_appeal", "pending"]:
        edge_label = "Enables inter-state NOC"
    elif curr_id == "address":
        edge_label = "Validates residency"
    else:
        edge_label = "Proceeds to"
        
    dot_code += f'    {curr_id} -> {next_id} [label="{edge_label}"];\n'

dot_code += "}"
st.graphviz_chart(dot_code)

# --- PER-TASK SCHEDULE ---
st.markdown("---")
st.subheader("📅 Task-by-Task Safe Working Targets")

task_cols = st.columns(len(scheduled_tasks))
for idx, (c, t) in enumerate(zip(task_cols, scheduled_tasks), start=1):
    with c:
        status_icon = "🟢" if not t["is_breached"] else "🔴"
        st.markdown(f"**{status_icon} Step {idx}: {t['name']}**")
        st.markdown(f"*Rule Base:* `{t['governing_jurisdiction']}`")
        st.markdown(f"*Est. Duration:* **{t['duration']} day(s)**")
        
        if not t["is_breached"]:
            st.markdown(f"*Target Date:* **{t['display_target_date'].strftime('%d %b %Y')}**")
            st.markdown(f"*Buffer:* `{t['raw_days_left']} day(s) left`")
        else:
            st.markdown(f"*Working Target:* **IMMEDIATE**")
            st.caption(f"Calculated safe date ({t['calculated_safe_date'].strftime('%d %b')}) passed.")

        st.info(f"**Why blocked here:** {t['reason']}")

if overall_target_breached:
    sample_late_fee = target_rules["sample_late_fee_estimate"]
    st.error(
        f"🚨 **Simulated Late-Fee Risk Warning:** Your total sequential processing lead time exceeds the days remaining before license expiry. "
        f"If the application is filed after {expiry_date.strftime('%d %b %Y')}, a statutory late renewal penalty may apply under {to_state} rules (simulated rule estimate: ~₹{sample_late_fee}/month). "
        "Note: Missing an operational working target reduces buffer time, but statutory penalties apply only if the renewal completes past statutory deadlines and applicable grace periods."
    )

# --- LOCAL RULE GUIDANCE GENERATOR ---
def generate_local_rule_guidance():
    guidance_items = []

    if has_challan and challan_amount > 0:
        guidance_items.append(f"**Immediate Action 1:** Clear outstanding traffic challan (₹{challan_amount}) on the {from_state} portal to remove the national registry lock.")
    
    if ownership_status == "Rejected by Source RTO":
        guidance_items.append(f"**Immediate Action 2:** Address the transfer objection at {from_state} RTO. Rectify Form 29/30 documentation to re-enable Form 28 NOC processing.")
    elif ownership_status == "Pending (Normal Review)":
        guidance_items.append(f"**Immediate Action 2:** Monitor Form 28 NOC issuance from {from_state} RTO before filing records in {to_state}.")
    else:
        guidance_items.append(f"**Immediate Action:** Prepare your local residence proof and file for address modification directly on the {to_state} portal.")

    if address_invalidated:
        trap = f"Your proof of address was rejected by {to_state}. Upload a verified domicile certificate or utility bill in your name to avoid renewed delays."
    elif slot_scarcity:
        trap = f"{to_state} RTO appointment wait is currently elevated ({target_slot_wait} days). Secure your booking slot immediately after address approval."
    else:
        trap = f"Do not attempt to renew your DL in {to_state} before completing prior transfer clearances in {from_state}."

    timeline_note = (
        "You have breached safe operational working buffers. Prioritize Step 1 today to avoid expiring during the RTO appointment queue."
        if overall_target_breached else
        f"You are currently within safe operational targets if initial tasks begin by {first_task['display_target_date'].strftime('%d %b %Y')}."
    )

    return f"""
    * {guidance_items[0]}
    * **Primary Mistake to Avoid:** {trap}
    * **Timeline Assessment:** {timeline_note}
    * **గమనిక (Telugu Summary):** మీ చలాన్లు మరియు అభ్యంతరాలను త్వరగా పరిష్కరించుకుని, గడువు ముగియకముందే స్లాట్ బుక్ చేసుకోండి.
    """

# --- AI PLAIN-LANGUAGE EXPLAINER ---
st.markdown("---")
st.subheader("🤖 Citizen Assistant (Plain-English & Vernacular Guidance)")

if st.button("Generate Plain-English & Vernacular Guidance"):
    ai_success = False
    
    if client:
        with st.spinner("AI is generating clear citizen guidance..."):
            status_desc = (
                "Form 29/30 REJECTED by source RTO (Rectification required)"
                if ownership_status == "Rejected by Source RTO"
                else ("Form 28 NOC pending at source RTO" if ownership_status == "Pending (Normal Review)" else "Clear")
            )
            prompt = f"""
            You are a helpful, empathetic public transport officer assisting an Indian citizen navigating cross-jurisdiction vehicle and driving licence services.
            Case Context:
            - Moving from {from_state} to {to_state}.
            - Licence expires on {expiry_date.strftime('%d %b %Y')} ({days_to_expiry} days away).
            - Unpaid challan: ₹{challan_amount}.
            - Vehicle Transfer Status: {status_desc}.
            - Address Document Status: {'Rejected/Re-verifying' if address_invalidated else 'Valid'}.
            - Earliest action target: {first_task['display_target_date'].strftime('%d %b %Y')}.
            - Slot waiting buffer in {to_state}: {target_slot_wait} days.
            - Status: {'BREACHED OPERATIONAL BUFFER - URGENT ACTION NEEDED' if overall_target_breached else 'ON TRACK'}.

            Provide 3 structured bullet points in plain, reassuring English:
            1. What exact action they must take today (reference only conditions that are true).
            2. The single biggest procedural mistake to avoid.
            3. A realistic timeline assessment.
            Add one short summary sentence in Telugu or Hindi for vernacular accessibility.
            Keep the entire response under 120 words.
            """
            try:
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )
                if response and response.text:
                    st.write(response.text)
                    ai_success = True
            except Exception as e:
                st.warning(f"Live AI assistant service unavailable ({e}). Running deterministic local rule engine:")

    if not ai_success:
        st.markdown(generate_local_rule_guidance())
