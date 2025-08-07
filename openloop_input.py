import numpy as np
import matplotlib.pyplot as plt

def generate_pneumatic_signal(total_time, sample_rate):
    """
    Generate cyclic voltage signal for pneumatic device testing.

    Parameters:
    total_time (float): Total generation time (seconds).
    sample_rate (int): Sampling rate (Hz), number of data points per second.

    Returns:
    t (numpy.ndarray): Time axis array.
    voltage (numpy.ndarray): Corresponding voltage signal array.
    """
    # Define signal period
    T = 8.0  # seconds (3+1+3+1)

    # Create time axis
    dt = 1.0 / sample_rate
    t = np.arange(0, total_time, dt)

    # Calculate relative time within each cycle
    time_in_cycle = t % T

    # Generate voltage values based on relative time within cycle
    # Initialize voltage array
    voltage = np.zeros_like(t)

    # 0-3s: 5V
    voltage[(time_in_cycle >= 0.0) & (time_in_cycle < 3.0)] = 5.0
    
    # 3-4s: 7V (1 second duration)
    voltage[(time_in_cycle >= 3.0) & (time_in_cycle < 4.0)] = 7.0
    
    # 4-7s: 5V (3 seconds duration)
    voltage[(time_in_cycle >= 4.0) & (time_in_cycle < 7.0)] = 5.0
    
    # 7-8s: 3V (1 second duration)
    voltage[(time_in_cycle >= 7.0) & (time_in_cycle < 8.0)] = 3.0

    return t, voltage

if __name__ == '__main__':
    # Close all previous figures
    plt.close('all')
    
    # --- Parameter Settings ---
    total_simulation_time = 24  # seconds, 3 complete cycles to observe repetition
    sampling_rate = 1000      # Hz, high sampling rate makes square wave edges clearer

    # --- Generate Signal ---
    time_array, voltage_array = generate_pneumatic_signal(total_simulation_time, sampling_rate)

    # --- Plotting and Visualization ---
    plt.figure(figsize=(12, 6))
    plt.plot(time_array, voltage_array, label='Input Signal', linewidth=2)
    
    # Set chart style
    plt.title("Pneumatic Device Open-loop Test Input Signal")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Voltage (V)")
    plt.grid(True)
    plt.ylim(2.5, 7.5)  # Set Y-axis range to see 3V, 5V and 7V clearly
    plt.xticks(np.arange(0, total_simulation_time + 1, 1)) # Set X-axis ticks
    plt.legend()

    # Display chart
    plt.show()