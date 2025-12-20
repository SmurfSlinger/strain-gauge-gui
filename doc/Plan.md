# Abstract:

The design of this program is object-oriented. This style was chosen to allow for flexible and dynamic code that allows for any machine, real or mock, to be used
with the main code for testing and research purposes.

Real instruments are defined as the three physical machines we work with in the lab--the switch, the voltage source, and the current source.

Mock instruments, conversely, are software-only mockups designed to mimic the behavior of the real machines for development and testing purposes.

In order to add a new instrument, a new source file should be added to the appropriate directory:
 ```
 * src/instruments/
 or
 * src/mock/  
 ```

The new class must extend the base_instrument class.

---






# Phase 1: Instrument Communication & Control

---
### 1) Analyze user manuals for each machine and provide all significant commands.
  * SYSTEM SWITCH/MULTIMETER
    * [Manual](../data/3700manual.pdf)
    ```
      * IDN?                        Query instrument identification string
      * RST                         Reset instrument to factory default state
      * SRE                         Enable service request events (rarely needed)
      * CLS                         Clear status and error queues

      * ROUTe:CLOSe (@<ch>)         Close (connect) a specific channel
      * ROUTe:OPEN (@<ch>)          Open (disconnect) a specific channel
      * ROUTe:CLOSe:ALL             Close all channels (use with caution)
      * ROUTe:OPEN:ALL              Open all channels (safe reset of switch state)

      * ROUTe:OPEN? (@<ch>)         Query if a channel is open
      * ROUTe:CLOSe? (@<ch>)        Query if a channel is closed

      * ROUTe:CHANnel:COUNt?        Query total number of available channels
      * ROUTe:CHANnel:LIST?         Query list of all valid channel numbers
      * ROUTe:PATH:STATE?           Query the current routing (path) configuration

      * ROUTe:CHANnel:DEFINE "<name>", (@<list>)   Create a named channel pattern
      * ROUTe:CHANnel:CLOSe "<name>"               Close all channels in a pattern
      * ROUTe:CHANnel:OPEN "<name>"                Open all channels in a pattern

      * ROUTe:SCAN:DEFINE (@<list>) Define channels for a scan sequence
      * ROUTe:SCAN:EXECute          Execute the scan
      * ROUTe:SCAN:ABORt            Abort an active scan

      * SYST:ERR?                   Query next system error in queue
      * STAT:OPER:COND?             Operational status register (system condition)
      * STAT:QUES:COND?             Questionable status register (hardware warnings)
    ```
  * VOLTAGE SOURCE
    * [Manual](../data/6487manual.pdf)
    ```
    * IDN?                      Query instrument identification string
    * RST                       Reset instrument to factory default state
    * CLS                       Clear status and error queues
    
    * SOUR:VOLT <value>         Set output voltage (in volts)
    * SOUR:VOLT?                Query output voltage
    * SOUR:VOLT:RANG <value>    Set voltage source range
    * SOUR:VOLT:STAT ON         Enable voltage output
    * SOUR:VOLT:STAT OFF        Disable voltage output

    * SENS:CURR:RANG <value>    Set current measurement range
    * SENS:CURR:RANG:AUTO ON    Enable auto-ranging for current
    * SENS:CURR:NPLC <value>    Set integration time (power line cycles)
    * SENS:ZERO:AUTO ON         Enable auto-zero mode
    * SENS:FUNC "CURR"          Select current measurement function
    * SENS:FUNC?                Query active measurement function

    * READ?                     Trigger a reading and return value
    * INIT                      Begin measurement without returning data
    * FETCH?                    Retrieve previously triggered readings
    * TRIG:COUN <value>         Set trigger count
    * TRIG:SOUR IMM             Immediate trigger source

    * FORM:ELEM READ,TIME       Format output: reading + timestamp
    * FORM:ELEM?                Query current output formatting

    * SYST:ZCH ON               Enable zero-check mode (force input to zero)
    * SYST:ZCH OFF              Disable zero-check (enable real readings)
    * SYST:ZCOR ON              Enable zero-correction
    * SYST:ZCOR:ACQ             Acquire zero-correction value
    * SYST:LOC                  Return control to front panel

    * SYST:ERR?                 Query next system error in queue
    * STAT:OPER:COND?           Operational status (system condition)
    * STAT:QUES:COND?           Questionable status (hardware warnings)
      ```
  * DC/AC CURRENT SOURCE
    * [Manual](../data/6221manual.pdf)
    ```
    * IDN?                        Query instrument identification string
    * RST                         Reset instrument to factory default state
    * CLS                         Clear status and error queues

    * SOUR:CURR <value>           Set DC output current (amps)
    * SOUR:CURR?                  Query output current
    * SOUR:CURR:RANG <value>      Set current source range
    * SOUR:CURR:STAT ON           Enable current output
    * SOUR:CURR:STAT OFF          Disable current output

    * SOUR:CURR:COMP <value>      Set compliance voltage limit
    * SOUR:CURR:COMP?             Query compliance voltage

    * SENS:VOLT:RANG <value>      Set voltage measurement range
    * SENS:VOLT:RANG:AUTO ON      Enable auto-ranging for voltage
    * SENS:FUNC "VOLT"            Select voltage measurement function
    * SENS:FUNC?                  Query active measurement function

    * READ?                       Trigger a reading and return value
    * INIT                        Begin measurement without returning data
    * FETCH?                      Retrieve previous readings
    * TRIG:COUN <value>           Set trigger count
    * TRIG:SOUR IMM               Immediate trigger source

    * SOUR:WAVE:FUNC SIN          Select sine waveform generation
    * SOUR:WAVE:AMPL <value>      Set amplitude of AC waveform
    * SOUR:WAVE:FREQ <value>      Set frequency of AC waveform
    * SOUR:WAVE:DCYC <value>      Set duty cycle (for pulse/square)
    * SOUR:WAVE:STAT ON           Enable waveform output
    * SOUR:WAVE:STAT OFF          Disable waveform output

    * SYST:ZCH ON                 Enable zero-check mode
    * SYST:ZCH OFF                Disable zero-check mode
    * SYST:LOC                    Return control to front panel

    * SYST:ERR?                   Query next system error in queue
    * STAT:OPER:COND?             Operational status (system condition)
    * STAT:QUES:COND?             Questionable status (hardware warnings)
      ```
---
### 2) Implement NIVISA and PYVISA.
* 
---
### 3) Configure GPIB communication.
*
---
### 4) Read data, verify outputs.
*
---
### 5) Integrate channel switching.
*
---
### 6) Implement error handling.
*
---
### 7) Test, identify edge cases.
* 
---

# Phase 2: GUI

---

### 1) Design buttons, inputs, and other controls.
* File, Edit, View, Project, Operate, Tools, Window, Help (baseline/reference)
* Record button (begin recording data)
  * Reset button to reset graph only (previous data is still saved)
  * Stop button to finish the test
* Plot Decision (e.g. resistance vs time, etc)
* Measurements
  * Voltage (V)
  * Current (A)
  * Resistance (Ohms)
* Real-time load/strain data measurements
---
### 2) Display data.
*
---
### 3) Implement live plotting/reading.
*
---
### 4) Implement saving data.
*
---
### 5) Design settings menu.
*
---
### 6) Add finishing details.
*
---


