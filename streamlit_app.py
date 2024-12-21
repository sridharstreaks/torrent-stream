import libtorrent as lt
import time
import os
import streamlit as st
from streamlit_webrtc import WebRtcStreamerContext, webrtc_streamer

def download_torrent(torrent_path, save_path, file_index=0):
    ses = lt.session()
    ses.listen_on(6881, 6891)

    info = lt.torrent_info(torrent_path)
    h = ses.add_torrent({'ti': info, 'save_path': save_path})

    file_handle = h.torrent_file().files()
    file_name = file_handle.file_path(file_index)
    file_path = os.path.join(save_path, file_name)

    print(f'Starting download of {torrent_path}...')
    while not h.is_seed():
        s = h.status()
        print(f'Downloading: {s.progress * 100:.2f}% complete (down: {s.download_rate / 1000:.1f} kB/s up: {s.upload_rate / 1000:.1f} kB/s peers: {s.num_peers})')
        time.sleep(1)

        # Check if the file has enough pieces to start streaming
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            break

    return file_path

def stream_video(file_path):
    def video_frame_callback(frame):
        with open(file_path, 'rb') as f:
            video_data = f.read()
        frame.from_ndarray(video_data, format="bgr24")
        return frame

    webrtc_streamer(key="example", video_frame_callback=video_frame_callback)

def main():
    st.title("Torrent Video Streamer")

    torrent_file = st.text_input("Enter the path to the torrent file:")
    save_path = st.text_input("Enter the path to save the downloaded video:")

    if st.button("Start Download and Stream"):
        if not torrent_file or not save_path:
            st.error("Please provide both torrent file path and save path.")
        else:
            video_file = download_torrent(torrent_file, save_path)
            if video_file:
                st.success("Download started. Streaming video...")
                stream_video(video_file)
            else:
                st.error("No video file found in the torrent.")

if __name__ == "__main__":
    main()
