import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av
import cv2
from pyzbar.pyzbar import decode

st.title("QRコード読み取り（Android対応）")

# QRコード読み取りクラス
class QRReader(VideoTransformerBase):
    def __init__(self):
        self.last_text = None

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # QRコード解析
        decoded = decode(img)
        if decoded:
            self.last_text = decoded[0].data.decode("utf-8")

        return img

# カメラ起動
ctx = webrtc_streamer(
    key="qr-reader",
    video_processor_factory=QRReader,
    media_stream_constraints={"video": True, "audio": False},
)

# 読み取った QR の内容を表示
if ctx.video_processor:
    qr_text = ctx.video_processor.last_text
    if qr_text:
        st.success(f"読み取ったQRコード: {qr_text}")
