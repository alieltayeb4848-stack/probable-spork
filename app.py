# -------------------------------------------------
# 🎬 AI Director Studio Pro — Ultra Edition v4.1
# ملف app.py — النسخة الكاملة المدمجة
# -------------------------------------------------

import streamlit as st
import json
import os
import uuid
import google.generativeai as genai

from fpdf import FPDF

# -------------------------------------------------
# إعداد مفتاح Gemini API
# -------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.warning("⚠️ لم يتم ضبط مفتاح GEMINI_API_KEY في متغيرات البيئة.")

# -------------------------------------------------
# إعداد صفحة Streamlit
# -------------------------------------------------
st.set_page_config(
    page_title="AI Director Studio Pro — Ultra Edition v4.1",
    page_icon="🎬",
    layout="wide"
)

# -------------------------------------------------
# تهيئة مجلد المشاريع
# -------------------------------------------------
if not os.path.exists("projects"):
    os.makedirs("projects")

# -------------------------------------------------
# تهيئة session_state الأساسية
# -------------------------------------------------
default_states = {
    "generated_scenes": [],
    "characters": [],
    "scene_links": [],
    "shot_design": [],
    "consistency_rules": [],
    "lorebook": {},
    "current_project": None,
    "selected_timeline_scene": None
}

for k, v in default_states.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------------------------------
# إصلاحات صغيرة في الذاكرة (دفاعي)
# -------------------------------------------------
required_states = [
    "generated_scenes", "characters", "scene_links",
    "shot_design", "consistency_rules", "lorebook"
]
for state in required_states:
    if state not in st.session_state:
        st.session_state[state] = [] if state != "lorebook" else {}

# -------------------------------------------------
# نموذج Gemini واحد فقط
# -------------------------------------------------
if GEMINI_API_KEY and "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = genai.GenerativeModel("gemini-pro")


# =================================================
# دوال التوليد الذكي (v4.1)
# =================================================

def auto_generate_lorebook(text):
    """توليد دفتر عالم محسّن."""
    model = st.session_state["gemini_model"]
    prompt = f"""
    استخرج دفتر عالم احترافي من النص التالي.

    يجب أن يحتوي على:
    - قوانين العالم
    - الزمن
    - الأماكن
    - الأحداث الكبرى
    - الثيمات
    - الرموز
    - التوترات الأساسية

    اكتب النتيجة بصيغة:
    العنوان: الوصف

    النص:
    {text}
    """
    response = model.generate_content(prompt)
    lines = response.text.split("\n")
    lore = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            lore[key.strip()] = value.strip()
    return lore


def auto_generate_characters(text):
    """توليد شخصيات محسّنة."""
    model = st.session_state["gemini_model"]
    prompt = f"""
    استخرج الشخصيات من النص بصيغة JSON.

    كل شخصية يجب أن تحتوي على:
    - name
    - role (دورها الدرامي)
    - description
    - background
    - motivation
    - strengths
    - weaknesses
    - relations
    - arc (القوس الشخصي)

    النص:
    {text}
    """
    response = model.generate_content(prompt)
    try:
        return json.loads(response.text)
    except:
        return []


def auto_generate_consistency_rules(text):
    """توليد قواعد تناسق محسّنة."""
    model = st.session_state["gemini_model"]
    prompt = f"""
    استخرج 12 قاعدة تحافظ على منطق القصة واستمراريتها.

    يجب أن تكون القواعد:
    - واضحة
    - قابلة للتطبيق
    - مرتبطة بالشخصيات أو العالم أو الأحداث

    النص:
    {text}
    """
    response = model.generate_content(prompt)
    return [line.strip() for line in response.text.split("\n") if line.strip()]


def auto_generate_scene_links(scenes):
    """توليد روابط مشاهد محسّنة."""
    links = []
    for i in range(len(scenes) - 1):
        current_title = scenes[i]["title"]
        next_title = scenes[i + 1]["title"]
        links.append({
            "current_scene": current_title,
            "next_scene": next_title,
            "reason": "تطور طبيعي في الأحداث.",
            "effect": "يزيد التوتر الدرامي.",
            "change": "يغير حالة الشخصية أو العالم."
        })
    return links


def auto_generate_shots(scenes):
    """توليد لقطات سينمائية محسّنة."""
    model = st.session_state["gemini_model"]
    shots = []
    for scene in scenes:
        prompt = f"""
        أنشئ لقطة سينمائية احترافية للمشهد التالي:

        العنوان: {scene['title']}
        الوصف: {scene['description']}

        يجب أن تحتوي على:
        - type
        - angle
        - lens
        - lighting
        - mood
        - movement
        - reason (سبب اختيار اللقطة)

        اكتب النتيجة بصيغة JSON.
        """
        response = model.generate_content(prompt)
        try:
            shot = json.loads(response.text)
            shots.append(shot)
        except:
            shots.append({
                "type": "Wide Shot",
                "angle": "Eye Level",
                "lens": "35mm",
                "lighting": "Soft Light",
                "mood": "Neutral",
                "movement": "Static",
                "reason": "لقطة افتراضية."
            })
    return shots


# -------------------------------------------------
# Cache ذكي للتوليد (v4.1)
# -------------------------------------------------
@st.cache_data(show_spinner=False)
def cached_lore(text):
    return auto_generate_lorebook(text)

@st.cache_data(show_spinner=False)
def cached_characters(text):
    return auto_generate_characters(text)

@st.cache_data(show_spinner=False)
def cached_rules(text):
    return auto_generate_consistency_rules(text)

@st.cache_data(show_spinner=False)
def cached_shots(scenes):
    return auto_generate_shots(scenes)

@st.cache_data(show_spinner=False)
def cached_links(scenes):
    return auto_generate_scene_links(scenes)


def fast_auto_generate(scenes):
    """توليد سريع باستخدام Cache."""
    full_text = "\n".join([s["description"] for s in scenes])
    st.session_state["lorebook"] = cached_lore(full_text)
    st.session_state["characters"] = cached_characters(full_text)
    st.session_state["consistency_rules"] = cached_rules(full_text)
    st.session_state["scene_links"] = cached_links(scenes)
    st.session_state["shot_design"] = cached_shots(scenes)
    return True


# =================================================
# UX Helpers — رسائل مخصصة
# =================================================

def success_msg(text):
    st.markdown(
        f"""
        <div style='background-color:#0f5132;padding:12px;border-radius:8px;color:#d1e7dd;margin-bottom:10px;'>
            ✔️ {text}
        </div>
        """,
        unsafe_allow_html=True
    )

def error_msg(text):
    st.markdown(
        f"""
        <div style='background-color:#842029;padding:12px;border-radius:8px;color:#f8d7da;margin-bottom:10px;'>
            ❌ {text}
        </div>
        """,
        unsafe_allow_html=True
    )

def info_msg(text):
    st.markdown(
        f"""
        <div style='background-color:#055160;padding:12px;border-radius:8px;color:#cff4fc;margin-bottom:10px;'>
            ℹ️ {text}
        </div>
        """,
        unsafe_allow_html=True
    )


# =================================================
# CSS — Dark Theme + Cards + Animation
# =================================================
custom_ui_css = """
<style>
    body {
        background-color: #0d1117 !important;
    }
    .card {
        background-color: #161b22;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid #222;
        box-shadow: 0 0 8px rgba(0,0,0,0.4);
        transition: 0.25s;
    }
    .card:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(0,0,0,0.6);
    }
    .fade-in {
        animation: fadeIn 0.6s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .stButton>button {
        background-color: #238636;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        border: none;
        transition: 0.2s;
    }
    .stButton>button:hover {
        background-color: #2ea043;
        transform: scale(1.05);
    }
    section[data-testid="stSidebar"] {
        background-color: #0f141a;
        border-right: 1px solid #222;
    }
    h1, h2, h3, h4, h5, h6, p, span {
        color: #e6edf3 !important;
    }
    footer {visibility: hidden;}
</style>
"""
st.markdown(custom_ui_css, unsafe_allow_html=True)


# =================================================
# القائمة الجانبية — Navigation
# =================================================
st.sidebar.title("🎬 AI Director Studio Pro")
st.sidebar.markdown("### Ultra Edition v4.1")

main_page = st.sidebar.radio(
    "اختر الصفحة:",
    [
        "🎬 مولّد السيناريو",
        "🎞️ الخط الزمني السينمائي",
        "📖 وضع القصة (Story Mode)",
        "📄 تصدير PDF",
        "📦 تصدير JSON",
        "📁 إدارة المشاريع"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**المطور:** علي — Ultra Edition v4.1")

# زر إعادة الضبط في الشريط الجانبي
st.sidebar.markdown("---")
if st.sidebar.button("🔄 إعادة ضبط التطبيق بالكامل"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.sidebar.success("✔️ تم إعادة ضبط التطبيق.")
    st.rerun()


# =================================================
# 🎬 صفحة مولّد السيناريو
# =================================================
if main_page == "🎬 مولّد السيناريو":

    st.title("🎬 مولّد السيناريو السينمائي")
    st.markdown("### اكتب فكرة أو ملخص، ودع النظام يبني لك مشاهد سينمائية كاملة.")

    prompt_text = st.text_area(
        "اكتب وصف القصة أو الفكرة الأساسية:",
        height=180,
        placeholder="اكتب هنا الفكرة العامة، الثيم، الشخصيات الأساسية، أو أي تفاصيل تريد أن يبني عليها النظام المشاهد..."
    )

    col_gen, col_clear = st.columns([2, 1])

    with col_gen:
        generate_btn = st.button("🎬 توليد المشاهد")
    with col_clear:
        clear_btn = st.button("🧹 مسح المشاهد الحالية")

    if clear_btn:
        st.session_state["generated_scenes"] = []
        st.session_state["characters"] = []
        st.session_state["scene_links"] = []
        st.session_state["shot_design"] = []
        st.session_state["consistency_rules"] = []
        st.session_state["lorebook"] = {}
        success_msg("تم مسح المشاهد والبيانات المرتبطة.")

    if generate_btn:
        if not prompt_text.strip():
            error_msg("الرجاء إدخال وصف للقصة أولًا.")
        elif "gemini_model" not in st.session_state:
            error_msg("لم يتم ضبط مفتاح GEMINI_API_KEY. يرجى تعيينه في متغيرات البيئة.")
        else:
            model = st.session_state["gemini_model"]
            gen_prompt = f"""
            أنشئ قائمة مشاهد سينمائية لقصة بناءً على الوصف التالي.

            لكل مشهد، أعده بصيغة JSON داخل قائمة:

            [
              {{
                "title": "",
                "description": ""
              }}
            ]

            الوصف:
            {prompt_text}
            """

            with st.spinner("🎬 يتم توليد المشاهد..."):
                response = model.generate_content(gen_prompt)

            try:
                scenes = json.loads(response.text)
                st.session_state["generated_scenes"] = scenes
                fast_auto_generate(scenes)
                success_msg("تم توليد المشاهد وتشغيل الدمج الذكي (Ultra Edition v4.1).")
            except Exception as e:
                error_msg("حدث خطأ أثناء تحليل استجابة النموذج. تأكد من صحة المفتاح أو أعد المحاولة.")
                st.write(e)

    st.markdown("---")

    if st.session_state["generated_scenes"]:
        st.markdown("## 🎬 المشاهد المولّدة")
        for i, scene in enumerate(st.session_state["generated_scenes"], start=1):
            st.markdown(
                f"""
                <div class="card fade-in" style="margin-bottom:15px;">
                    <h3>🎬 مشهد {i}: {scene['title']}</h3>
                    <p>{scene['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        info_msg("لم يتم توليد مشاهد بعد. اكتب وصف القصة واضغط على زر التوليد.")


# =================================================
# 🎞️ صفحة الخط الزمني السينمائي
# =================================================
elif main_page == "🎞️ الخط الزمني السينمائي":

    st.title("🎞️ الخط الزمني السينمائي (Cinematic Timeline)")
    st.markdown("### عرض المشاهد على شكل شريط فيلم + تفاصيل عمودية لكل مشهد")

    if not st.session_state["generated_scenes"]:
        info_msg("لم يتم توليد مشاهد بعد.")
    else:
        scenes = st.session_state["generated_scenes"]

        st.markdown("## 🎬 الخط الزمني (Film Strip Style)")

        film_strip_css = """
        <style>
        .film-strip {
            display: flex;
            gap: 15px;
            overflow-x: auto;
            padding: 10px;
            white-space: nowrap;
        }
        .film-card {
            background-color: #1a1f27;
            border: 2px solid #333;
            border-radius: 8px;
            padding: 12px 20px;
            color: white;
            font-size: 16px;
            display: inline-block;
            transition: 0.2s;
            box-shadow: 0 0 0px #000;
        }
        .film-card:hover {
            background-color: #222831;
            transform: scale(1.05);
            box-shadow: 0 0 10px #000;
            cursor: pointer;
        }
        .selected-film-card {
            background-color: #2d333b !important;
            border: 2px solid #58a6ff !important;
            transform: scale(1.05);
            box-shadow: 0 0 12px #000;
        }
        </style>
        """
        st.markdown(film_strip_css, unsafe_allow_html=True)

        st.markdown("<div class='film-strip'>", unsafe_allow_html=True)

        for i, scene in enumerate(scenes):
            css_class = "film-card"
            if st.session_state.get("selected_timeline_scene") == i:
                css_class += " selected-film-card"

            if st.button(f"مشهد {i+1}", key=f"film_btn_{i}"):
                st.session_state["selected_timeline_scene"] = i

            st.markdown(
                f"<div class='{css_class}'>▮◼◼ {scene['title']} ◼◼▮</div>",
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")

        st.markdown("## 📑 تفاصيل المشهد")

        if st.session_state["selected_timeline_scene"] is not None:
            idx = st.session_state["selected_timeline_scene"]
            scene = scenes[idx]

            st.markdown(f"### 🎬 {scene['title']}")

            st.markdown(
                f"""
                <div style='background-color:#161b22;padding:15px;border-radius:8px;margin-bottom:15px;'>
                    <h4>📝 وصف المشهد</h4>
                    <p>{scene['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("### 👥 الشخصيات المشاركة")
            found_chars = []
            for char in st.session_state["characters"]:
                if isinstance(char, dict) and char.get("name", "") in scene["description"]:
                    found_chars.append(char["name"])

            if found_chars:
                for c in found_chars:
                    st.markdown(f"- {c}")
            else:
                st.markdown("- لا توجد شخصيات محددة.")

            st.markdown("### 🎥 اللقطة السينمائية")
            if idx < len(st.session_state["shot_design"]):
                st.json(st.session_state["shot_design"][idx])
            else:
                info_msg("لا توجد لقطة لهذا المشهد.")

            st.markdown("### 🔗 الروابط")
            for link in st.session_state["scene_links"]:
                if link["current_scene"] == scene["title"]:
                    st.write(f"➡️ ينتقل إلى: {link['next_scene']}")
                    st.write(f"📌 السبب: {link['reason']}")
                    st.write(f"🎯 النتيجة: {link['effect']}")

            st.markdown("### ⚖️ قواعد التناسق")
            related_rules = [
                r for r in st.session_state["consistency_rules"]
                if scene["title"] in r
            ]
            if related_rules:
                for r in related_rules:
                    st.markdown(f"- {r}")
            else:
                st.markdown("- لا توجد قواعد مرتبطة.")
        else:
            info_msg("اضغط على أي مشهد في شريط الفيلم لعرض التفاصيل.")


# =================================================
# 📖 صفحة Story Mode
# =================================================
elif main_page == "📖 وضع القصة (Story Mode)":

    st.title("📖 وضع القصة السينمائي (Story Mode)")
    st.markdown("### عرض القصة كاملة بصيغة سيناريو احترافي")

    if not st.session_state["generated_scenes"]:
        info_msg("لم يتم توليد مشاهد بعد.")
    else:
        scenes = st.session_state["generated_scenes"]
        characters = st.session_state["characters"]
        links = st.session_state["scene_links"]
        shots = st.session_state["shot_design"]
        rules = st.session_state["consistency_rules"]
        lore = st.session_state["lorebook"]

        st.markdown("## 🌍 عالم القصة (Lorebook)")
        if lore:
            for key, value in lore.items():
                st.markdown(
                    f"""
                    <div class="card fade-in" style='margin-bottom:10px;'>
                        <h4>📌 {key}</h4>
                        <p>{value}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            info_msg("لا توجد عناصر في دفتر العالم بعد.")

        st.markdown("---")
        st.markdown("## 🎬 القصة الكاملة")

        for i, scene in enumerate(scenes):
            st.markdown(
                f"""
                <div class="card fade-in" style="margin-bottom:25px;">
                    <h2>🎬 {scene['title']}</h2>
                    <p style='font-size:16px;line-height:1.7;'>{scene['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("### 👥 الشخصيات المشاركة")
            found_chars = []
            for char in characters:
                if isinstance(char, dict) and char.get("name", "") in scene["description"]:
                    found_chars.append(char["name"])
            if found_chars:
                for c in found_chars:
                    st.markdown(f"- {c}")
            else:
                st.markdown("- لا توجد شخصيات محددة.")

            st.markdown("### 🎥 اللقطة السينمائية")
            if i < len(shots):
                st.json(shots[i])
            else:
                info_msg("لا توجد لقطة لهذا المشهد.")

            st.markdown("### 🔗 الروابط")
            for link in links:
                if link["current_scene"] == scene["title"]:
                    st.write(f"➡️ ينتقل إلى: {link['next_scene']}")
                    st.write(f"📌 السبب: {link['reason']}")
                    st.write(f"🎯 النتيجة: {link['effect']}")

            st.markdown("### ⚖️ قواعد التناسق المرتبطة")
            related_rules = [r for r in rules if scene["title"] in r]
            if related_rules:
                for r in related_rules:
                    st.markdown(f"- {r}")
            else:
                st.markdown("- لا توجد قواعد مرتبطة.")

            st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)


# =================================================
# 📄 صفحة تصدير PDF
# =================================================
elif main_page == "📄 تصدير PDF":

    st.title("📄 تصدير المشروع إلى PDF")
    st.markdown("### إنشاء ملف PDF احترافي يحتوي على القصة الكاملة + المشاهد + اللقطات + الشخصيات + دفتر العالم")

    if not st.session_state["generated_scenes"]:
        info_msg("لا توجد مشاهد لتصديرها.")
    else:
        scenes = st.session_state["generated_scenes"]
        characters = st.session_state["characters"]
        links = st.session_state["scene_links"]
        shots = st.session_state["shot_design"]
        rules = st.session_state["consistency_rules"]
        lore = st.session_state["lorebook"]

        if st.button("📄 إنشاء PDF"):

            pdf = FPDF()
            pdf.add_page()

            try:
                pdf.add_font("Arabic", "", "Amiri-Regular.ttf", uni=True)
                pdf.set_font("Arabic", size=16)
            except:
                pdf.set_font("Arial", size=16)

            # الغلاف
            pdf.set_font("Arial", size=22)
            pdf.cell(0, 10, txt="AI Director Studio Pro - Ultra Edition v4.1", ln=True, align="C")
            pdf.ln(10)
            pdf.cell(0, 10, txt="Project Report", ln=True, align="C")
            pdf.ln(20)

            # دفتر العالم
            pdf.set_font("Arial", size=18)
            pdf.cell(0, 10, txt="World Lorebook", ln=True)
            pdf.set_font("Arial", size=14)
            for key, value in lore.items():
                try:
                    pdf.multi_cell(0, 8, txt=f"{key}: {value}")
                except:
                    pdf.multi_cell(0, 8, txt="[encoding error]")
                pdf.ln(2)

            pdf.add_page()

            # الشخصيات
            pdf.set_font("Arial", size=18)
            pdf.cell(0, 10, txt="Characters", ln=True)
            pdf.set_font("Arial", size=14)
            for char in characters:
                if isinstance(char, dict):
                    try:
                        pdf.multi_cell(0, 8, txt=f"Name: {char.get('name','')}")
                        pdf.multi_cell(0, 8, txt=f"Role: {char.get('role','')}")
                        pdf.multi_cell(0, 8, txt=f"Description: {char.get('description','')}")
                        pdf.multi_cell(0, 8, txt=f"Background: {char.get('background','')}")
                        pdf.multi_cell(0, 8, txt=f"Motivation: {char.get('motivation','')}")
                        pdf.multi_cell(0, 8, txt=f"Arc: {char.get('arc','')}")
                    except:
                        pdf.multi_cell(0, 8, txt="[character encoding error]")
                    pdf.ln(5)

            pdf.add_page()

            # القواعد
            pdf.set_font("Arial", size=18)
            pdf.cell(0, 10, txt="Consistency Rules", ln=True)
            pdf.set_font("Arial", size=14)
            for rule in rules:
                try:
                    pdf.multi_cell(0, 8, txt=f"- {rule}")
                except:
                    pdf.multi_cell(0, 8, txt="- [encoding error]")

            pdf.add_page()

            # القصة الكاملة
            pdf.set_font("Arial", size=18)
            pdf.cell(0, 10, txt="Full Story", ln=True)
            pdf.set_font("Arial", size=14)
            for i, scene in enumerate(scenes):
                pdf.ln(5)
                pdf.set_font("Arial", size=16)
                try:
                    pdf.multi_cell(0, 8, txt=f"Scene: {scene['title']}")
                except:
                    pdf.multi_cell(0, 8, txt="Scene: [encoding error]")
                pdf.set_font("Arial", size=14)
                try:
                    pdf.multi_cell(0, 8, txt=scene["description"])
                except:
                    pdf.multi_cell(0, 8, txt="[encoding error]")

                if i < len(shots):
                    try:
                        pdf.multi_cell(0, 8, txt=f"Shot: {json.dumps(shots[i], ensure_ascii=True)}")
                    except:
                        pdf.multi_cell(0, 8, txt="Shot: [encoding error]")

                for link in links:
                    if link["current_scene"] == scene["title"]:
                        try:
                            pdf.multi_cell(0, 8, txt=f"-> Next: {link['next_scene']}")
                        except:
                            pass
                pdf.ln(5)

            pdf.output("project_export.pdf")
            success_msg("🎉 تم إنشاء ملف PDF بنجاح!")

            with open("project_export.pdf", "rb") as f:
                st.download_button(
                    "⬇️ تحميل PDF",
                    data=f,
                    file_name="project.pdf",
                    mime="application/pdf"
                )


# =================================================
# 📦 صفحة تصدير JSON
# =================================================
elif main_page == "📦 تصدير JSON":

    st.title("📦 تصدير المشروع بصيغة JSON")
    st.markdown("### إنشاء ملف JSON يحتوي على جميع عناصر المشروع")

    if not st.session_state["generated_scenes"]:
        info_msg("لا توجد مشاهد لتصديرها.")
    else:
        scenes = st.session_state["generated_scenes"]
        characters = st.session_state["characters"]
        links = st.session_state["scene_links"]
        shots = st.session_state["shot_design"]
        rules = st.session_state["consistency_rules"]
        lore = st.session_state["lorebook"]

        if st.button("📦 إنشاء JSON"):
            project_json = {
                "scenes": scenes,
                "characters": characters,
                "scene_links": links,
                "shot_design": shots,
                "consistency_rules": rules,
                "lorebook": lore,
                "version": "4.1"
            }

            json_str = json.dumps(project_json, ensure_ascii=False, indent=4)
            success_msg("🎉 تم إنشاء ملف JSON بنجاح!")

            st.download_button(
                "⬇️ تحميل JSON",
                data=json_str.encode("utf-8"),
                file_name="project_export.json",
                mime="application/json"
            )


# =================================================
# 📁 إدارة المشاريع
# =================================================
elif main_page == "📁 إدارة المشاريع":

    st.title("📁 إدارة المشاريع — Project Manager")
    st.markdown("### حفظ وفتح المشاريع بصيغة Ultra Edition v4.1")

    # إنشاء مشروع جديد
    st.markdown("## 🆕 إنشاء مشروع جديد")
    new_project_name = st.text_input("اسم المشروع:")

    if st.button("📁 إنشاء مشروع"):
        if new_project_name.strip() != "":
            project_id = str(uuid.uuid4())
            project_path = f"projects/{project_id}.json"
            new_project = {
                "id": project_id,
                "name": new_project_name,
                "scenes": [],
                "characters": [],
                "scene_links": [],
                "shot_design": [],
                "consistency_rules": [],
                "lorebook": {},
                "version": "4.1"
            }
            with open(project_path, "w", encoding="utf-8") as f:
                json.dump(new_project, f, ensure_ascii=False, indent=4)
            success_msg("🎉 تم إنشاء المشروع بنجاح!")
        else:
            error_msg("الرجاء إدخال اسم المشروع.")

    st.markdown("---")

    # فتح مشروع موجود
    st.markdown("## 📂 فتح مشروع موجود")
    project_files = [f for f in os.listdir("projects") if f.endswith(".json")]

    if len(project_files) == 0:
        info_msg("لا توجد مشاريع محفوظة بعد.")
    else:
        selected_file = st.selectbox("اختر مشروعًا:", project_files)

        if st.button("📂 فتح المشروع"):
            with open(f"projects/{selected_file}", "r", encoding="utf-8") as f:
                project_data = json.load(f)

            # إصلاح المشاريع القديمة تلقائيًا
            required_keys = [
                "scenes", "characters", "scene_links",
                "shot_design", "consistency_rules", "lorebook"
            ]
            for key in required_keys:
                if key not in project_data:
                    project_data[key] = [] if key != "lorebook" else {}

            st.session_state["current_project"] = project_data
            st.session_state["generated_scenes"] = project_data["scenes"]
            st.session_state["characters"] = project_data["characters"]
            st.session_state["scene_links"] = project_data["scene_links"]
            st.session_state["shot_design"] = project_data["shot_design"]
            st.session_state["consistency_rules"] = project_data["consistency_rules"]
            st.session_state["lorebook"] = project_data["lorebook"]

            success_msg("🎉 تم فتح المشروع بنجاح!")

    st.markdown("---")

    # حفظ المشروع الحالي
    st.markdown("## 💾 حفظ المشروع الحالي")

    if st.session_state.get("current_project"):
        if st.button("💾 حفظ المشروع"):
            project = st.session_state["current_project"]
            project_id = project["id"]
            project_path = f"projects/{project_id}.json"

            project["scenes"] = st.session_state["generated_scenes"]
            project["characters"] = st.session_state["characters"]
            project["scene_links"] = st.session_state["scene_links"]
            project["shot_design"] = st.session_state["shot_design"]
            project["consistency_rules"] = st.session_state["consistency_rules"]
            project["lorebook"] = st.session_state["lorebook"]
            project["version"] = "4.1"

            with open(project_path, "w", encoding="utf-8") as f:
                json.dump(project, f, ensure_ascii=False, indent=4)

            success_msg("✔️ تم حفظ المشروع بنجاح!")
    else:
        info_msg("لا يوجد مشروع مفتوح حاليًا.")


# =================================================
# 🔥 الفوتر
# =================================================
st.markdown("""
<hr style='border: 1px solid #333; margin-top: 40px; margin-bottom: 30px;'>
<div style='text-align:center; color:#777; font-size:14px;'>
    AI Director Studio Pro — Ultra Edition v4.1<br>
    واجهة عربية • وضع داكن • Timeline مزدوج • Story Mode • PDF/JSON Export • Hybrid AI
</div>
""", unsafe_allow_html=True)
