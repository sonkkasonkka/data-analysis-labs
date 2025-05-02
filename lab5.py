import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, filtfilt

# початкові значення 
DEFAULTS = {
    'amplitude': 1.0,
    'frequency': 2.0,
    'phase': 0.0,
    'noise_mean': 0.0,
    'noise_covariance': 0.1
}

# глобальні змінні для збереження шуму
cached_noise = None
last_noise_params = (DEFAULTS['noise_mean'], DEFAULTS['noise_covariance'])

# гармоніка + шум
def harmonic_with_noise(amplitude, frequency, phase, noise_mean, noise_covariance, show_noise):
    global cached_noise, last_noise_params

    t = np.linspace(0, 2, 1000)
    pure = amplitude * np.sin(2 * np.pi * frequency * t + phase)

    # якщо шум не змінювався, залишити старий
    if (noise_mean, noise_covariance) != last_noise_params or cached_noise is None:
        cached_noise = np.random.normal(noise_mean, np.sqrt(noise_covariance), size=t.shape)
        last_noise_params = (noise_mean, noise_covariance)

    noisy = pure + cached_noise
    return t, pure, noisy if show_noise else pure

# Фільтрація Butterworth lowpass filter
def filter_signal(signal, cutoff=3.0, fs=500.0, order=4):
    b, a = butter(order, cutoff / (0.5 * fs), btype='low')
    return filtfilt(b, a, signal)

def update(val):
    amp = s_amp.val
    freq = s_freq.val
    phase = s_phase.val
    n_mean = s_noise_mean.val
    n_cov = s_noise_cov.val
    show_noise = check.get_status()[0]
    show_filtered = check.get_status()[1]

    t, pure, signal = harmonic_with_noise(amp, freq, phase, n_mean, n_cov, show_noise)
    filtered = filter_signal(signal)

    l_orig.set_ydata(signal)
    l_pure.set_ydata(pure)
    l_filtered.set_ydata(filtered if show_filtered else np.full_like(signal, np.nan))
    fig.canvas.draw_idle()

# скидання параметрів
def reset(event):
    for s in [s_amp, s_freq, s_phase, s_noise_mean, s_noise_cov]:
        s.reset()
    check.set_active(0) if not check.get_status()[0] else None
    check.set_active(1) if not check.get_status()[1] else None

fig, ax = plt.subplots()
plt.subplots_adjust(left=0.25, bottom=0.45)

t = np.linspace(0, 2, 1000)
init_signal = DEFAULTS['amplitude'] * np.sin(2 * np.pi * DEFAULTS['frequency'] * t + DEFAULTS['phase'])
l_orig, = plt.plot(t, init_signal, label='Гармоніка з шумом')
l_pure, = plt.plot(t, init_signal, '--', label='Чиста гармоніка')
l_filtered, = plt.plot(t, np.full_like(init_signal, np.nan), label='Відфільтрована гармоніка')

plt.legend(loc='upper right')
plt.title("Гармоніка з шумом і фільтрацією")
plt.xlabel("Час")
plt.ylabel("Сигнал")

# слайдери
axcolor = 'lightgoldenrodyellow'
ax_amp = plt.axes([0.25, 0.35, 0.65, 0.03], facecolor=axcolor)
ax_freq = plt.axes([0.25, 0.30, 0.65, 0.03], facecolor=axcolor)
ax_phase = plt.axes([0.25, 0.25, 0.65, 0.03], facecolor=axcolor)
ax_noise_mean = plt.axes([0.25, 0.20, 0.65, 0.03], facecolor=axcolor)
ax_noise_cov = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)

s_amp = Slider(ax_amp, 'Амплітуда', 0.1, 5.0, valinit=DEFAULTS['amplitude'])
s_freq = Slider(ax_freq, 'Частота', 0.1, 10.0, valinit=DEFAULTS['frequency'])
s_phase = Slider(ax_phase, 'Фаза', 0.0, 2*np.pi, valinit=DEFAULTS['phase'])
s_noise_mean = Slider(ax_noise_mean, 'Середнє шуму', -1.0, 1.0, valinit=DEFAULTS['noise_mean'])
s_noise_cov = Slider(ax_noise_cov, 'Дисперсія шуму', 0.01, 1.0, valinit=DEFAULTS['noise_covariance'])

for slider in [s_amp, s_freq, s_phase, s_noise_mean, s_noise_cov]:
    slider.on_changed(update)

# кнопка Reset
reset_ax = plt.axes([0.8, 0.025, 0.1, 0.04])
button = Button(reset_ax, 'Reset', color=axcolor, hovercolor='0.975')
button.on_clicked(reset)

check_ax = plt.axes([0.025, 0.6, 0.15, 0.15])
check = CheckButtons(check_ax, ['Показати шум', 'Показати фільтр'], [True, False])
check.on_clicked(update)


plt.show()
