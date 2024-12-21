import streamlit as st
import libtorrent as lt
import time
import os

# Set up a directory for temporary storage
temp_dir = "temp_video"
os.makedirs(temp_dir, exist_ok=True)

def download_torrent(magnet_link, save_path):
    """Download a torrent file using libtorrent."""
    ses = lt.session()
    ses.apply_settings({'listen_interfaces': '0.0.0.0:6881,[::]:6881'})

    params = lt.add_torrent_params()
    params.save_path = save_path
    params.storage_mode = lt.storage_mode_t(2)
    params.url = magnet_link

    handle = ses.add_torrent(params)

    st.write("Downloading Metadata...")
    while not handle.status().has_metadata:
        time.sleep(1)
    st.write("Metadata Imported, Starting Download...")

    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        state_str = [
            "queued", "checking", "downloading metadata", "downloading", "finished",
            "seeding", "allocating", "checking fastresume"
        ]
        progress_info = (
            f"{s.progress * 100:.2f}% complete (down: {s.download_rate / 1000:.1f} kB/s, "
            f"up: {s.upload_rate / 1000:.1f} kB/s, peers: {s.num_peers}) {state_str[s.state]}"
        )
        st.write(progress_info)
        time.sleep(5)

    st.success("Download Complete!")
    return os.path.join(save_path, handle.name())

# Streamlit UI
st.title("Torrent Video Downloader")

magnet_link = st.text_input("Enter Magnet Link:")
if magnet_link:
    if st.button("Start Download"):
        st.write("Starting download...")
        downloaded_file_path = download_torrent(magnet_link, temp_dir)

        if os.path.exists(downloaded_file_path):
            st.success("File downloaded successfully!")

            # Provide a download button
            with open(downloaded_file_path, "rb") as f:
                video_data = f.read()

            st.download_button(
                label="Download Video",
                data=video_data,
                file_name=os.path.basename(downloaded_file_path),
                mime="video/mp4"  # Adjust MIME type based on file type
            )

# Optional cleanup button to remove temporary files
if st.button("Clear Temporary Files"):
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    st.success("Temporary files cleared.")
