import streamlit as st
import requests
from pathlib import Path
import os
import uuid
import random

API_BASE = "http://127.0.0.1:8000"

# --- UI setup ---
st.set_page_config(page_title="NewsSite", layout="wide")
st.markdown("<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} </style>", unsafe_allow_html=True)
st.title("")

# --- session state ---
if "page" not in st.session_state:
    st.session_state["page"] = "all"
if "post_id" not in st.session_state:
    st.session_state["post_id"] = None
if "rerun" not in st.session_state:
    st.session_state["rerun"] = False
# --- form session state defaults ---
for key in [
    "first_name", "last_name", "post_title", "post_content", "img_url_input",
    "c_first", "c_last", "c_text"
]:
    if key not in st.session_state:
        st.session_state[key] = ""


def trigger_rerun():
    st.session_state["rerun"] = not st.session_state["rerun"]

# --- directories ---
BASE_DIR = Path(__file__).resolve().parent
UPLOADS = BASE_DIR / "uploads"
MEMES = BASE_DIR / "memes"
os.makedirs(UPLOADS, exist_ok=True)
os.makedirs(MEMES, exist_ok=True)

# --- top centered buttons ---
cols = st.columns([1,1,1,6,1,1,1])
with cols[3]:
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        if st.button("➕", help="Create Post"):
            st.session_state["page"] = "create"
    with c2:
        if st.button("📰", help="All Posts"):
            st.session_state["page"] = "all"
    with c3:
        if st.button("🙂", help="Random Meme"):
            st.session_state["page"] = "meme"

st.markdown("---")

# ------------------ PAGES ------------------

def page_all():
    st.header("All Posts")
    try:
        r = requests.get(f"{API_BASE}/posts", timeout=5)
        r.raise_for_status()
        posts = r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Cannot load posts. Is backend running? {e}")
        return

    if not posts:
        st.info("No posts yet. Create first post.")
        return

    for p in posts:
        st.markdown("### " + p["title"])
        if st.button("View Post", key=f"btn_{p['id']}"):
            st.session_state["page"] = "post"
            st.session_state["post_id"] = p["id"]

        cols = st.columns([0.3, 0.7])
        with cols[0]:
            if p.get("image_url"):
                try:
                    st.image(p["image_url"], width=150, use_container_width=False)
                except:
                    st.image(p["image_url"], width=150, use_container_width=False)
        with cols[1]:
            st.write(f"**Date:** {p.get('created_at','')}")
            st.write(f"👍 Likes: {p.get('likes',0)}")
        st.markdown("---")

def page_create():
    st.header("Create Post")
    first = st.text_input("First name", key="first_name")
    last = st.text_input("Last name", key="last_name")
    title = st.text_input("Title", key="post_title")
    content = st.text_area("Content", key="post_content")
    uploaded = st.file_uploader("Upload header image (optional)", type=["png","jpg","jpeg","webp"])
    img_url_input = st.text_input("Or paste image URL (optional)", key="img_url_input")

    saved_path = None
    if uploaded is not None:
        ext = Path(uploaded.name).suffix
        fname = f"{uuid.uuid4().hex}{ext}"
        save_path = UPLOADS / fname
        with open(save_path, "wb") as f:
            f.write(uploaded.getbuffer())
        saved_path = str(save_path)

    final_image = saved_path or (img_url_input.strip() if img_url_input.strip() else None)

    if st.button("Create Post"):
        if not first.strip() or not last.strip() or not title.strip() or not content.strip():
            st.warning("Please fill first name, last name, title and content.")
        else:
            payload = {
                "author": f"{first.strip()} {last.strip()}",
                "title": title.strip(),
                "content": content.strip(),
                "image_url": final_image
            }
            try:
                r = requests.post(f"{API_BASE}/posts", json=payload, timeout=5)
                r.raise_for_status()
                st.success("Post created!")

                st.session_state.pop("first_name", None)
                st.session_state.pop("last_name", None)
                st.session_state.pop("post_title", None)
                st.session_state.pop("post_content", None)
                st.session_state.pop("img_url_input", None)
                st.rerun()


                trigger_rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to create post: {e}")


def page_post():
    post_id = st.session_state.get("post_id")
    if not post_id:
        st.info("No post selected.")
        return

    try:
        rp = requests.get(f"{API_BASE}/posts/{post_id}", timeout=5)
        rp.raise_for_status()
        post = rp.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Cannot load post: {e}")
        return

    cols = st.columns([0.4, 0.6])
    with cols[0]:
        if post.get("image_url"):
            try:
                st.image(post["image_url"], width=250, use_container_width=False)
            except:
                st.image(post["image_url"], width=250, use_container_width=False)
    with cols[1]:
        st.markdown(f"### {post['title']}")
        st.write(f"Author: **{post['author']}**")
        st.write(f"Created: {post['created_at']}")
        st.write(post["content"])
        # like button
        if st.button(f"👍 {post.get('likes',0)}", key=f"post_like_{post_id}"):
            try:
                requests.post(f"{API_BASE}/posts/{post_id}/like")
                trigger_rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Like failed: {e}")

    st.markdown("---")

    # comments
    st.subheader("Comments")
    try:
        rc = requests.get(f"{API_BASE}/posts/{post_id}/comments", timeout=5)
        rc.raise_for_status()
        comments = rc.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Cannot load comments: {e}")
        comments = []

    for c in comments:
        st.write(f"**{c['author']}** — {c['created_at']}")
        st.write(c["content"])
        c_cols = st.columns([0.15, 0.85])
        with c_cols[0]:
            if st.button(f"👍 {c['likes']}", key=f"like_c_{c['id']}"):
                try:
                    requests.post(f"{API_BASE}/comments/{c['id']}/like")
                    trigger_rerun()
                except requests.exceptions.RequestException as e:
                    st.error(f"Like failed: {e}")
        st.markdown("---")

    # add comment
    st.subheader("Add comment")
    first = st.text_input("First name", key="c_first")
    last = st.text_input("Last name", key="c_last")
    cont = st.text_area("Comment", key="c_text")

    if st.button("Post comment"):
        if not first.strip() or not last.strip() or not cont.strip():
            st.warning("Fill all fields")
        else:
            author = f"{first.strip()} {last.strip()}"
            payload = {"author": author, "content": cont.strip()}

            try:
                r = requests.post(f"{API_BASE}/posts/{post_id}/comments", json=payload, timeout=5)
                r.raise_for_status()
                st.success("Comment posted")
                st.session_state.pop("c_first", None)
                st.session_state.pop("c_last", None)
                st.session_state.pop("c_text", None)
                st.rerun()

                trigger_rerun()
            except requests.exceptions.RequestException as e:
                try:
                    st.error(f"Failed to post comment: {r.status_code} {r.text}")
                except:
                    st.error(f"Failed to post comment: {e}")

def page_meme():
    st.header("Random Meme")
    files = list(MEMES.glob("*"))
    if not files:
        st.info("No memes found. Put images into frontend/memes/")
        return
    img = random.choice(files)
    st.image(str(img), use_container_width=True)
    if st.button("Next meme"):
        trigger_rerun()

# --- render ---
if st.session_state["page"] == "all":
    page_all()
elif st.session_state["page"] == "create":
    page_create()
elif st.session_state["page"] == "post":
    page_post()
elif st.session_state["page"] == "meme":
    page_meme()
