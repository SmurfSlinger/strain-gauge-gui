from src.mock.switch_3700 import MockSwitch3700
from src.controller.experiment_controller import ExperimentController
from src.mock.source_6221 import MockSource6221
from src.mock.source_6487 import MockSource6487

def mock_main():
    sw = MockSwitch3700()
    sw.connect()

    sw.close_channel(101)
    sw.close_channel(102)
    print(sw.closed_channels)

    sw.open_channel(101)
    print(sw.closed_channels)

    sw.open_all()
    print(sw.closed_channels)

def test_sources():
    controller = ExperimentController(
        switch=MockSwitch3700(),
        current_source=MockSource6221(),
        voltage_source=MockSource6487()
    )

    result = controller.run_single_channel_test(101, 0.001, 5)
    print(result)

test_sources()