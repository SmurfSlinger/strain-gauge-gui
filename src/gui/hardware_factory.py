from src.controller.experiment_controller import ExperimentController
from src.gui.config_loader import GuiConfig

from src.instruments.mock.switch_3700 import MockSwitch3700
from src.instruments.mock.source_6221 import MockSource6221
from src.instruments.mock.source_6487 import MockSource6487

from src.instruments.real.switch_3700 import Switch3700
from src.instruments.real.source_6221 import Source6221
from src.instruments.real.source_6487 import Source6487


def build_controller(cfg: GuiConfig):
    mode = cfg.mode

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

    switch = Switch3700(cfg.switch)
    current_source = Source6221(cfg.current_source)
    voltmeter = Source6487(cfg.voltmeter)

    controller = ExperimentController(
        switch=switch,
        current_source=current_source,
        voltmeter=voltmeter,
    )

    controller.mode = "real"
    return controller, switch, current_source, voltmeter
