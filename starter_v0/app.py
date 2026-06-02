import streamlit as st
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import subprocess

# Set up page config
st.set_page_config(
    page_title="🕵️‍♂️ Research Agent Explorer",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for rich, premium aesthetics
st.markdown("""
<style>
    .main {
        background-color: #0f1116;
        color: #ffffff !important;
    }
    .stApp {
        background-color: #0f1116;
    }
    /* Force 100% solid opacity and pure white for targeted document text tags only */
    div.stMarkdown p, 
    div.stMarkdown li, 
    div.stMarkdown span,
    div.stMarkdown label,
    .main p, 
    .main li {
        color: #ffffff !important;
        opacity: 1.0 !important; /* Maximized solid opacity */
        text-rendering: optimizeLegibility !important;
        -webkit-font-smoothing: antialiased !important;
    }
    
    /* 🛠️ Sidebar Premium Styling & Text Contrast */
    [data-testid="stSidebar"] {
        background-color: #0b0f19 !important; /* Dark rich charcoal sidebar */
        border-right: 1px solid #1e293b !important;
    }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        opacity: 1.0 !important;
    }
    [data-testid="stSidebar"] label p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Let Streamlit's native dark-mode style selectboxes, dropdown portals, and input text */
    /* This completely prevents React portal dropdown list items from having white-on-white collisions! */
    h1, h2, h3 {
        color: #38bdf8 !important;
        font-family: 'Outfit', 'Inter', sans-serif;
    }
    .stButton>button {
        background-color: #0284c7 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0ea5e9 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(14, 165, 233, 0.3);
    }
    .card {
        background-color: #1e293b;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 15px;
    }
    .tool-badge {
        background-color: #0369a1;
        color: #e0f2fe;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    .success-badge {
        background-color: #15803d;
        color: #dcfce7;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
    }
    .fail-badge {
        background-color: #b91c1c;
        color: #fee2e2;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85em;
        font-weight: bold;
        display: inline-block;
    }
    
    /* 💬 Custom Chat Styling - Consistent Text Color and Modern Bubble look */
    [data-testid="stChatMessage"] {
        background-color: #232d3f !important; /* Lighter premium navy-slate, distinctly lighter than black */
        border: 1px solid #3d4e68 !important; /* Premium high-contrast border */
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    }
    
    /* Force bot response and user message text to be pure white and extremely sharp */
    [data-testid="stChatMessage"] div,
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span,
    [data-testid="stChatMessage"] label {
        color: #ffffff !important; /* Pure high-contrast white */
        font-size: 1.05rem !important; /* Crisp, slightly larger size */
        font-weight: 500 !important; /* Slightly bolder font-weight to prevent thin blurriness */
        line-height: 1.65 !important;
        text-rendering: optimizeLegibility !important;
        -webkit-font-smoothing: antialiased !important; /* Force subpixel crisp rendering */
        -moz-osx-font-smoothing: grayscale !important;
    }
    
    /* Special headers inside chat messages */
    [data-testid="stChatMessage"] h1, 
    [data-testid="stChatMessage"] h2, 
    [data-testid="stChatMessage"] h3, 
    [data-testid="stChatMessage"] h4 {
        color: #38bdf8 !important;
        font-weight: 700 !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        -webkit-font-smoothing: antialiased !important;
    }
    
    /* Code block styling inside chat messages */
    [data-testid="stChatMessage"] code {
        background-color: #0f141c !important;
        color: #38bdf8 !important;
        padding: 3px 6px !important;
        border-radius: 6px !important;
        font-family: 'Consolas', 'Courier New', monospace !important;
        font-size: 0.95em !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stChatMessage"] pre {
        background-color: #0f141c !important;
        border: 1px solid #2d3b4e !important;
        border-radius: 10px !important;
        padding: 14px !important;
    }
    
    [data-testid="stChatMessage"] pre code {
        background-color: transparent !important;
        padding: 0 !important;
        color: #f1f5f9 !important;
        font-weight: 500 !important;
    }
</style>
""", unsafe_allow_html=True)

# Add local directory to path to import agent modules
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
load_lab_env(ROOT)

from providers import make_provider
from tools import load_tool_declarations, to_openai_tools, TOOL_FUNCTIONS
from agent import ResearchAgent

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_run_log" not in st.session_state:
    st.session_state.agent_run_log = []

st.title("🕵️‍♂️ Research Agent Explorer")
st.markdown("##### *An Evidence-Driven Tool Calling & Prompt Engineering Lab UI*")

# Sidebar Configuration
st.sidebar.title("🛠️ Agent Configuration")

provider_name = st.sidebar.selectbox(
    "Select Provider",
    ["openai", "gemini", "anthropic"],
    index=0
)

# Auto-detect default models or configure based on env
default_model = ""
if provider_name == "openai":
    default_model = os.getenv("OPENAI_MODEL", "minimaxai/minimax-m2.7")
elif provider_name == "gemini":
    default_model = "gemini-3.5-flash"

model_name = st.sidebar.text_input("Model Override", value=default_model)

system_prompt_file = st.sidebar.text_input(
    "System Prompt Path",
    value="artifacts/system_prompt.md"
)

tools_file = st.sidebar.text_input(
    "Tools Config Path",
    value="artifacts/tools.yaml"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔑 Loaded Env Variables")
st.sidebar.code(f"""OPENAI_BASE_URL: {os.getenv("OPENAI_BASE_URL", "None")}
TAVILY_API_KEY: {"Loaded ✅" if os.getenv("TAVILY_API_KEY") else "Missing ❌"}
RAPIDAPI_KEY: {"Loaded ✅" if os.getenv("RAPIDAPI_KEY") else "Missing ❌"}
FIRECRAWL_API_KEY: {"Loaded ✅" if os.getenv("FIRECRAWL_API_KEY") else "Missing ❌"}""")

st.sidebar.markdown("---")
st.sidebar.markdown("### ✈️ Telegram Bot Integration")
telegram_token = st.sidebar.text_input(
    "Telegram Bot Token",
    value=os.getenv("TELEGRAM_BOT_TOKEN", ""),
    type="password",
    help="Enter your Telegram Bot Token from @BotFather"
)
telegram_chat_id = st.sidebar.text_input(
    "Telegram Chat ID",
    value=os.getenv("TELEGRAM_CHAT_ID", ""),
    help="Enter your Telegram Chat ID (User ID or Group ID)"
)

# Sync with environment variables dynamically
if telegram_token:
    os.environ["TELEGRAM_BOT_TOKEN"] = telegram_token
if telegram_chat_id:
    os.environ["TELEGRAM_CHAT_ID"] = telegram_chat_id

if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
    st.sidebar.success("Telegram Status: Connected ✅")
else:
    st.sidebar.warning("Telegram Status: Not Configured ⚠️")

# Tabs
tab_chat, tab_evals, tab_history, tab_tools = st.tabs([
    "💬 Live Chat Mode", 
    "📊 Run Evaluation Suite", 
    "📂 Historical Runs Explorer", 
    "🛠️ Registered Tools Inspector"
])

# Load core files
try:
    system_prompt = Path(system_prompt_file).read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(Path(tools_file))
    openai_tools = to_openai_tools(tool_declarations)
except Exception as e:
    st.error(f"Error loading system prompt/tools config: {e}")
    st.stop()

# ================= TAB 1: LIVE CHAT =================
with tab_chat:
    st.markdown("### 💬 Chat with the Research Agent")
    st.markdown("Talk to your customized agent, watch it choose tools, view execution logs, and reply.")
    
    # Reset Chat button
    if st.button("🔄 Clear Chat & Reset Session State"):
        st.session_state.messages = []
        st.session_state.agent_run_log = []
        st.rerun()

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Display intermediate tool call logs if any in current turn
    if st.session_state.agent_run_log:
        with st.expander("🛠️ Show Tool Execution Log (Latest Turn)", expanded=True):
            for log in st.session_state.agent_run_log:
                st.markdown(f"<span class='tool-badge'>Tool Call: {log['tool']}</span>", unsafe_allow_html=True)
                st.code(f"Arguments: {json.dumps(log['args'], indent=2, ensure_ascii=False)}")
                st.code(f"Result: {json.dumps(log['result'], indent=2, ensure_ascii=False)}")

    # Chat Input
    if user_input := st.chat_input("Ask the agent something (e.g. 'Lấy 3 tweet gần đây của Elon Musk'...)"):
        # Display user input
        with st.chat_message("user"):
            st.markdown(user_input)
            
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Initialize provider & agent
        try:
            provider = make_provider(provider_name)
            agent = ResearchAgent(
                provider, 
                system_prompt=system_prompt, 
                tools=openai_tools, 
                model=model_name if model_name else None
            )
            
            with st.spinner("Agent is thinking & executing tools..."):
                # Parse turns
                history_messages = []
                # To support multi-turn carryover in evaluation format, we can pass earlier turns
                if len(st.session_state.messages) > 1:
                    previous = st.session_state.messages[:-1]
                    latest = st.session_state.messages[-1]["content"]
                    previous_text = "\n".join(
                        f"- Earlier {item['role']} turn {index + 1}: {item['content']}"
                        for index, item in enumerate(previous)
                    )
                    content = (
                        "Conversation context for a multi-turn eval.\n"
                        "Use earlier turns only as context. Do not answer earlier turns and do not call tools for them.\n\n"
                        f"{previous_text}\n\n"
                        f"Latest user turn to answer now: {latest}"
                    )
                    history_messages = [{"role": "user", "content": content}]
                else:
                    history_messages = [{"role": "user", "content": user_input}]
                
                # Run Agent
                run = agent.run(history_messages)
                
            # Log tool runs
            st.session_state.agent_run_log = run.tool_results
            
            # Formulate response
            assistant_response = ""
            if run.text:
                assistant_response = run.text
            elif run.tool_calls:
                # Format a friendly summary of tool execution if no text was returned
                tool_names = ", ".join([f"`{c.name}`" for c in run.tool_calls])
                assistant_response = f"🔧 **Executed tool calls:** {tool_names}\n\n"
                for res in run.tool_results:
                    assistant_response += f"**Output of `{res['tool']}`:**\n```json\n{json.dumps(res['result'], indent=2, ensure_ascii=False)}\n```\n"
            else:
                assistant_response = "No response text or tool calls generated."
                
            # Display Assistant response
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
                
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            st.rerun()
            
        except Exception as e:
            st.error(f"Error executing agent: {e}")

# ================= TAB 2: RUN EVALS =================
with tab_evals:
    st.markdown("### 📊 Run Live Evaluations")
    st.markdown("Execute the evaluation suite and view real-time statistics and results.")
    
    eval_suite_file = st.selectbox(
        "Select Eval Cases File",
        ["data/eval_base.json", "data/eval_group.json", "data/eval_research_extension.json"]
    )
    
    eval_version = st.text_input("Run Version Label", value="v3")
    eval_suite_label = st.selectbox("Suite Label", ["base", "group", "extension"])
    
    if st.button("🚀 Run Live Evaluation Suite"):
        st.markdown("---")
        progress_bar = st.progress(0.0)
        status_text = st.empty()
        
        # Load cases
        try:
            cases_path = ROOT / eval_suite_file
            cases_data = json.loads(cases_path.read_text(encoding="utf-8"))
            cases = cases_data.get("cases", [])
            st.info(f"Loaded {len(cases)} cases from {eval_suite_file}")
        except Exception as e:
            st.error(f"Error loading eval cases: {e}")
            st.stop()
            
        results_container = st.container()
        
        # We will run this via a subprocess or direct execution inside the app
        cmd = [
            sys.executable,
            "run_eval.py",
            "--provider", provider_name,
            "--version", eval_version,
            "--suite", eval_suite_label,
            "--eval-cases", eval_suite_file,
            "--system-prompt", system_prompt_file,
            "--tools", tools_file
        ]
        if model_name:
            cmd.extend(["--model", model_name])
            
        status_text.text("Executing run_eval.py script in background...")
        
        try:
            # We run it synchronously to capture the output and display results
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=str(ROOT)
            )
            
            # Read output
            st.code(result.stdout)
            if result.stderr:
                st.warning("Warnings/Errors in stderr:")
                st.code(result.stderr)
                
            # Scan runs directory for the latest file
            runs_dir = ROOT / "runs"
            if runs_dir.exists():
                run_files = sorted(list(runs_dir.glob("*.json")), key=os.path.getmtime, reverse=True)
                if run_files:
                    latest_run = run_files[0]
                    st.success(f"Latest run JSON generated: `{latest_run.name}`")
                    
                    # Display metrics
                    run_data = json.loads(latest_run.read_text(encoding="utf-8"))
                    summary = run_data.get("summary", {})
                    
                    st.markdown("### 🏆 Final Scoreboard")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Case Accuracy", f"{summary.get('case_accuracy', 0.0)*100:.1f}%")
                    col2.metric("Routing Accuracy", f"{summary.get('tool_routing_accuracy', 0.0)*100:.1f}%")
                    col3.metric("Argument Accuracy", f"{summary.get('argument_accuracy', 0.0)*100:.1f}%")
                    col4.metric("Passed / Total", f"{summary.get('passed_cases', 0)} / {summary.get('measured_cases', 0)}")
                    
        except Exception as e:
            st.error(f"Error running evaluation: {e}")

# ================= TAB 3: HISTORICAL RUNS EXPLORER =================
with tab_history:
    st.markdown("### 📂 Historical Runs & Evidence Inspector")
    st.markdown("Load and inspect previous evaluation run JSON files to trace mistakes and mismatches.")
    
    runs_dir = ROOT / "runs"
    if not runs_dir.exists() or not list(runs_dir.glob("*.json")):
        st.info("No historical runs found. Run an evaluation suite first!")
    else:
        run_files = sorted([f.name for f in runs_dir.glob("*.json")], reverse=True)
        selected_run_file = st.selectbox("Select Run JSON File", run_files)
        
        if selected_run_file:
            run_path = runs_dir / selected_run_file
            run_data = json.loads(run_path.read_text(encoding="utf-8"))
            
            # Display run info
            summary = run_data.get("summary", {})
            st.markdown(f"**Run ID**: `{run_data.get('run_id')}` | **Model**: `{run_data.get('model')}` | **Generated At**: `{run_data.get('generated_at')}`")
            st.markdown(f"**Prompt Hash**: `{run_data.get('prompt_hash')[:12]}` | **Tools Hash**: `{run_data.get('tools_hash')[:12]}`")
            
            # Metrics Columns
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Case Accuracy", f"{summary.get('case_accuracy', 0.0)*100:.1f}%")
            col2.metric("Routing Accuracy", f"{summary.get('tool_routing_accuracy', 0.0)*100:.1f}%")
            col3.metric("Argument Accuracy", f"{summary.get('argument_accuracy', 0.0)*100:.1f}%")
            col4.metric("Passed Cases", f"{summary.get('passed_cases', 0)} / {summary.get('measured_cases', 0)}")
            
            # Error distribution
            st.markdown("#### 📉 Error Breakdown")
            col_fail, col_mismatch = st.columns(2)
            with col_fail:
                st.markdown("**Failure Counts by Type**")
                st.write(summary.get("failure_counts", {}))
            with col_mismatch:
                st.markdown("**Observed Mismatches**")
                st.write(summary.get("observed_mismatch_counts", {}))
                
            st.markdown("---")
            st.markdown("### 📋 Case-by-Case Log")
            
            filter_status = st.selectbox("Filter Status", ["All", "PASS Only", "FAIL Only"])
            
            for index, case in enumerate(run_data.get("results", [])):
                case_id = case.get("id")
                case_passed = case.get("result", {}).get("passed", False)
                case_failure = case.get("result", {}).get("failure_type") or "None"
                
                # Apply filter
                if filter_status == "PASS Only" and not case_passed:
                    continue
                if filter_status == "FAIL Only" and case_passed:
                    continue
                    
                status_html = "<span class='success-badge'>PASS</span>" if case_passed else f"<span class='fail-badge'>FAIL: {case_failure}</span>"
                
                with st.container():
                    st.markdown(f"##### {case_id} — {status_html}", unsafe_allow_html=True)
                    st.write(f"**Input Query / Turns:**")
                    st.code(case.get("input"))
                    
                    col_exp, col_act = st.columns(2)
                    with col_exp:
                        st.write("**Expected Tool Calls:**")
                        st.json(case.get("expect"))
                    with col_act:
                        st.write("**Observed Tool Calls:**")
                        st.json(case.get("result", {}).get("actual_tool_calls", []))
                        
                    if not case_passed:
                        st.markdown("**Mismatches / Failures:**")
                        st.error("\n".join(case.get("result", {}).get("failures", [])))
                        
                    st.markdown("---")

# ================= TAB 4: REGISTERED TOOLS =================
with tab_tools:
    st.markdown("### 🛠️ Registered Tools & Supplementary Integration Guide")
    st.markdown("Xem danh sách các công cụ đã được đăng ký và hướng dẫn chi tiết cách tích hợp/sử dụng hiệu quả các Tool bổ sung & Telegram.")
    
    subtab_schema, subtab_guide = st.tabs([
        "📋 Danh sách & Schema của Tools",
        "💡 Hướng dẫn & Cách sử dụng hiệu quả"
    ])
    
    with subtab_schema:
        st.info(f"Hiện tại hệ thống đã tải `{len(tool_declarations)}` tools được đăng ký trong file `tools.yaml`.")
        
        for tool in tool_declarations:
            name = tool.get("name")
            desc = tool.get("description")
            params = tool.get("parameters", {})
            req = params.get("required", [])
            props = params.get("properties", {})
            
            with st.expander(f"🔧 Tool: `{name}` — {desc[:80]}...", expanded=False):
                st.markdown(f"**Mô tả (Description)**: {desc}")
                st.markdown(f"**Tham số bắt buộc (Required parameters)**: `{req}`")
                st.markdown("**Cấu trúc tham số (Parameters Schema):**")
                st.json(props)
                
    with subtab_guide:
        st.markdown("""
        ### 🚀 Chi tiết về 3 Supplementary Tools (Công cụ bổ sung thêm)
        Chúng tôi đã nghiên cứu và phát triển thêm **03 công cụ bổ sung** mới, giúp Agent có khả năng nhận biết thời gian thực và phân tích văn bản chuyên sâu:
        """)
        
        # Tool 1 Card
        st.markdown("""
        <div class="card">
            <h4>📅 1. Tool <code>get_time</code> (Lấy thời gian hiện tại của hệ thống)</h4>
            <ul>
                <li><b>Chức năng:</b> Trả về ngày, giờ hiện tại (định dạng YYYY-MM-DD HH:MM:SS), múi giờ của hệ thống (timezone) và thứ trong tuần (day of week).</li>
                <li><b>Cách hoạt động dưới agent:</b> Khi người dùng hỏi các thông tin liên quan đến thời gian tương đối hoặc mốc thời gian thực tế (ví dụ: <i>"Tin tức 3 ngày gần đây"</i>, <i>"Hôm nay là thứ mấy?"</i>), Agent sẽ tự động gọi <code>get_time</code> đầu tiên để xác định mốc thời gian chuẩn làm cơ sở truy vấn cho các tool khác như <code>lookup</code> hay <code>social_search</code>.</li>
                <li><b>Cách sử dụng hiệu quả:</b> Đảm bảo Prompt hệ thống (System Prompt) có quy định rõ: <i>"Trước khi tìm kiếm tin tức giới hạn thời gian, hãy luôn gọi get_time để biết hôm nay là ngày nào"</i>. Điều này giúp Agent không bao giờ bị ảo tưởng về thời gian (temporal hallucination).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Tool 2 Card
        st.markdown("""
        <div class="card">
            <h4>📊 2. Tool <code>text_statistics</code> (Thống kê & Phân tích văn bản)</h4>
            <ul>
                <li><b>Chức năng:</b> Tính toán số lượng từ (word count), số ký tự (character count), số câu (sentence count), ước lượng thời gian đọc (reading time) và độ đa dạng từ vựng (ratio of unique words / total words).</li>
                <li><b>Cách hoạt động dưới agent:</b> Thích hợp khi xử lý văn bản dài, tóm tắt bài báo học thuật hoặc chuẩn bị nội dung trước khi gửi email/tin nhắn. Ví dụ: <i>"Hãy phân tích bài báo này xem độ đa dạng từ vựng thế nào"</i> hoặc <i>"Tóm tắt bài báo và tính thời gian đọc ước tính"</i>.</li>
                <li><b>Cách sử dụng hiệu quả:</b> Sử dụng kết hợp với tool <code>paper_text</code> (Arxiv parser) để phân tích chất lượng của các bài báo học thuật trước khi lưu trữ hoặc xuất báo cáo.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Tool 3 Card
        st.markdown("""
        <div class="card">
            <h4>🧠 3. Tool <code>sentiment_analysis</code> (Phân tích cảm xúc văn bản)</h4>
            <ul>
                <li><b>Chức năng:</b> Phân loại cảm xúc/thái độ của văn bản thành <b>Positive (Tích cực)</b>, <b>Negative (Tiêu cực)</b> hoặc <b>Neutral (Trung tính)</b> và trả về điểm số cảm xúc (score) từ -1.0 đến 1.0 kèm danh sách các từ khóa cảm xúc phát hiện được.</li>
                <li><b>Đặc điểm nổi bật:</b> Hỗ trợ cả <b>tiếng Anh</b> và <b>tiếng Việt</b> nhờ bộ từ điển Lexicon đa ngữ tùy chỉnh bao gồm các từ ngữ như <i>"hay, tốt, tuyệt, dở, tệ, hỏng, chán..."</i>.</li>
                <li><b>Cách hoạt động dưới agent:</b> Dùng để phân tích thái độ của dư luận, ví dụ: <i>"Tìm kiếm các tweet về GPT-5 và đánh giá xem mọi người đang khen hay chê"</i>. Agent sẽ gọi <code>social_search</code> để lấy danh sách tweet, sau đó gọi <code>sentiment_analysis</code> trên nội dung thu thập được để đưa ra báo cáo tổng hợp cực kỳ khoa học.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### 🔮 3 Unique & Powerful Supplementary Tools (Công cụ Độc & Lạ nhưng Cực kỳ Hữu ích)
        Để tăng cường vị thế dẫn đầu công nghệ của Research Agent, chúng tôi đã phát triển thêm 3 công cụ độc quyền đột phá, mang lại trải nghiệm chuyên nghiệp vượt trội:
        """)

        # Tool 4: agent_memory
        st.markdown("""
        <div class="card" style="border-left: 5px solid #a855f7;">
            <h4>💾 4. Tool <code>agent_memory</code> (Bộ nhớ dài hạn thông minh của Agent)</h4>
            <ul>
                <li><b>Chức năng:</b> Cho phép Agent tự động **lưu trữ, đọc, liệt kê và xóa** các cặp dữ liệu khóa-giá trị (Key-Value) hoặc ghi chú vào một file nhớ cục bộ (<code>data/agent_memory.json</code>).</li>
                <li><b>Tại sao độc lạ & hữu ích:</b> Các LLM thông thường hoàn toàn bị mất trí nhớ sau khi kết thúc phiên chat hoặc F5 trang. Bằng cách sử dụng <code>agent_memory</code>, Agent có thể lưu lại các bản thảo bài viết đang viết dở, lưu sở thích cá nhân của bạn, hoặc tạo danh sách việc cần làm (Todo List) và đọc lại chúng trong các buổi làm việc sau!</li>
                <li><b>Cách sử dụng hiệu quả:</b> Thử chat: <i>"Hãy lưu bản nháp nghiên cứu của tôi với key 'draft_gpt5' và nội dung là 'Dự kiến GPT-5 ra mắt vào cuối 2026 với khả năng suy luận đa bước nâng cao'"</i>. Phiên làm việc sau bạn chỉ cần gõ: <i>"Đọc lại bản nháp draft_gpt5 cho tôi"</i>!</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Tool 5: export_report
        st.markdown("""
        <div class="card" style="border-left: 5px solid #22c55e;">
            <h4>📄 5. Tool <code>export_report</code> (Xuất báo cáo HTML Premium đa phong cách)</h4>
            <ul>
                <li><b>Chức năng:</b> Nhận vào tiêu đề bài viết, nội dung dạng Markdown và một chủ đề giao diện (<code>glassmorphism</code>, <code>slate</code>, hoặc <code>corporate</code>) để biên dịch thành một trang HTML báo cáo tĩnh độc lập, cực kỳ đẹp mắt được lưu ở thư mục <code>exports/</code>.</li>
                <li><b>Tại sao độc lạ & hữu ích:</b> Thay vì chỉ in văn bản thuần túy tẻ nhạt trong bong bóng chat, Agent có thể tổng hợp toàn bộ kết quả phân tích mạng xã hội, các bài báo học thuật rồi tự động xuất bản thành một trang web báo cáo sang trọng, chuyên nghiệp với hiệu ứng mờ kính (glassmorphism) thời thượng, hỗ trợ đầy đủ Marked.js để kết xuất bảng biểu, khối code và trích dẫn!</li>
                <li><b>Cách sử dụng hiệu quả:</b> Thử ra lệnh: <i>"Hãy tổng hợp các bài báo về AI và xuất thành báo cáo HTML Premium chủ đề glassmorphism với tiêu đề 'AI Trends 2026' nhé"</i>. Agent sẽ tạo tệp tin và trả về đường link tuyệt vời để bạn mở ngay trên trình duyệt.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Tool 6: visualize_data
        st.markdown("""
        <div class="card" style="border-left: 5px solid #eab308;">
            <h4>📈 6. Tool <code>visualize_data</code> (Tự động vẽ biểu đồ dữ liệu SVG siêu đẹp)</h4>
            <ul>
                <li><b>Chức năng:</b> Nhận vào một từ điển dữ liệu (các điểm số hay tỷ lệ phần trăm) và tự động tính toán, kết xuất thành một biểu đồ hình cột (Bar) hoặc biểu đồ đường (Line) định dạng vector SVG sắc nét với hiệu ứng phát sáng neon (glow) cực đỉnh, lưu tệp ở thư mục <code>exports/</code>.</li>
                <li><b>Tại sao độc lạ & hữu ích:</b> Hoàn toàn **không cần bất kỳ thư viện vẽ biểu đồ nặng nề nào (như matplotlib hay plotly)**! Tool được lập trình thuật toán vẽ hình học thuần Python tạo ra file SVG nhẹ nhàng, chuẩn SEO, hiển thị tương thích hoàn hảo ở mọi độ phân giải.</li>
                <li><b>Cách sử dụng hiệu quả:</b> Thử chat: <i>"Hãy vẽ biểu đồ đường biểu diễn sự tăng trưởng điểm số từ v0 đến v3: v0 là 44.4%, v1 là 77.8%, v2 là 88.9%, v3 là 100%"</i>. Agent sẽ gọi tool và hiển thị biểu đồ SVG lung linh ngay lập tức!</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        ### ✈️ Chi tiết về công cụ gửi tin nhắn Telegram (Tool <code>send</code>)
        Công cụ gửi Telegram (`send`) đã được **tích hợp đầy đủ và sẵn sàng hoạt động** trong hệ thống code của chúng tôi! Dưới đây là cách sử dụng và cấu hình hiệu quả nhất:
        """)
        
        st.markdown("""
        <div class="card" style="border-left: 5px solid #0284c7;">
            <h4>🔄 Cơ chế xác nhận bảo mật 2 bước (Two-Step Confirmation)</h4>
            <p>Để tránh việc Agent tự ý gửi tin nhắn rác hoặc thông tin chưa được kiểm chứng lên kênh Telegram, tool <code>send</code> được thiết kế bắt buộc phải có thuộc tính xác nhận:</p>
            <ol>
                <li><b>Bước 1 (confirmed=False):</b> Khi người dùng ra lệnh gửi tin nhắn, Agent sẽ gọi tool với đối số <code>confirmed=False</code> đầu tiên. Hệ thống sẽ trả về trạng thái <code>needs_confirmation</code>.</li>
                <li><b>Bước 2 (Xác nhận từ người dùng):</b> Agent sẽ dừng lại, in ra nội dung tin nhắn và hỏi người dùng bằng ngôn ngữ tự nhiên: <i>"Tôi đã chuẩn bị nội dung tin nhắn gửi lên Telegram. Bạn có xác nhận muốn gửi không?"</i>.</li>
                <li><b>Bước 3 (confirmed=True):</b> Khi người dùng chat đồng ý (ví dụ: "Đồng ý", "Gửi đi", "Yes"), Agent mới gọi lại tool <code>send</code> lần thứ 2 với tham số <code>confirmed=True</code> để chính thức gửi tin nhắn đi.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        #### 🛠️ Hướng dẫn tích hợp & Tạo Bot Telegram để chạy Live trong 3 phút:
        Nếu bạn muốn thử nghiệm tính năng này trực tiếp ngay bây giờ:
        1. **Tạo Bot Telegram:**
           - Tìm kiếm `@BotFather` trên ứng dụng Telegram của bạn.
           - Gõ `/newbot` và đặt tên cho Bot. `@BotFather` sẽ cấp cho bạn một chuỗi **Telegram Bot Token** (ví dụ: `543216789:ABCDefGhIjK...`).
        2. **Lấy Chat ID của bạn (Người nhận tin nhắn):**
           - Hãy tìm kiếm `@userinfobot` trên Telegram và nhấn Start, it will return your **ID** (một chuỗi số dạng `123456789`).
           - Hoặc nhắn một tin nhắn bất kỳ cho Bot bạn vừa tạo, sau đó mở trình duyệt truy cập: `https://api.telegram.org/bot<TOKEN_CỦA_BẠN>/getUpdates` để tìm trường `"chat":{"id":...}` trong dữ liệu trả về.
        3. **Cấu hình trên Giao diện Streamlit:**
           - Nhập trực tiếp **Telegram Bot Token** và **Telegram Chat ID** vào khung **"✈️ Telegram Bot Integration"** ở sidebar bên trái giao diện này.
           - Hệ thống sẽ tự động cập nhật biến môi trường thời gian thực. Trạng thái sẽ chuyển sang màu xanh lá **Telegram Status: Connected ✅**.
        4. **Trải nghiệm Live Chat:**
           - Chuyển sang Tab **"💬 Live Chat Mode"**, thử gõ: *"Hãy gửi lời chào 'Xin chào từ Streamlit GUI' lên Telegram của tôi nhé"* và xem Agent thực hiện quy trình xác nhận bảo mật và gửi tin nhắn thực tế!
        """)
