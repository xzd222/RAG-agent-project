"""
知识库管理页面 - Streamlit 实现

功能:
- 上传 txt/pdf 文件
- 查看已入库文件列表及状态
- 展示文件前 200 字预览
- 手动触发重新入库
- 删除文件
"""

import os
import time

import streamlit as st

from rag.vector_store import VectorStoreService
from utils.file_handler import get_file_md5_hex
from utils.path_tool import get_abs_path

st.set_page_config(page_title="知识库管理", page_icon="📚", layout="wide")
st.title("📚 知识库管理")
st.divider()


@st.cache_resource
def get_vs():
    return VectorStoreService()


@st.cache_data(ttl=5)
def load_ingested_md5s() -> set[str]:
    md5_path = get_abs_path("md5.text")
    if not os.path.exists(md5_path):
        return set()
    with open(md5_path, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


@st.cache_data(ttl=5)
def scan_data_dir() -> list[dict]:
    data_path = get_abs_path("data")
    if not os.path.isdir(data_path):
        return []

    allowed = (".txt", ".pdf")
    ingested = load_ingested_md5s()
    result = []

    for filename in os.listdir(data_path):
        filepath = os.path.join(data_path, filename)
        if not os.path.isfile(filepath):
            continue
        if not filename.endswith(allowed):
            continue
        md5 = get_file_md5_hex(filepath)
        preview = ""
        if filename.endswith(".txt"):
            try:
                with open(filepath, "r", encoding="utf-8") as pf:
                    text = pf.read(200)
                    preview = text[:200] + ("…" if len(text) > 200 else "")
            except Exception:
                preview = "(无法预览)"

        result.append({
            "filename": filename,
            "md5": md5 or "N/A",
            "ingested": md5 in ingested if md5 else False,
            "size_kb": round(os.path.getsize(filepath) / 1024, 1),
            "preview": preview,
        })

    return sorted(result, key=lambda x: x["filename"])


# ── 防止重复上传 ─────────────────────────────────────────────
if "uploaded_fingerprints" not in st.session_state:
    st.session_state.uploaded_fingerprints: set[str] = set()


def do_ingest():
    with st.spinner("正在入库…"):
        try:
            get_vs().load_document()
            load_ingested_md5s.clear()
            scan_data_dir.clear()
        except Exception as e:
            st.error(f"入库失败: {e}")


# ── 侧边栏 ───────────────────────────────────────────────────

with st.sidebar:
    st.subheader("操作")

    if st.button("🔄 重新入库", use_container_width=True):
        do_ingest()
        st.success("入库完成！")
        time.sleep(0.5)
        st.rerun()

    st.divider()
    st.caption("支持格式: .txt / .pdf")
    st.caption("文件存入项目 `data/` 目录")

# ── 上传 ─────────────────────────────────────────────────────

st.subheader("上传文件")

uploaded = st.file_uploader(
    "选择 txt 或 pdf 文件",
    type=["txt", "pdf"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    key="file_uploader",
)

if uploaded:
    data_dir = get_abs_path("data")
    os.makedirs(data_dir, exist_ok=True)

    new_files = []
    for f in uploaded:
        fingerprint = f"{f.name}-{f.size}"
        if fingerprint in st.session_state.uploaded_fingerprints:
            continue
        st.session_state.uploaded_fingerprints.add(fingerprint)
        save_path = os.path.join(data_dir, f.name)
        with open(save_path, "wb") as wf:
            wf.write(f.getbuffer())
        new_files.append(f.name)

    if new_files:
        st.toast(f"✅ 已保存: {', '.join(new_files)}")
        do_ingest()
        st.success("入库完成！")
        time.sleep(0.5)
        st.rerun()

# ── 文件列表 ─────────────────────────────────────────────────

st.subheader("文件列表")

files = scan_data_dir()

if not files:
    st.info("暂无文件，请上传 txt 或 pdf 文件。")
else:
    for f in files:
        col1, col2, col3, col4 = st.columns([2.5, 1, 1, 0.8])

        with col1:
            icon = "📄" if f["filename"].endswith(".txt") else "📕"
            st.write(f"{icon} **{f['filename']}**")
            if f["preview"]:
                with st.expander("预览"):
                    st.write(f["preview"])

        with col2:
            st.caption(f"{f['size_kb']} KB")

        with col3:
            st.badge("已入库", color="green") if f["ingested"] else st.badge("未入库", color="orange")

        with col4:
            if st.button("🗑️", key=f"del_{f['filename']}", help=f"删除 {f['filename']}"):
                try:
                    os.remove(os.path.join(get_abs_path("data"), f["filename"]))
                    scan_data_dir.clear()
                    st.toast(f"已删除 {f['filename']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"删除失败: {e}")

        # MD5
        st.caption(f"MD5: `{f['md5'][:16]}…`")
        st.divider()
