import os
import tempfile
import requests
import streamlit as st
from moviepy.editor import VideoFileClip, vfx
import moviepy.video.fx.all as vfx_all
from PIL import Image, ImageEnhance

# Configuração da página para celular
st.set_page_config(
    page_title="ViralCut - Anti-Flop & Edição Automática",
    page_icon="🚀",
    layout="centered"
)

st.title("🚀 ViralCut - Gerador de Vídeos Anti-Flop")
st.caption("Transforme qualquer vídeo do TikTok em conteúdo inédito em HD para o algoritmo.")

# ---------------------------------------------------------
# FUNÇÃO 1: Download Limpo sem Marca d'Água (API TikWM)
# ---------------------------------------------------------
def baixar_tiktok_sem_marca(url):
    api_url = "https://www.tikwm.com/api/"
    params = {"url": url, "hd": 1}
    response = requests.get(api_url, params=params, timeout=15)
    data = response.json()
    
    if data.get("code") == 0:
        # Puxa o link direto em HD sem marca d'água
        video_url = data["data"].get("hdplay") or data["data"].get("play")
        video_bytes = requests.get(video_url).content
        return video_bytes
    else:
        raise Exception("Não foi possível extrair o vídeo. Verifique se o link é público.")

# ---------------------------------------------------------
# FUNÇÃO 2: Processamento Anti-Flop do Vídeo
# ---------------------------------------------------------
def processar_video_antiflop(input_path, output_path, crop_percent, speed_factor, flip_video, boost_quality):
    clip = VideoFileClip(input_path)
    
    # 1. Crop Inteligente (Corta bordas para remover nomes de perfil e logos)
    if crop_percent > 0:
        w, h = clip.size
        crop_x = int(w * (crop_percent / 100))
        crop_y = int(h * (crop_percent / 100))
        clip = clip.crop(x1=crop_x, y1=crop_y, x2=w-crop_x, y2=h-crop_y)

    # 2. Alteração de Velocidade (Engana o leitor de tempo do algoritmo)
    if speed_factor != 1.0:
        clip = clip.fx(vfx.speedx, speed_factor)

    # 3. Inversão Espelhada (Muda o mapeamento de pixels)
    if flip_video:
        clip = clip.fx(vfx.mirror_x)

    # 4. Ajuste de Nitidez / Contraste (Efeito HD/4K)
    if boost_quality:
        def otimizar_frame(frame):
            img = Image.fromarray(frame)
            # Aumenta contraste e nitidez
            img = ImageEnhance.Contrast(img).enhance(1.15)
            img = ImageEnhance.Sharpness(img).enhance(1.20)
            return np.array(img)
        
        import numpy as np
        clip = clip.fl_image(otimizar_frame)

    # Exportação com bitrate alto para manter qualidade de imagem
    clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        bitrate="5000k",
        preset="ultrafast",
        threads=4
    )
    clip.close()

# ---------------------------------------------------------
# INTERFACE DO USUÁRIO (STREAMLIT)
# ---------------------------------------------------------
tab1, tab2 = st.tabs(["🔗 Link do TikTok", "📁 Upload de Arquivo"])
video_source_path = None

with tab1:
    tiktok_url = st.text_input("Cole o link do vídeo do TikTok:")
    if st.button("Puxar Vídeo do TikTok", type="primary"):
        if tiktok_url:
            with st.spinner("Baixando vídeo sem marca d'água em HD..."):
                try:
                    video_bytes = baixar_tiktok_sem_marca(tiktok_url)
                    temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                    temp_in.write(video_bytes)
                    temp_in.close()
                    st.session_state["video_path"] = temp_in.name
                    st.success("Vídeo baixado sem marca d'água!")
                except Exception as e:
                    st.error(f"Erro ao baixar: {e}")
        else:
            st.warning("Insira uma URL válida.")

with tab2:
    uploaded_file = st.file_uploader("Envie um vídeo da galeria do celular:", type=["mp4", "mov"])
    if uploaded_file is not None:
        temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_in.write(uploaded_file.read())
        temp_in.close()
        st.session_state["video_path"] = temp_in.name
        st.success("Arquivo carregado com sucesso!")

# Se houver vídeo pronto para edição
if "video_path" in st.session_state and os.path.exists(st.session_state["video_path"]):
    st.divider()
    st.subheader("⚙️ Configurações Anti-Flop & Edição")
    
    col1, col2 = st.columns(2)
    with col1:
        crop_val = st.slider("Corte das Bordas (Crop %):", 0, 10, 3, help="Remove nomes de perfis nas bordas.")
        speed_val = st.slider("Velocidade do Vídeo:", 0.95, 1.10, 1.04, step=0.01, help="Muda o HASH do arquivo.")
    
    with col2:
        flip_val = st.checkbox("Espelhar Vídeo (Flip Horizontal)", value=True)
        boost_val = st.checkbox("Melhorar Nitidez / Modo HD", value=True)

    if st.button("🚀 Processar Vídeo Anti-Flop", type="primary", use_container_width=True):
        with st.spinner("Aplicando engenharia anti-flop e exportando..."):
            temp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            try:
                processar_video_antiflop(
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
                        label="📥 BAIXAR VÍDEO PRONTO PARA VIRALIZAR",
                        data=file,
                        file_name="video_viral_antiflop.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )
            except Exception as err:
                st.error(f"Erro durante o processamento: {err}")

st.divider()
st.info("💡 **Dica VIP:** Quer liberar acessos ilimitados e novos filtros? Adquira o plano pelo nosso Bot do Telegram.")
