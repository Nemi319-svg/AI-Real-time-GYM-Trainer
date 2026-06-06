import os
import base64
import streamlit as st
import streamlit.components.v1 as components


def load_css(file_path):
    """Load local CSS file"""
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )


def inject_local_font(font_path, font_name="AdobeClean"):
    """Inject local font into Streamlit"""
    if not os.path.exists(font_path):
        return

    with open(font_path, "rb") as f:
        encoded_font = base64.b64encode(f.read()).decode()

    ext = os.path.splitext(font_path)[1].lower()

    format_map = {
        ".otf": "opentype",
        ".ttf": "truetype",
        ".woff": "woff",
        ".woff2": "woff2"
    }

    mime_map = {
        ".otf": "font/otf",
        ".ttf": "font/ttf",
        ".woff": "font/woff",
        ".woff2": "font/woff2"
    }

    st.markdown(
        f"""
        <style>
        @font-face {{
            font-family: '{font_name}';
            src: url(data:{mime_map.get(ext,'font/otf')};base64,{encoded_font})
                 format('{format_map.get(ext,'opentype')}');
        }}

        html, body, [class*="css"] {{
            font-family: '{font_name}', sans-serif;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_webrtc_styles():
    """Patch streamlit-webrtc iframe styles"""

    font_path = os.path.join(os.getcwd(), "static", "AdobeClean.otf")

    if not os.path.exists(font_path):
        return

    with open(font_path, "rb") as font_file:
        encoded_font = base64.b64encode(font_file.read()).decode()

    components.html(
        f"""
        <script>
        (function() {{

            function injectIntoIframe(iframe) {{
                try {{
                    const doc =
                        iframe.contentDocument ||
                        iframe.contentWindow.document;

                    if (!doc || !doc.head) return;

                    if (doc.getElementById("webrtc-custom-style"))
                        return;

                    const style = doc.createElement("style");
                    style.id = "webrtc-custom-style";

                    style.textContent = `
                        @font-face {{
                            font-family: 'AdobeClean';
                            src: url('data:font/otf;base64,{encoded_font}')
                                 format('opentype');
                        }}

                        .MuiButtonBase-root,
                        .MuiButton-root,
                        .MuiButton-contained,
                        .MuiButton-text {{
                            border-radius: 0 !important;
                            font-family: AdobeClean, sans-serif !important;
                            letter-spacing: 0.05em !important;
                        }}
                    `;

                    doc.head.appendChild(style);

                }} catch(err) {{
                    console.log(err);
                }}
            }}

            function patch() {{
                const iframes =
                    window.parent.document.querySelectorAll("iframe");

                iframes.forEach((iframe) => {{
                    if (
                        iframe.src &&
                        iframe.src.includes("webrtc")
                    ) {{
                        injectIntoIframe(iframe);
                    }}
                }});
            }}

            setTimeout(patch, 1000);

        }})();
        </script>
        """,
        height=0,
    )