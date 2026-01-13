from __future__ import annotations


# Controller (your existing file)
from src.controller.experiment_controller import ExperimentController




def build_controller(cfg):
    if cfg.mode == "mock":
        from src.instruments.mock.switch_3700 import MockSwitch3700
        from src.instruments.mock.source_6221 import MockSource6221
        from src.instruments.mock.source_6487 import MockSource6487

        switch = MockSwitch3700()
        current_source = MockSource6221()
        voltmeter = MockSource6487(
            switch=switch,
            current_source=current_source
        )

    else:
        from src.instruments.real.switch_3700 import Switch3700
        from src.instruments.real.source_6221 import Source6221
        from src.instruments.real.source_6487 import Source6487

        switch = Switch3700()
        current_source = Source6221()
        voltmeter = Source6487()

    controller = ExperimentController(
        switch=switch,
        current_source=current_source,
        voltmeter=voltmeter,
    )

    return controller, switch, current_source, voltmeter
