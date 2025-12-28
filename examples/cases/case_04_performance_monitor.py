"""
case_04_performance_monitor.py
Real-time system performance monitor

Demonstrates:
- Tracking CPU and RAM via psutil
- History graphs with fixed 0–100% scale
- Circular gauges with dense fill
- Render statistics with highlighted background
"""

import transparent_overlay
import time
import psutil
import math


class SystemMonitor:
    def __init__(self):
        self.overlay = transparent_overlay.Overlay()
        self.overlay.start_layer()

        self.cpu_history = []
        self.ram_history = []
        self.max_history = 100
        self.screen_refresh_rate = self.get_screen_refresh_rate()
        self.start_time = time.time()

    def get_cpu_usage(self):
        """Get CPU usage percent"""
        return psutil.cpu_percent(interval=0.1)

    def get_ram_usage(self):
        """Get RAM usage percent"""
        memory = psutil.virtual_memory()
        return memory.percent

    def get_system_info(self):
        """Get basic system information"""
        cpu_usage = self.get_cpu_usage()
        ram_usage = self.get_ram_usage()

        # Обновляем историю
        self.cpu_history.append(cpu_usage)
        self.ram_history.append(ram_usage)

        if len(self.cpu_history) > self.max_history:
            self.cpu_history.pop(0)
            self.ram_history.pop(0)

        return cpu_usage, ram_usage

    def get_screen_refresh_rate(self):
        """Get primary display refresh rate (Windows)"""
        try:
            user32 = ctypes.windll.user32
            hdc = user32.GetDC(0)
            refresh_rate = user32.GetDeviceCaps(hdc, 116)  # VREFRESH
            user32.ReleaseDC(0, hdc)
            return refresh_rate
        except:
            return '-'

    def draw_graph(self, x, y, width, height, data, color, label):
        """Draw a graph with fixed 0–100% range"""
        if len(data) < 2:
            return

        # Graph background
        self.overlay.draw_rect(x, y, width, height, (0, 0, 0, 120))
        self.overlay.draw_rect(x, y, width, height, color, thickness=1)

        # Graph title
        self.overlay.draw_text(x + width // 2, y - 15, label,
                               color=color, font_size=12, align="center")

        # Draw lines (fixed 0–100%)
        points = []

        for i, value in enumerate(data):
            x_pos = x + (i / len(data)) * width
            y_pos = y + height - (value / 100) * height  # Фиксировано 100%
            points.append((x_pos, y_pos))

        for i in range(len(points) - 1):
            self.overlay.draw_line(points[i][0], points[i][1],
                                   points[i + 1][0], points[i + 1][1], color, 2)

    def draw_gauge(self, x, y, size, value, color, label):
        """Draw a circular gauge with dense fill"""
        # Фон
        self.overlay.draw_circle(x, y, size, (0, 0, 0, 120))
        self.overlay.draw_circle(x, y, size, (100, 100, 100, 255), thickness=2)

        if value > 0:
            segments = 200
            degrees_per_segment = 360 // segments
            active_segments = int((value / 100) * segments)

            for i in range(active_segments):
                angle = math.radians(i * degrees_per_segment - 90)  # Start from top
                end_x = x + (size - 3) * math.cos(angle)
                end_y = y + (size - 3) * math.sin(angle)
                self.overlay.draw_line(x, y, end_x, end_y, color, 2)

        # Text below the gauge
        self.overlay.draw_text(x, y + size + 10, f"{value:.1f}%",
                               color=color, font_size=14, align="center", anchor="mm")
        self.overlay.draw_text(x, y + size + 25, label,
                               color=color, font_size=12, align="center", anchor="mm")

    def draw_info_panel(self, cpu_usage, ram_usage, elapsed_time):
        """Draw the main information panel"""
        panel_x, panel_y = 20, 20
        panel_width, panel_height = 220, 180

        # Panel background
        self.overlay.draw_rect(panel_x, panel_y, panel_width, panel_height, (0, 0, 0, 180))
        self.overlay.draw_rect(panel_x, panel_y, panel_width, panel_height, (80, 80, 120, 255), thickness=2)

        # Title
        self.overlay.draw_text(panel_x + 10, panel_y + 15, "System Monitor",
                               color=(255, 255, 255, 255), font_size=16)

        # CPU info
        cpu_color = (255, 100, 100, 255) if cpu_usage > 80 else (100, 255, 100, 255)
        self.overlay.draw_text(panel_x + 20, panel_y + 45, f"CPU: {cpu_usage:.1f}%",
                               color=cpu_color, font_size=14)

        # RAM info
        ram_color = (255, 100, 100, 255) if ram_usage > 80 else (100, 200, 255, 255)
        self.overlay.draw_text(panel_x + 20, panel_y + 70, f"RAM: {ram_usage:.1f}%",
                               color=ram_color, font_size=14)

        # Uptime
        self.overlay.draw_text(panel_x + 20, panel_y + 95, f"Uptime: {elapsed_time:.0f}s",
                               color=(200, 200, 200, 255), font_size=14)

        # FPS info
        render_fps = self.overlay.get_render_fps()
        object_count = self.overlay.get_object_count()

        fps_color = (100, 255, 100, 255) if render_fps > 30 else (255, 100, 100, 255)
        self.overlay.draw_text(panel_x + 20, panel_y + 120, f"Screen FPS: {self.screen_refresh_rate}",
                               color=fps_color, font_size=14)
        self.overlay.draw_text(panel_x + 20, panel_y + 145, f"Objects: {object_count}",
                               color=(200, 200, 255, 255), font_size=14)

    def run(self):
        """Main monitoring loop"""
        print("Starting system monitor...")
        print("Tracking CPU, RAM, and FPS in real time")

        try:
            while True:
                cpu_usage, ram_usage = self.get_system_info()
                elapsed_time = time.time() - self.start_time

                self.overlay.frame_clear()

                # Main information panel
                self.draw_info_panel(cpu_usage, ram_usage, elapsed_time)

                # Graphs (fixed 0–100% range)
                graph_x, graph_y = 20, 220
                graph_width, graph_height = 300, 100

                self.draw_graph(graph_x, graph_y, graph_width, graph_height,
                                self.cpu_history, (255, 100, 100, 255), "CPU Usage %")

                self.draw_graph(graph_x, graph_y + 120, graph_width, graph_height,
                                self.ram_history, (100, 200, 255, 255), "RAM Usage %")

                # Circular gauges with dense fill
                gauge_x, gauge_y = 350, 100
                gauge_size = 40

                self.draw_gauge(gauge_x, gauge_y, gauge_size, cpu_usage,
                                (255, 100, 100, 255), "CPU")

                self.draw_gauge(gauge_x + 100, gauge_y, gauge_size, ram_usage,
                                (100, 200, 255, 255), "RAM")

                # Library statistics
                stats_x, stats_y = 350, 200
                stats_text, _ = self.overlay.get_render_statistics()

                self.overlay.draw_text(stats_x, stats_y, stats_text,
                                       color=(200, 200, 200, 255), font_size=15, highlight=True,
                                       bg_color=(0, 0, 0, 120))

                self.overlay.signal_render()
                time.sleep(0.05)  # Update periodically

        except KeyboardInterrupt:
            print("Monitoring stopped")
        finally:
            self.overlay.stop_layer()


def main():
    monitor = SystemMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
