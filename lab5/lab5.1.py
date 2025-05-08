import numpy as np
from scipy.signal import butter, filtfilt
from bokeh.plotting import figure, curdoc
from bokeh.layouts import column
from bokeh.models import Slider, Button, CheckboxGroup
from bokeh.models import ColumnDataSource

# === Time axis ===
t = np.linspace(0, 2 * np.pi, 1000)

# === Default parameters ===
DEFAULTS = {
    'amplitude': 1.0,
    'frequency': 2.0,
    'phase': 0.0,
    'noise_mean': 0.0,
    'noise_cov': 0.2
}

cached_noise = np.random.normal(DEFAULTS['noise_mean'], np.sqrt(DEFAULTS['noise_cov']), size=t.shape)

# === Signal generation ===
def generate_signal(amplitude, frequency, phase, noise_mean, noise_cov, show_noise):
    pure = amplitude * np.sin(2 * np.pi * frequency * t + phase)
    global cached_noise
    if show_noise:
        cached_noise = np.random.normal(noise_mean, np.sqrt(noise_cov), size=t.shape)
        return pure, pure + cached_noise
    else:
        return pure, pure

# === Filters ===
def moving_average(signal, window=10):
    return np.convolve(signal, np.ones(window) / window, mode='same')

def butterworth(signal, cutoff=3.0, fs=100.0, order=4):
    b, a = butter(order, cutoff / (0.5 * fs), btype='low')
    return filtfilt(b, a, signal)

# === Input elements ===
amp_slider = Slider(start=0.1, end=5, value=DEFAULTS['amplitude'], step=0.1, title="Amplitude")
freq_slider = Slider(start=0.1, end=10, value=DEFAULTS['frequency'], step=0.1, title="Frequency")
phase_slider = Slider(start=0, end=2 * np.pi, value=DEFAULTS['phase'], step=0.1, title="Phase")
mean_slider = Slider(start=-1.0, end=1.0, value=DEFAULTS['noise_mean'], step=0.1, title="Noise Mean")
cov_slider = Slider(start=0.01, end=1.0, value=DEFAULTS['noise_cov'], step=0.01, title="Noise Variance")

filters = CheckboxGroup(labels=["Show Noise", "Butterworth Filter", "Moving Average"], active=[0])
reset_btn = Button(label="Reset", button_type="success")

# === Data source with initial data ===
pure, noisy = generate_signal(
    DEFAULTS['amplitude'], DEFAULTS['frequency'], DEFAULTS['phase'],
    DEFAULTS['noise_mean'], DEFAULTS['noise_cov'], show_noise=True
)
source = ColumnDataSource(data={'x': t, 'pure': pure, 'noisy': noisy, 'filtered': noisy})

# === Plot setup ===
plot = figure(title="Harmonic with Noise and Filtering", height=400, width=800)
plot.line('x', 'pure', source=source, legend_label='Pure Harmonic', line_color='blue')
plot.line('x', 'noisy', source=source, legend_label='Noisy', line_color='red')
plot.line('x', 'filtered', source=source, legend_label='Filtered Signal', line_color='green')
plot.legend.location = "top_left"

# === Update function ===
def update():
    a = amp_slider.value
    f = freq_slider.value
    ph = phase_slider.value
    m = mean_slider.value
    cov = cov_slider.value
    show_noise = 0 in filters.active
    use_butter = 1 in filters.active
    use_custom = 2 in filters.active

    pure, noisy = generate_signal(a, f, ph, m, cov, show_noise)

    filtered = noisy
    if use_butter:
        filtered = butterworth(filtered)
    if use_custom:
        filtered = moving_average(filtered)

    source.data = {'x': t, 'pure': pure, 'noisy': noisy, 'filtered': filtered}

# === Reset function ===
def reset():
    amp_slider.value = DEFAULTS['amplitude']
    freq_slider.value = DEFAULTS['frequency']
    phase_slider.value = DEFAULTS['phase']
    mean_slider.value = DEFAULTS['noise_mean']
    cov_slider.value = DEFAULTS['noise_cov']
    filters.active = [0]
    update()

# === Event handlers ===
for widget in [amp_slider, freq_slider, phase_slider, mean_slider, cov_slider]:
    widget.on_change('value', lambda attr, old, new: update())
filters.on_change('active', lambda attr, old, new: update())  # Changed from 'value' to 'active'
reset_btn.on_click(reset)

# === Initial update ===
update()

# === Layout ===
layout = column(plot, amp_slider, freq_slider, phase_slider, mean_slider, cov_slider, filters, reset_btn)
curdoc().add_root(layout)
curdoc().title = "Harmonic with Noise"