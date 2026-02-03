"""
Help dialog for the Strain Gauge DAQ application.
"""
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTabWidget,
    QTextBrowser,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Qt


class HelpDialog(QDialog):
    """Help dialog with tabbed sections for different topics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Strain Gauge DAQ - Help")
        self.resize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Create tabbed interface
        tabs = QTabWidget()
        
        # Add tabs for different help topics
        tabs.addTab(self._create_quickstart(), "Quick Start")
        tabs.addTab(self._create_multiplexing_help(), "Multiplexing")
        tabs.addTab(self._create_data_help(), "Data & Files")
        tabs.addTab(self._create_troubleshooting(), "Troubleshooting")
        
        layout.addWidget(tabs)
        
        # Close button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
    
    def _create_quickstart(self):
        """Quick start guide."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setHtml("""
        <html>
        <body style="font-family: Arial; font-size: 11pt;">
        <h2>Quick Start Guide</h2>
        
        <h3>1. Connect Instruments</h3>
        <ol>
            <li>Ensure all GPIB instruments are powered on and connected</li>
            <li>Click <b>Connect Instruments</b> in the Experiment Settings section</li>
            <li>Wait for the connection confirmation dialog</li>
            <li>Status bar should show "Connected"</li>
        </ol>
        
        <h3>2. Configure Measurement</h3>
        <ol>
            <li><b>Force Ch +/-</b>: Set the switch channels to connect to your gauge</li>
            <li><b>Current (A)</b>: Set excitation current (typical: 0.001 A = 1 mA)</li>
            <li><b>Interval (ms)</b>: Set time between samples (typical: 100 ms)</li>
        </ol>
        
        <h3>3. Start Recording</h3>
        <ol>
            <li>Set a working directory using the <b>Browse (...)</b> button</li>
            <li>Click <b>RECORD</b></li>
            <li>Choose where to save the CSV file</li>
            <li>Data will be plotted in real-time and saved to the CSV</li>
        </ol>
        
        <h3>4. Stop Recording</h3>
        <ol>
            <li>Click <b>STOP</b> to end the measurement</li>
            <li>CSV file is automatically closed and saved</li>
            <li>Click <b>Reset</b> to clear the plot if needed</li>
        </ol>
        
        <p><b>Tip:</b> Use the <b>Plot Decision</b> dropdown to switch between viewing 
        Resistance, Voltage, or Current vs Time.</p>
        </body>
        </html>
        """)
        return browser
    
    def _create_multiplexing_help(self):
        """Multiplexing guide."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setHtml("""
        <html>
        <body style="font-family: Arial; font-size: 11pt;">
        <h2>Multiplexing Guide</h2>
        
        <p>Multiplexing allows you to measure multiple strain gauges during a single test
        by automatically switching between different channel configurations.</p>
        
        <h3>Setting Up Cases</h3>
        <p>Measurement cases are defined in <code>config.json</code>:</p>
        <pre style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
"measurement_cases": [
  {"name": "Gauge 1", "force_channel_pos": 1001, "force_channel_neg": 1002},
  {"name": "Gauge 2", "force_channel_pos": 1003, "force_channel_neg": 1004},
  {"name": "Gauge 3", "force_channel_pos": 1005, "force_channel_neg": 1006}
]</pre>
        
        <h3>Operating Modes</h3>
        
        <h4>Mode 1: Manual (No Multiplexing)</h4>
        <ul>
            <li><b>Enable Multiplexing:</b> Unchecked</li>
            <li>Select a gauge from the dropdown</li>
            <li>Channels automatically populate</li>
            <li>Measures only the selected gauge</li>
            <li><b>Use when:</b> Testing a single location or calibrating</li>
        </ul>
        
        <h4>Mode 2: Manual Multiplexing</h4>
        <ul>
            <li><b>Enable Multiplexing:</b> Checked</li>
            <li><b>Auto Cycle:</b> Unchecked</li>
            <li>Click <b>Switch to Next Case</b> button to manually advance</li>
            <li>System reconfigures channels automatically</li>
            <li><b>Use when:</b> You want control over when to switch 
            (e.g., after reaching specific load levels)</li>
        </ul>
        
        <h4>Mode 3: Automatic Multiplexing</h4>
        <ul>
            <li><b>Enable Multiplexing:</b> Checked</li>
            <li><b>Auto Cycle:</b> Checked</li>
            <li>Set <b>Readings/Case</b> (e.g., 10 readings per gauge)</li>
            <li>System automatically rotates through all gauges</li>
            <li>Takes N readings from each gauge before switching</li>
            <li><b>Use when:</b> Monitoring multiple locations during continuous testing</li>
        </ul>
        
        <h3>Status Indicators</h3>
        <ul>
            <li><b>Current Case:</b> Shows which gauge is being measured</li>
            <li><b>Readings:</b> Number of samples taken from current gauge</li>
        </ul>
        
        <p><b>Note:</b> When multiplexing is enabled, the case dropdown is disabled
        because switching is controlled by the multiplexing system.</p>
        </body>
        </html>
        """)
        return browser
    
    def _create_data_help(self):
        """Data and file format help."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setHtml("""
        <html>
        <body style="font-family: Arial; font-size: 11pt;">
        <h2>Data & File Format</h2>
        
        <h3>CSV Output Format</h3>
        <p>Data is saved as a CSV (Comma-Separated Values) file with:</p>
        
        <h4>Header Section (metadata):</h4>
        <pre style="background: #f0f0f0; padding: 10px; border-radius: 5px;">
# Strain Gauge Data Acquisition
# Date: 2026-02-03 14:30:15
# Current: 0.001 A
# Channels: +1002, -1002
# Sample Interval: 100 ms
</pre>
        
        <h4>Data Columns:</h4>
        <table border="1" cellpadding="5" style="border-collapse: collapse;">
        <tr style="background: #e0e0e0;">
            <th>Column</th><th>Units</th><th>Description</th>
        </tr>
        <tr><td>Time (s)</td><td>seconds</td><td>Elapsed time since recording started</td></tr>
        <tr><td>Current (A)</td><td>amperes</td><td>Applied excitation current</td></tr>
        <tr><td>Voltage (V)</td><td>volts</td><td>Measured voltage across gauge</td></tr>
        <tr><td>Resistance (Ohm)</td><td>ohms</td><td>Calculated R = V/I</td></tr>
        <tr><td>Load (lbs)</td><td>pounds</td><td>Mechanical load (if DAQ connected)</td></tr>
        <tr><td>Extension (in)</td><td>inches</td><td>Displacement (if DAQ connected)</td></tr>
        <tr><td>Strain 1</td><td>-</td><td>Strain gauge 1 reading</td></tr>
        <tr><td>Strain 2</td><td>-</td><td>Strain gauge 2 reading</td></tr>
        </table>
        
        <h3>Opening CSV Files</h3>
        <ul>
            <li><b>Excel:</b> File → Open → Select CSV file</li>
            <li><b>Python:</b> Use <code>pandas.read_csv()</code>, skip comment rows with <code>comment='#'</code></li>
            <li><b>MATLAB:</b> Use <code>readtable()</code> or <code>csvread()</code></li>
        </ul>
        
        <h3>Working Directory</h3>
        <p>The working directory is where CSV files are saved by default. 
        Set it once at the start of your session using the <b>Browse (...)</b> button.</p>
        
        <p><b>Tip:</b> Create a new folder for each test specimen to keep data organized.</p>
        </body>
        </html>
        """)
        return browser
    
    def _create_troubleshooting(self):
        """Troubleshooting guide."""
        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setHtml("""
        <html>
        <body style="font-family: Arial; font-size: 11pt;">
        <h2>Troubleshooting</h2>
        
        <h3>Connection Issues</h3>
        
        <h4>Error: "Connection FAILED"</h4>
        <ul>
            <li>Check that all instruments are powered on</li>
            <li>Verify GPIB cables are securely connected</li>
            <li>Ensure GPIB addresses match config.json:
                <ul>
                    <li>Switch: GPIB0::16::INSTR</li>
                    <li>Current Source 6221: GPIB0::12::INSTR</li>
                    <li>Picoammeter 6487: GPIB0::22::INSTR</li>
                </ul>
            </li>
            <li>Try power cycling the instruments</li>
        </ul>
        
        <h4>Instruments connected but no data</h4>
        <ul>
            <li>Check that channels are valid (1001-1020, 1021-1040)</li>
            <li>Verify gauge is properly wired to the switch channels</li>
            <li>Check current level isn't too low (try 1 mA = 0.001 A)</li>
        </ul>
        
        <h3>Data Issues</h3>
        
        <h4>Resistance shows as 0.000000</h4>
        <ul>
            <li>Check that gauge is connected (not open circuit)</li>
            <li>Verify correct channels are selected</li>
            <li>Increase current if signal is too low</li>
        </ul>
        
        <h4>Noisy or erratic readings</h4>
        <ul>
            <li>Check for loose connections</li>
            <li>Verify proper grounding</li>
            <li>Shield cables from electrical noise sources</li>
            <li>Increase sample interval to allow settling time</li>
        </ul>
        
        <h3>GUI Issues</h3>
        
        <h4>Plot window keeps resizing</h4>
        <ul>
            <li>This is fixed in the current version</li>
            <li>Y-axis locks after 10 data points</li>
            <li>X-axis scrolls showing last 30 seconds</li>
        </ul>
        
        <h4>Can't save CSV file</h4>
        <ul>
            <li>Set a working directory first using Browse (...)</li>
            <li>Ensure you have write permissions to that folder</li>
            <li>Close any programs that might have the file open</li>
        </ul>
        
        <h3>Multiplexing Issues</h3>
        
        <h4>Switch button doesn't work</h4>
        <ul>
            <li>Enable Multiplexing must be checked</li>
            <li>Auto Cycle must be unchecked for manual switching</li>
            <li>Recording must be active (click RECORD first)</li>
        </ul>
        
        <h4>Auto cycle not working</h4>
        <ul>
            <li>Both Enable Multiplexing and Auto Cycle must be checked</li>
            <li>Wait for Readings/Case count to reach the set value</li>
            <li>Check that multiple cases are defined in config.json</li>
        </ul>
        
        <h3>Getting Help</h3>
        <p>For additional support:</p>
        <ul>
            <li>Check instrument manuals for GPIB command reference</li>
            <li>Review config.json for proper channel configuration</li>
            <li>Contact your lab supervisor or IT support</li>
        </ul>
        </body>
        </html>
        """)
        return browser
