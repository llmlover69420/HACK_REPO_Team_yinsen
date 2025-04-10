import matplotlib.pyplot as plt
import queue
from typing import List, Optional
import logging

class EnergyVisualizer:
    def __init__(self, threshold: float):
        self.logger = logging.getLogger(__name__)
        self.fig = None
        self.ax = None
        self.line = None
        self.threshold_line = None
        self.threshold = threshold
        
        # Initialize the plot
        self._setup_plot()
    
    def _setup_plot(self):
        """Initialize the matplotlib plot"""
        plt.ion()  # Enable interactive mode
        self.fig, self.ax = plt.subplots(figsize=(10, 4))
        self.line, = self.ax.plot([], [])
        self.threshold_line = self.ax.axhline(y=self.threshold, color='r', linestyle='--')
        self.ax.set_title('Audio Energy Levels')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Energy')
        self.ax.grid(True)
        plt.show()
    
    def update(self, time_values: List[float], energy_values: List[float]):
        """Update the plot with new data"""
        try:
            if self.line is not None:
                self.line.set_data(time_values, energy_values)
                self.ax.relim()
                self.ax.autoscale_view()
                plt.pause(0.01)
        except Exception as e:
            self.logger.error(f"Error updating plot: {e}")
    
    def close(self):
        """Close the plot"""
        if self.fig is not None:
            plt.close(self.fig) 