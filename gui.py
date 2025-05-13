import tkinter as tk
from tkinter import filedialog, messagebox
from audio_io import read_audio, play_audio
from fir_filter import FIRFilter
import threading
import numpy as np

class AudioProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FIR 滤波器音频处理")
        self.file_path = None
        self.sample_rate = None
        self.audio_data = None
        self.filtered_audio = None
        self.fir_filter = None
        self.stop_event = threading.Event()  # 用于控制播放线程
        self.audio_data_lock = threading.Lock()  # 用于同步音频数据更新
        self.is_paused = True  # 标记当前是否暂停播放
        self.play_thread = None  # 保存播放线程
        self.current_position = 0  # 当前播放位置（样本索引）

        # 文件选择按钮
        tk.Button(root, text="选择音频文件", command=self.load_file).pack(pady=5)

        # 截止频率输入框
        self.cutoff_frame = tk.Frame(root)
        self.cutoff_frame.pack()
        self.low_cutoff_label = tk.Label(self.cutoff_frame, text="截止频率 (Hz):")
        self.low_cutoff_entry = tk.Entry(self.cutoff_frame)
        self.high_cutoff_label = tk.Label(self.cutoff_frame, text="高截止频率 (Hz):")
        self.high_cutoff_entry = tk.Entry(self.cutoff_frame)

        # 滤波器类型选择
        tk.Label(root, text="滤波器类型:").pack()
        self.filter_type = tk.StringVar(value="none")
        self.filter_type.trace_add("write", self.update_cutoff_inputs)  # 动态更新输入框
        tk.OptionMenu(root, self.filter_type, "none", "lowpass", "highpass", "bandpass", "bandstop").pack()

        # 应用滤波器按钮
        tk.Button(root, text="应用滤波器", command=self.apply_filter).pack(pady=5)

        # 播放按钮
        self.play_button = tk.Button(root, text="播放", command=self.toggle_play_pause)
        self.play_button.pack(pady=5)

        # 显示当前播放音频的标签
        self.current_file_label = tk.Label(root, text="当前播放：无", font=("Arial", 12))
        self.current_file_label.pack(pady=5)

    def load_file(self):
        """
        选择音频文件并加载音频数据。
        """
        self.file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.aac")])
        if self.file_path:
            try:
                self.sample_rate, self.audio_data, duration = read_audio(self.file_path)
                self.filtered_audio = self.audio_data
                self.fir_filter = FIRFilter(self.sample_rate)
                # 更新当前播放音频的标签
                self.current_file_label.config(text=f"当前播放：{self.file_path.split('/')[-1]}")
                messagebox.showinfo("成功", f"加载音频文件成功！时长: {duration:.2f} 秒")
            except Exception as e:
                messagebox.showerror("错误", f"无法加载音频文件: {e}")

    def get_filtered_audio(self):
        """
        获取当前滤波后的音频数据。
        """
        with self.audio_data_lock:
            return self.filtered_audio

    def apply_filter(self):
        """
        动态应用滤波器到音频数据。
        """
        if not self.fir_filter or self.audio_data is None:
            messagebox.showerror("错误", "请先加载音频文件")
            return

        filter_type = self.filter_type.get()
        try:
            if filter_type in ["lowpass", "highpass"]:
                # 检查单个截止频率输入
                cutoff = self.low_cutoff_entry.get()
                if not cutoff or not cutoff.isdigit() or float(cutoff) <= 0:
                    messagebox.showerror("错误", "请输入有效的截止频率 (Hz)")
                    return
                cutoff = float(cutoff)
                self.fir_filter.design_FIR_filter(filter_type, cutoff)
            elif filter_type in ["bandpass", "bandstop"]:
                # 检查两个截止频率输入
                low_cutoff = self.low_cutoff_entry.get()
                high_cutoff = self.high_cutoff_entry.get()
                if not low_cutoff or not high_cutoff or not low_cutoff.isdigit() or not high_cutoff.isdigit():
                    messagebox.showerror("错误", "请输入有效的截止频率 (Hz)")
                    return
                low_cutoff = float(low_cutoff)
                high_cutoff = float(high_cutoff)
                if low_cutoff <= 0 or high_cutoff <= 0 or low_cutoff >= high_cutoff:
                    messagebox.showerror("错误", "低截止频率必须小于高截止频率，且均为正值")
                    return
                self.fir_filter.design_FIR_filter(filter_type, [low_cutoff, high_cutoff])
            else:
                self.fir_filter.design_FIR_filter("none", None)

            # 动态更新滤波器应用到音频数据
            with self.audio_data_lock:
                self.filtered_audio = self.fir_filter.apply_filter(self.audio_data)
                self.filtered_audio = np.clip(self.filtered_audio, -32768, 32767).astype(np.int16)
            messagebox.showinfo("成功", "滤波器设置已动态应用")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的截止频率")

    def toggle_play_pause(self):
        """
        切换播放和暂停状态。
        """
        if self.filtered_audio is None:
            messagebox.showerror("错误", "请先加载音频文件并应用滤波器")
            return

        if self.is_paused:
            # 恢复播放
            self.is_paused = False
            self.stop_event.clear()
            self.play_button.config(text="暂停")
            if not self.play_thread or not self.play_thread.is_alive():
                self.play_thread = threading.Thread(target=self._play_audio_thread)
                self.play_thread.start()
        else:
            # 暂停播放
            self.is_paused = True
            self.stop_event.set()
            self.play_button.config(text="播放")

    def _play_audio_thread(self):
        """
        播放音频线程。
        """
        try:
            def get_audio_data():
                """
                动态获取滤波后的音频数据。
                """
                with self.audio_data_lock:
                    return self.filtered_audio

            # 更新当前播放音频的标签（确保在播放时显示）
            self.current_file_label.config(text=f"当前播放：{self.file_path.split('/')[-1]}")
            self.current_position = play_audio(self.sample_rate, get_audio_data, self.stop_event, self.current_position)
        except Exception as e:
            messagebox.showerror("错误", f"播放音频时出错: {e}")
        finally:
            self.stop_event.set()
            self.play_button.config(text="播放")

    def play_audio(self):
        """
        播放音频，支持动态更新。
        """
        if self.filtered_audio is None:
            messagebox.showerror("错误", "请先加载音频文件并应用滤波器")
            return

        self.stop_event.clear()
        threading.Thread(target=play_audio, args=(self.sample_rate, self.get_filtered_audio, self.stop_event)).start()

    def update_cutoff_inputs(self, *args):
        """
        根据滤波器类型动态更新截止频率输入框。
        """
        # 清除所有输入框
        self.low_cutoff_label.grid_forget()
        self.low_cutoff_entry.grid_forget()
        self.high_cutoff_label.grid_forget()
        self.high_cutoff_entry.grid_forget()

        filter_type = self.filter_type.get()
        if filter_type in ["lowpass", "highpass"]:
            # 显示单个截止频率输入框
            self.low_cutoff_label.config(text="截止频率 (Hz):")
            self.low_cutoff_label.grid(row=0, column=0)
            self.low_cutoff_entry.grid(row=0, column=1)
        elif filter_type in ["bandpass", "bandstop"]:
            # 显示两个截止频率输入框
            self.low_cutoff_label.config(text="低截止频率 (Hz):")
            self.low_cutoff_label.grid(row=0, column=0)
            self.low_cutoff_entry.grid(row=0, column=1)
            self.high_cutoff_label.config(text="高截止频率 (Hz):")
            self.high_cutoff_label.grid(row=1, column=0)
            self.high_cutoff_entry.grid(row=1, column=1)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioProcessingApp(root)
    root.mainloop()
