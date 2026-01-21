from src.controller.experiment_controller import ExperimentController

from src.instruments.mock.switch_3700 import MockSwitch3700
from src.instruments.mock.source_6221 import MockSource6221
from src.instruments.mock.source_6487 import MockSource6487

from src.instruments.keithley.keithley_3700 import Keithley3700
from src.instruments.keithley.keithley_6221 import Keithley6221
from src.instruments.keithley.keithley_6487 import Keithley6487


def build_controller(cfg):
    mode = cfg.get("mode", "mock")

    if mode == "mock":
        switch = MockSwitch3700()
        current_source = MockSource6221()
        voltmeter = MockSource6487()

        controller = ExperimentController(
            switch=switch,
            current_source=current_source,
            voltmeter=voltmeter,
        )

        controller.mode = "mock"
        return controller, switch, current_source, voltmeter

    # -----------------------------
    # REAL HARDWARE MODE
    # -----------------------------

    gpib = cfg["gpib_addresses"]

    switch = Keithley3700(gpib["switch"])
    current_source = Keithley6221(gpib["current_source"])
    voltmeter = Keithley6487(gpib["voltmeter"])

    controller = ExperimentController(
        switch=switch,
        current_source=current_source,
        voltmeter=voltmeter,
    )

    controller.mode = "real"

    print("BUILD MODE:", mode)
    print("SWITCH CLASS:", type(switch))

    return controller, switch, current_source, voltmeter
