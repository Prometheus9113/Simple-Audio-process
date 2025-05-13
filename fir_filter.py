import numpy as np
from scipy.signal import firwin, lfilter

class FIRFilter:
    def __init__(self, sample_rate):
        self.sample_rate = sample_rate
        self.filter_type = "none"
        self.cutoff = None
        self.num_taps = 1024
        self.filter_coeffs = None

    def design_filter(self, filter_type, cutoff):
        """
        设计 FIR 滤波器。
        :param filter_type: 滤波器类型 ('lowpass', 'highpass', 'bandpass', 'bandstop', 'none')
        :param cutoff: 截止频率（Hz），单值或范围
        """
        self.filter_type = filter_type
        self.cutoff = cutoff

        if filter_type == "none":
            self.filter_coeffs = None
            return

        nyquist = self.sample_rate / 2
        if isinstance(cutoff, (list, tuple)):
            normalized_cutoff = [f / nyquist for f in cutoff]
        else:
            normalized_cutoff = cutoff / nyquist

        if filter_type == "lowpass":
            pass_zero_self = True
        elif filter_type == "highpass":
            pass_zero_self = False
        elif filter_type == "bandpass":
            pass_zero_self = False
        elif filter_type == "bandstop":
            pass_zero_self = True
        else:
            raise ValueError(f"Unsupported filter type: {filter_type}")

        # 修复高通和带阻滤波器设计时可能的错误
        if isinstance(normalized_cutoff, list):
            if any(c <= 0 or c >= 1 for c in normalized_cutoff):
                raise ValueError("Normalized cutoff frequencies must be between 0 and 1.")
        else:
            if normalized_cutoff <= 0 or normalized_cutoff >= 1:
                raise ValueError("Normalized cutoff frequency must be between 0 and 1.")

        self.filter_coeffs = firwin(self.num_taps+1, normalized_cutoff, pass_zero=pass_zero_self)

    def apply_filter(self, audio_data):
        """
        应用 FIR 滤波器。
        :param audio_data: 输入音频数据（numpy 数组）
        :return: 滤波后的音频数据
        """
        if self.filter_coeffs is None:
            return audio_data
        return lfilter(self.filter_coeffs, 1.0, audio_data)
