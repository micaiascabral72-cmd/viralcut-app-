import os
import tempfile
import requests
import streamlit as st
import numpy as np
from PIL import Image, ImageEnhance

# Compatibilidade com MoviePy v1 e v2
try:
    from moviepy.editor import VideoFileClip, vfx
except ImportError:
    from moviepy import VideoFileClip, vfx

# Configuração da página para celular
st.set_page_config(
    page_title="ViralCut - Anti-Flop HD",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 ViralCut - Edição & Anti-Flop")
st.caption("Processe vídeos mantendo legendas nítidas e qualidade HD.")

# ---------------------------------------------------------
# FUNÇÃO: Download Limpo do TikTok (TikWM)
# ---------------------------------------------------------
def baixar_tiktok_sem_marca(url):
    api_url = "https://www.tikwm.com/api/"
    params = {"url": url, "hd": 1}
    response = requests.get(api_url, params=params, timeout=15)
    data = response.json()
    
    if data.get("code") == 0:
        video_url = data["data"].get("hdplay") or data["data"].get("play")
        return requests.get(video_url).content
    else:
        raise Exception("Não foi possível baixar o vídeo. Verifique se a conta/vídeo é pública.")

# ---------------------------------------------------------
# FUNÇÃO: Processamento de Vídeo Otimizado
# ---------------------------------------------------------
def processar_video(input_path, output_path, crop_percent, speed_factor, flip_video, boost_quality):
    clip = VideoFileClip(input_path)
    
    # 1. Crop Leve (Apenas para ajustar bordas sem cortar textos)
    if crop_percent > 0:
        w, h = clip.size
        crop_x = int(w * (crop_percent / 100))
        crop_y = int(h * (crop_percent / 100))
        clip = clip.crop(x1=crop_x, y1=crop_y, x2=w-crop_x, y2=h-crop_y)

    # 2. Alteração de Velocidade Sutil (Anti-Flop)
    if speed_factor != 1.0:
        clip = clip.fx(vfx.speedx, speed_factor)

    # 3. Espelhar apenas se selecionado (desativado por padrão para vídeos com texto)
    if flip_video:
        clip = clip.fx(vfx.mirror_x)

    # 4. Ajuste Suave de Contraste/Nitidez (Sem estourar a imagem)
    if boost_quality:
        def otimizar_frame(frame):
            img = Image.fromarray(frame)
            # Melhora suave de contraste e nitidez
            img = ImageEnhance.Contrast(img).enhance(1.08)
            img = ImageEnhance.Sharpness(img).enhance(1.10)
            return np.array(img)
        
        clip = clip.fl_image(otimizar_frame)

    # Exportação em Alta Definição
    clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        bitrate="6000k",
        preset="fast"
    )
    clip.close()

# ---------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["🔗 Link do TikTok", "📁 Upload do Celular"])

with tab1:
    tiktok_url = st.text_input("Cole o link do TikTok:")
    if st.button("Baixar Vídeo", type="primary"):
        if tiktok_url:
            with st.spinner("Baixando em HD sem marca d'água..."):
                try:
                    video_bytes = baixar_tiktok_sem_marca(tiktok_url)
                    temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                    temp_in.write(video_bytes)
                    temp_in.close()
                    st.session_state["video_path"] = temp_in.name
                    st.success("Vídeo carregado com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")

with tab2:
    uploaded_file = st.file_uploader("Envie um vídeo da galeria:", type=["mp4", "mov"])
    if uploaded_file is not None:
        temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_in.write(uploaded_file.read())
        temp_in.close()
        st.session_state["video_path"] = temp_in.name
        st.success("Arquivo carregado!")

if "video_path" in st.session_state and os.path.exists(st.session_state["video_path"]):
    st.divider()
    st.subheader("⚙️ Opções de Otimização")
    
    col1, col2 = st.columns(2)
    with col1:
        crop_val = st.slider("Corte das Bordas (%):", 0, 5, 1, help="Evite valores altos se o vídeo tiver legendas nas bordas.")
        speed_val = st.slider("Velocidade:", 0.98, 1.05, 1.02, step=0.01)
    
    with col2:
        #value=False garante que textos e legendas NÃO fiquem ao contrário
        flip_val = st.checkbox("Espelhar Vídeo (Apenas p/ vídeos SEM texto)", value=False)
        boost_val = st.checkbox("Melhorar Nitidez HD", value=True)

    if st.button("🚀 Processar Vídeo HD", type="primary", use_container_width=True):
        with st.spinner("Processando..."):
            temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            try:
                processar_video(
                    st.session_state["video_path"],
                    temp_out,
                    crop_val,
                    speed_val,
                    flip_val,
                    boost_val
                )
                
                st.video(temp_out)
                
                with open(temp_out, "rb") as file:
                    st.download_button(
                        label="📥 BAIXAR VÍDEO PRONTO EM HD",
                        data=file,
                        file_name="video_viral_hd.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
            except Exception as err:
                st.error(f"Erro no processamento: {err}")
