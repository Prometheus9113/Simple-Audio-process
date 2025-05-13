from scipy.signal import firwin, lfilter, iirfilter, sosfilt

class Filter:
    def __init__(self, sample_rate, type_of_filter):
        self.type = type_of_filter
        self.sample_rate = sample_rate
        self.filter_type = "none"
        self.cutoff = None
        self.fir_num_taps = 1024
        self.iir_num_taps = 17
        self.filter_coeffs = None

    def design_FIR_filter(self, filter_type, cutoff):
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

        self.filter_coeffs = firwin(self.fir_num_taps+1, normalized_cutoff, pass_zero=pass_zero_self)

    def apply_fir_filter(self, audio_data):
        """
        应用 FIR 滤波器。
        :param audio_data: 输入音频数据（numpy 数组）
        :return: 滤波后的音频数据
        """
        if self.filter_coeffs is None:
            return audio_data
        return lfilter(self.filter_coeffs, 1.0, audio_data)
    
    """
    IIR 滤波器设计
    
    """

    def design_IIR_filter(self, filter_type, cutoff):
        """
        设计 IIR 滤波器。
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

        if isinstance(normalized_cutoff, list):
            if any(c <= 0 or c >= 1 for c in normalized_cutoff):
                raise ValueError("Normalized cutoff frequencies must be between 0 and 1.")
        else:
            if normalized_cutoff <= 0 or normalized_cutoff >= 1:
                raise ValueError("Normalized cutoff frequency must be between 0 and 1.")
        pass

        self.filter_coeffs = iirfilter(self.iir_num_taps, cutoff ,rs=80, btype=filter_type, ftype='cheby2', output='sos',  fs=self.sample_rate)

    def apply_iir_filter(self, audio_data):
        """
        应用 IIR 滤波器。
        :param audio_data: 输入音频数据（numpy 数组）
        :return: 滤波后的音频数据

        """
        if self.filter_coeffs is None:
            return audio_data
        return sosfilt(self.filter_coeffs, audio_data)
    
    def apply_current_filter(self, audio_data):
        """
        应用滤波器设置
        :param audio_data: 输入音频数据（numpy 数组）
        :return: 滤波后的音频数据

        """
        if self.filter_coeffs is None:
            return audio_data
        
        # 根据使用的滤波器类型应用相应的滤波器

        if self.type == "FIR":
            return self.apply_fir_filter(audio_data)
        elif self.type == "IIR":
            return self.apply_iir_filter(audio_data)
        else:
            raise ValueError(f"Unsupported filter type: {self.type}")
        
