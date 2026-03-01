import streamlit as st
import whisper
from gtts import gTTS
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import io
import random
import time


# ── Audio processing ──────────────────────────────────────────────────────────

def transcribe_chunk(audio_chunk_path):
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_chunk_path)
    return result["text"]


def split_audio(audio_file, chunk_duration_ms):
    audio = AudioSegment.from_wav(audio_file)
    chunk_count = len(audio) // chunk_duration_ms + 1
    chunks = []
    for i in range(chunk_count):
        start_time = i * chunk_duration_ms
        end_time = min((i + 1) * chunk_duration_ms, len(audio))
        chunk = audio[start_time:end_time]
        with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            chunk.export(tmp.name, format="wav")
            chunks.append(tmp.name)
    return chunks


def transcribe_audio(audio_file, chunk_duration_ms):
    chunks = split_audio(audio_file, chunk_duration_ms)
    return " ".join(transcribe_chunk(c) for c in chunks)


def filter_bad_words(text, bad_words, censor_type):
    beep_options = ["BEEP", "*bleep*", "$#@%!", "****", "[censored]", "[redacted]", "!@#$"]
    filtered = []
    for word in text.split():
        if any(bw in word.lower() for bw in bad_words):
            if censor_type == "Random":
                filtered.append(random.choice(beep_options))
            elif censor_type == "Dolphin":
                filtered.append("🐬" * (len(word) // 2 + 1))
            elif censor_type == "Symbols":
                syms = ["#", "@", "$", "%", "&", "*", "!"]
                filtered.append("".join(random.choice(syms) for _ in range(len(word))))
            else:
                filtered.append("BEEP")
        else:
            filtered.append(word)
    return " ".join(filtered)


def text_to_speech(text):
    tts = gTTS(text=text, lang="en", slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return buf


# ── UI helpers ────────────────────────────────────────────────────────────────

def set_custom_theme():
    st.markdown(
        """
        <style>
        .main { background: linear-gradient(to right, #1e3c72, #2a5298); color: white; }
        .stApp { max-width: 1000px; margin: 0 auto; }
        h1 {
            color: #FFD700;
            text-shadow: 2px 2px 4px #000000;
            font-size: 3.5em;
            text-align: center;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%   { transform: scale(1); }
            50%  { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        .upload-box {
            border: 3px dashed #FFD700;
            border-radius: 20px;
            padding: 30px;
            text-align: center;
            margin: 20px 0;
            background-color: rgba(0,0,0,0.3);
        }
        .censored-badge {
            display: inline-block;
            background-color: #FF4500;
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-weight: bold;
            margin: 5px;
        }
        .stButton button {
            background-color: #FF4500;
            color: white;
            font-weight: bold;
            padding: 10px 25px;
            border-radius: 10px;
            border: none;
            transition: all 0.3s;
        }
        .stButton button:hover {
            background-color: #FFD700;
            color: black;
            transform: scale(1.05);
        }
        .result-box {
            background-color: rgba(0,0,0,0.5);
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def display_fun_facts():
    facts = [
        "The average person swears about 80 times per day.",
        "Studies show that swearing can actually increase pain tolerance.",
        "The censorship sound 'BEEP' dates back to early radio and TV broadcasting.",
        "In medieval times, swear words were often related to religious blasphemy.",
        "Some languages have more than twice as many swear words as others.",
        "The first recorded TV censorship beep was in the 1950s.",
        "Different cultures have wildly different taboo words and phrases.",
        "Swearing in a foreign language activates different brain areas than in your native tongue.",
        "Dolphins make high-pitched sounds similar to TV beeps — hence dolphin censorship!",
        "Some streaming platforms use AI to detect and censor profanity in real-time.",
    ]
    st.sidebar.markdown("### 🎓 **Did You Know?**")
    st.sidebar.info(random.choice(facts))


# ── Main app ──────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="VulgarVeto", page_icon="🔊", layout="wide")
    set_custom_theme()

    # Built-in bad-words list (fallback — no external file required)
    bad_words = [
        "damn", "hell", "shit", "fuck", "ass", "bastard", "crap",
        "bitch", "piss", "dick", "cock", "pussy", "whore", "slut",
        "cunt", "motherfucker", "asshole", "bullshit"
    ]

    # Title
    st.markdown(
        """
        <div style="text-align:center; margin-bottom:30px;">
            <h1>🔊 VulgarVeto 🚫</h1>
            <p style="font-size:1.2em; color:#FFD700;">
                Keep it clean, keep it mean, bleep that obscene!
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Animated equalizer bar
    st.markdown(
        """
        <div style="display:flex; justify-content:center; margin:20px 0;">
            <div style="width:10px;height:20px;background:#FFD700;margin:0 2px;animation:eq 1s infinite;"></div>
            <div style="width:10px;height:40px;background:#FFD700;margin:0 2px;animation:eq 0.8s infinite;"></div>
            <div style="width:10px;height:15px;background:#FFD700;margin:0 2px;animation:eq 1.2s infinite;"></div>
            <div style="width:10px;height:30px;background:#FFD700;margin:0 2px;animation:eq 0.6s infinite;"></div>
            <div style="width:10px;height:45px;background:#FFD700;margin:0 2px;animation:eq 0.7s infinite;"></div>
        </div>
        <style>
        @keyframes eq {
            0%,100% { transform:scaleY(1); }
            50%      { transform:scaleY(0.4); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["🎤 Audio Filter", "ℹ️ About", "⚙️ Settings"])

    # ── Tab 0: Audio Filter ───────────────────────────────────────────────────
    with tabs[0]:
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("**Drop your potentially vulgar audio here**", type=["wav"])
        st.markdown("</div>", unsafe_allow_html=True)

        if uploaded_file:
            st.audio(uploaded_file, format="audio/wav")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Censorship Style")
                censor_type = st.selectbox(
                    "Choose how to censor bad words:",
                    ["Classic BEEP", "Random", "Dolphin", "Symbols"],
                )
            with col2:
                st.markdown("### Processing Method")
                chunk_duration = st.slider("Chunk duration (ms)", 5000, 30000, 15000, 5000)

            if st.button("🚫 Clean My Audio!"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("Analyzing audio...")
                progress_bar.progress(10)
                time.sleep(0.5)

                status_text.text("Transcribing content...")
                progress_bar.progress(30)

                # Save upload to a temp file for pydub
                with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                    tmp.write(uploaded_file.read())
                    tmp_path = tmp.name

                transcription = transcribe_audio(tmp_path, chunk_duration)

                status_text.text("Detecting naughty words...")
                progress_bar.progress(60)
                time.sleep(0.5)

                status_text.text("Applying censorship...")
                progress_bar.progress(80)
                filtered_text = filter_bad_words(transcription, bad_words, censor_type)

                status_text.text("Generating clean audio...")
                progress_bar.progress(90)
                filtered_audio = text_to_speech(filtered_text)

                progress_bar.progress(100)
                status_text.text("Complete! 🎉")
                time.sleep(1)
                progress_bar.empty()
                status_text.empty()

                # Stats
                total_words = len(transcription.split())
                bad_count = sum(
                    1 for w in transcription.lower().split()
                    if any(bw in w for bw in bad_words)
                )
                pct = (bad_count / total_words * 100) if total_words > 0 else 0

                st.markdown('<div class="result-box">', unsafe_allow_html=True)

                # Profanity meter
                bar_color = "green" if pct < 20 else ("yellow" if pct < 50 else "red")
                st.markdown(
                    f"""
                    ### Profanity Meter 🌡️
                    <div style="width:100%;background:#e0e0e0;border-radius:10px;height:30px;margin:10px 0;">
                        <div style="width:{min(pct,100):.1f}%;background:linear-gradient(to right,green,{bar_color});
                        height:100%;border-radius:10px;text-align:center;line-height:30px;
                        color:white;font-weight:bold;">
                            {pct:.1f}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if pct > 50:
                    st.warning("Whoa there, sailor! That's some colorful language! 🚢")
                elif pct > 20:
                    st.info("Hmm, you could use a little soap in that mouth! 🧼")
                else:
                    st.success("Pretty clean! Just a few touch-ups needed. ✨")

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("### Original Transcription")
                    st.write(transcription)
                with c2:
                    st.markdown("### Censored Version")
                    st.write(filtered_text)

                st.markdown("### Cleaned Audio")
                st.audio(filtered_audio, format="audio/mp3")

                st.markdown("</div>", unsafe_allow_html=True)

                # Show detected bad words as badges
                st.markdown("### Detected Bad Words:")
                detected = list({
                    w for w in transcription.lower().split()
                    if any(bw in w for bw in bad_words)
                })
                if detected:
                    badges = " ".join(
                        f'<span class="censored-badge">{w[0]}{"*"*(len(w)-1)}</span>'
                        for w in detected[:10]
                    )
                    st.markdown(f'<div style="display:flex;flex-wrap:wrap;">{badges}</div>',
                                unsafe_allow_html=True)
                else:
                    st.success("No bad words detected! 👏")

    # ── Tab 1: About ──────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown(
            """
            ## About VulgarVeto

            **VulgarVeto** is your solution to clean up foul-mouthed audio! Whether you're
            preparing content for:

            - 👪 Family-friendly platforms
            - 🏫 Educational settings
            - 📱 Social media that restricts profanity
            - 🎭 Comedy that needs strategic bleeps

            ### How It Works
            1. 🎤 **Upload** — Provide an audio file in WAV format
            2. 🧠 **Process** — AI transcribes the audio and finds problematic words
            3. 🚫 **Censor** — Bad words are replaced with your chosen style
            4. 🔊 **Output** — Download a clean version ready for your audience!

            ### Censorship Styles
            - **Classic BEEP** — The traditional censorship sound
            - **Random** — Various unexpected replacements
            - **Dolphin** — Marine-themed censorship (🐬🐬🐬)
            - **Symbols** — Replaces words with symbols (#@$%!)
            """
        )

    # ── Tab 2: Settings ───────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown("## Settings")
        st.write("Customize your VulgarVeto experience:")

        st.selectbox(
            "TTS Voice",
            ["Standard Female", "Standard Male", "Robot", "Posh British", "Valley Girl"],
        )

        sensitivity = st.slider("Profanity Detection Sensitivity", 1, 10, 5)
        level = "Low" if sensitivity < 4 else ("High" if sensitivity > 7 else "Medium")
        st.caption(f"Current setting: {level} sensitivity")

        with st.expander("Advanced Options"):
            st.checkbox("Block mild profanity", value=True)
            st.checkbox("Block moderate profanity", value=True)
            st.checkbox("Block severe profanity", value=True)
            st.checkbox("Use AI-enhanced detection", value=True)
            st.checkbox("Keep original audio timing", value=False)

    # ── Sidebar ───────────────────────────────────────────────────────────────
    # FIX: replaced deprecated use_column_width with width parameter
    st.sidebar.image(
        "https://www.crazysocks.com/cdn/shop/articles/benefits-of-swearing_800x.png?v=1688849137",
        width=300,   # ← fixed deprecation warning
    )
    display_fun_facts()

    quotes = [
        '"Censorship is telling a man he can\'t have a steak just because a baby can\'t chew it." - Mark Twain',
        '"The first condition of progress is the removal of censorship." - George Bernard Shaw',
        '"Censorship reflects a society\'s lack of confidence in itself." - Potter Stewart',
        '"BEEP out of my way, I\'m trying to BEEP make a point here!" - Censored Comedian',
        '"To BEEP, or not to BEEP, that is the BEEP question." - William ShakesBEEP',
    ]
    st.sidebar.markdown("### 💭 **Quotable Quotes**")
    st.sidebar.markdown(f"*{random.choice(quotes)}*")

    # Footer
    st.markdown(
        """
        <div style="text-align:center;margin-top:50px;padding:20px;
                    background-color:rgba(0,0,0,0.5);border-radius:10px;">
            <p>Made with 🤐 by VulgarVeto Team</p>
            <p style="font-size:0.8em;">
                We believe in your right to be clean… and your right to be dirty, just not in public!
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
