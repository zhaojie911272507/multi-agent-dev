import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, ifft

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def demonstrate_fourier_transform():
    """演示傅里叶变换的基本概念"""
    
    # 采样参数
    fs = 1000  # 采样频率
    t = np.linspace(0, 1, fs)  # 时间向量
    
    # 创建一个复合信号：包含多个频率成分
    # 信号 = 10Hz + 50Hz + 100Hz
    signal = (np.sin(2 * np.pi * 10 * t) +      # 10Hz
              0.5 * np.sin(2 * np.pi * 50 * t) + # 50Hz
              0.3 * np.sin(2 * np.pi * 100 * t)) # 100Hz
    
    # 添加一些噪声
    signal += 0.1 * np.random.randn(len(signal))
    
    # 计算FFT
    fft_result = fft(signal)
    frequencies = fftfreq(len(signal), 1/fs)
    
    # 计算幅度谱
    magnitude_spectrum = np.abs(fft_result)
    
    # 只显示正频率部分
    positive_freq_mask = frequencies >= 0
    positive_freqs = frequencies[positive_freq_mask]
    positive_magnitude = magnitude_spectrum[positive_freq_mask]
    
    # 创建图形
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. 时域信号
    axes[0, 0].plot(t[:200], signal[:200])  # 只显示前200个点
    axes[0, 0].set_title('时域信号')
    axes[0, 0].set_xlabel('时间 (秒)')
    axes[0, 0].set_ylabel('幅度')
    axes[0, 0].grid(True)
    
    # 2. 频域信号（幅度谱）
    axes[0, 1].plot(positive_freqs, positive_magnitude)
    axes[0, 1].set_title('频域信号（幅度谱）')
    axes[0, 1].set_xlabel('频率 (Hz)')
    axes[0, 1].set_ylabel('幅度')
    axes[0, 1].grid(True)
    axes[0, 1].set_xlim(0, 150)  # 限制显示范围
    
    # 3. 相位谱
    phase_spectrum = np.angle(fft_result)
    positive_phase = phase_spectrum[positive_freq_mask]
    axes[1, 0].plot(positive_freqs, positive_phase)
    axes[1, 0].set_title('相位谱')
    axes[1, 0].set_xlabel('频率 (Hz)')
    axes[1, 0].set_ylabel('相位 (弧度)')
    axes[1, 0].grid(True)
    axes[1, 0].set_xlim(0, 150)
    
    # 4. 重建信号（通过逆FFT）
    reconstructed_signal = np.real(ifft(fft_result))
    axes[1, 1].plot(t[:200], reconstructed_signal[:200], 'r-', label='重建信号')
    axes[1, 1].plot(t[:200], signal[:200], 'b--', alpha=0.7, label='原始信号')
    axes[1, 1].set_title('信号重建对比')
    axes[1, 1].set_xlabel('时间 (秒)')
    axes[1, 1].set_ylabel('幅度')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('fourier_transform_demo.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 打印主要频率成分
    print("\n=== 主要频率成分分析 ===")
    peak_indices = np.argsort(positive_magnitude)[-5:]  # 找到最大的5个峰值
    for i, idx in enumerate(reversed(peak_indices)):
        freq = positive_freqs[idx]
        magnitude = positive_magnitude[idx]
        print(f"频率 {freq:.1f} Hz: 幅度 {magnitude:.2f}")

def demonstrate_filtering():
    """演示频域滤波"""
    
    # 采样参数
    fs = 1000
    t = np.linspace(0, 1, fs)
    
    # 创建包含高频噪声的信号
    clean_signal = np.sin(2 * np.pi * 10 * t)  # 10Hz信号
    noise = 0.3 * np.sin(2 * np.pi * 200 * t)  # 200Hz噪声
    noisy_signal = clean_signal + noise
    
    # FFT
    fft_result = fft(noisy_signal)
    frequencies = fftfreq(len(noisy_signal), 1/fs)
    
    # 低通滤波：去除高频成分
    cutoff_freq = 50  # 截止频率50Hz
    filter_mask = np.abs(frequencies) <= cutoff_freq
    filtered_fft = fft_result * filter_mask
    
    # 逆FFT重建
    filtered_signal = np.real(ifft(filtered_fft))
    
    # 可视化
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 原始信号
    axes[0, 0].plot(t[:200], noisy_signal[:200])
    axes[0, 0].set_title('原始信号（含噪声）')
    axes[0, 0].set_xlabel('时间 (秒)')
    axes[0, 0].set_ylabel('幅度')
    axes[0, 0].grid(True)
    
    # 原始信号频谱
    positive_freq_mask = frequencies >= 0
    positive_freqs = frequencies[positive_freq_mask]
    positive_magnitude = np.abs(fft_result)[positive_freq_mask]
    axes[0, 1].plot(positive_freqs, positive_magnitude)
    axes[0, 1].set_title('原始信号频谱')
    axes[0, 1].set_xlabel('频率 (Hz)')
    axes[0, 1].set_ylabel('幅度')
    axes[0, 1].grid(True)
    axes[0, 1].set_xlim(0, 250)
    
    # 滤波后信号
    axes[1, 0].plot(t[:200], filtered_signal[:200])
    axes[1, 0].set_title('滤波后信号')
    axes[1, 0].set_xlabel('时间 (秒)')
    axes[1, 0].set_ylabel('幅度')
    axes[1, 0].grid(True)
    
    # 滤波后频谱
    filtered_positive_magnitude = np.abs(filtered_fft)[positive_freq_mask]
    axes[1, 1].plot(positive_freqs, filtered_positive_magnitude)
    axes[1, 1].set_title('滤波后频谱')
    axes[1, 1].set_xlabel('频率 (Hz)')
    axes[1, 1].set_ylabel('幅度')
    axes[1, 1].grid(True)
    axes[1, 1].set_xlim(0, 250)
    
    plt.tight_layout()
    plt.savefig('fourier_filtering_demo.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n=== 滤波效果分析 ===")
    print(f"原始信号RMS: {np.sqrt(np.mean(noisy_signal**2)):.4f}")
    print(f"滤波后信号RMS: {np.sqrt(np.mean(filtered_signal**2)):.4f}")
    print(f"噪声抑制比: {20*np.log10(np.sqrt(np.mean(noisy_signal**2))/np.sqrt(np.mean(filtered_signal**2))):.2f} dB")

if __name__ == "__main__":
    print("=== 傅里叶变换演示 ===")
    print("1. 基本傅里叶变换演示")
    demonstrate_fourier_transform()
    
    print("\n2. 频域滤波演示")
    demonstrate_filtering()
    
    print("\n=== 傅里叶变换总结 ===")
    print("• 傅里叶变换将时域信号转换为频域表示")
    print("• 频域显示了信号包含的频率成分")
    print("• 可以通过频域滤波去除不需要的频率成分")
    print("• FFT是计算离散傅里叶变换的高效算法")
    print("• 广泛应用于信号处理、图像处理、通信等领域") 