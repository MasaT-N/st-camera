import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
import av
import cv2
from pyzbar.pyzbar import decode

st.title("QRコード読み取り（Android対応）")
st.write("カメラをQRコードに向けてください。映像内に緑色の枠と内容が表示されます。")

# WebRTCの設定（STUNサーバーを追加して接続性を向上）
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# QRコード読み取りクラス
class QRReader(VideoProcessorBase):
    def __init__(self):
        self.last_text = None

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # QRコード解析
        decoded = decode(img)
        for obj in decoded:
            # QRコードのデータを抽出
            self.last_text = obj.data.decode("utf-8")
            
            # 映像内に枠を描画
            (x, y, w, h) = obj.rect
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 映像内に解析したテキストを描画
            cv2.putText(img, self.last_text, (x, y - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

# カメラ起動
ctx = webrtc_streamer(
    key="qr-reader",
    video_processor_factory=QRReader,
    rtc_configuration=RTC_CONFIGURATION,
    # 背面カメラを優先的に使用する設定
    media_stream_constraints={"video": {"facingMode": "environment"}, "audio": False},
    async_processing=True,
)

# 読み取った QR の内容を表示
if ctx.video_processor:
    if st.button("結果をテキストで確定表示"):
        st.write("現在の読み取り内容:")
    qr_text = ctx.video_processor.last_text
    if qr_text:
        st.success(f"読み取ったQRコード: {qr_text}")
