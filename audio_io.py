import wave
import pyaudio
from pydub import AudioSegment
import numpy as np

def read_audio(file_path):
    """
    读取音频文件，支持 WAV、MP3 和 AAC 格式。
    返回采样率、音频数据（numpy 数组）和时长（秒）。
    """
    if file_path.endswith(".wav"):
        with wave.open(file_path, 'rb') as wf:
            sample_rate = wf.getframerate()
            n_channels = wf.getnchannels()
            n_frames = wf.getnframes()
            audio_data = wf.readframes(n_frames)
            audio_data = np.frombuffer(audio_data, dtype=np.int16)
            if n_channels > 1:
                audio_data = audio_data.reshape(-1, n_channels)[:, 0]  # 转为单声道
            duration = n_frames / sample_rate
        return sample_rate, audio_data, duration
    elif file_path.endswith((".mp3", ".aac")):
        audio = AudioSegment.from_file(file_path)
        sample_rate = audio.frame_rate
        audio_data = np.array(audio.get_array_of_samples())
        if audio.channels > 1:
            audio_data = audio_data.reshape(-1, audio.channels)[:, 0]  # 转为单声道
        duration = len(audio) / 1000  # 转换为秒
        return sample_rate, audio_data, duration
    else:
        raise ValueError("Unsupported file format. Only WAV, MP3, and AAC are supported.")

def play_audio(sample_rate, get_audio_data, stop_event, start_position):
    """
    播放音频数据，支持动态更新和从指定位置继续播放。
    :param sample_rate: 采样率
    :param get_audio_data: 函数，用于动态获取最新的音频数据
    :param stop_event: threading.Event，用于控制停止播放
    :param start_position: 开始播放的位置（样本索引）
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    output=True)

    chunk_size = 1024
    position = start_position

    try:
        while not stop_event.is_set():
            audio_data = get_audio_data()  # 动态获取最新的音频数据
            for i in range(position, len(audio_data), chunk_size):
                if stop_event.is_set():
                    position = i  # 保存当前播放位置
                    break

                chunk = audio_data[i:i + chunk_size]
                chunk = np.clip(chunk, -32768, 32767).astype(np.int16)

                if len(chunk) == 0:
                    break

                stream.write(chunk.tobytes())
            else:
                position = 0  # 播放结束后重置位置
                break
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    return position  # 返回当前播放位置
