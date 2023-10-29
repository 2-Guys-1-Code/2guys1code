from abc import ABC
from typing import Any, Callable, List, Optional


class InterruptStepException(Exception):
    pass


class EndOfStepException(Exception):
    pass


class AbstractStep(ABC):
    def __repr__(self) -> str:
        return f"<Step {self.name}>"

    def __init__(
        self,
        name: str,
        logic: Callable[["AbstractStep"], None],
        done_logic: Optional[Callable[["AbstractStep"], bool]] = None,
        interrupt_logic: Optional[Callable[["AbstractStep"], bool]] = None,
    ):
        self.name: str = name

        self._logic: Callable[[AbstractStep], None] = logic
        self.done_logic: Optional[Callable[[AbstractStep], bool]] = done_logic
        self.interrupt_logic: Optional[
            Callable[[AbstractStep], bool]
        ] = interrupt_logic

    def _check_interrupt(self) -> None:
        if self.interrupt_logic is not None and self.interrupt_logic(self):
            raise InterruptStepException()

    def _check_done(self) -> None:
        if self.done_logic is not None and self.done_logic(self):
            raise EndOfStepException()

    def logic(self, *args, **kwargs) -> None:
        if self._logic is not None:
            self._logic(self, *args, **kwargs)

        self._check_interrupt()
        self._check_done()


class StepManager:
    def __init__(self, steps: List[AbstractStep]) -> None:
        self.steps = steps
        self.interrupted = False
        self.current_step_index = 0

    @property
    def current_step(self) -> AbstractStep:
        return self.steps[self.current_step_index]

    def advance(self) -> None:
        self.current_step_index += 1
        if self.current_step_index >= len(self.steps):
            self.current_step_index = len(self.steps) - 1

    def interrupt(self) -> None:
        self.interrupted = True
        self.current_step_index = 0

    def do(self, *args: Any, **kwargs: Any) -> None:
        try:
            self.current_step.logic(*args, **kwargs)
        except InterruptStepException:
            self.interrupt()
        except EndOfStepException:
            self.advance()


def logic(s, *a, **k):
    pass


class FakeStep(AbstractStep):
    def __init__(self, name: str, *args, **kwargs) -> None:
        done_logic = kwargs.pop("done_logic", lambda s, *a, **k: True)
        super().__init__(name, *args, done_logic=done_logic, **kwargs)
        self.run_counter = 0
        self.logic_has_run: bool = False

    def logic(self, *args, **kwargs) -> None:
        self.run_counter += 1
        self.logic_has_run = True
        print(f"Running {self.name} logic...")
        super().logic(*args, **kwargs)


class NestedStep(AbstractStep):
    def __init__(
        self, name: str, steps: List[AbstractStep], *args, **kwargs
    ) -> None:
        super().__init__(name, *args, **kwargs)
        self._step_manager = StepManager(steps)
        self.run_counter = 0

    def logic(self, *args, **kwargs) -> None:
        self.run_counter += 1
        print(f"Running {self.name} logic...")
        super().logic(*args, **kwargs)

    @property
    def current_step(self) -> AbstractStep:
        return self._step_manager.current_step


def test_step_manager():
    step1 = FakeStep("step1", logic)
    step2 = FakeStep("step2", logic)
    step3 = FakeStep("step3", logic)
    steps = [step1, step2, step3]

    step_manager = StepManager(steps)

    assert step_manager.current_step is step1
    assert step1.logic_has_run == False

    step_manager.do()

    assert step1.logic_has_run == True
    assert step_manager.current_step is step2
    assert step2.logic_has_run == False

    step_manager.do(1)

    assert step2.logic_has_run == True
    assert step_manager.current_step is step3
    assert step3.logic_has_run == False

    step_manager.do()

    assert step3.logic_has_run == True
    assert step_manager.current_step is step3


def test_step_manager_waits_for_step_to_be_done():
    step1 = FakeStep(
        "step1",
        lambda s, *a, **k: setattr(
            s, "run_counter", getattr(s, "run_counter", 0) + 1
        ),
        done_logic=lambda s, *a, **k: getattr(s, "run_counter", 0) > 1,
    )
    step2 = FakeStep("step2", logic)
    steps = [step1, step2]

    step_manager = StepManager(steps)

    assert step_manager.current_step is step1
    assert step1.logic_has_run == False

    step_manager.do(1)
    step_manager.do(2)

    assert step1.logic_has_run == True
    assert step_manager.current_step is step2


def test_step_manager_interrupts_sequence_on_second_step():
    step1 = FakeStep("step1", logic)
    step2 = FakeStep(
        "step2",
        logic,
        interrupt_logic=lambda s, *a, **k: getattr(s, "run_counter", 0) == 1,
    )
    step3 = FakeStep("step3", logic)
    steps = [step1, step2, step3]

    step_manager = StepManager(steps)

    assert step_manager.current_step is step1
    assert step1.logic_has_run == False

    step_manager.do()

    assert step1.logic_has_run == True
    assert step_manager.current_step is step2

    step_manager.do()

    assert step_manager.current_step is step1


def test_step_manager_with_nested_steps():
    step1_1 = FakeStep("step1_1", logic)
    step1_2 = FakeStep("step1_2", logic)
    step2_1 = FakeStep("step2_1", logic)
    step2_2 = FakeStep("step2_2", logic)

    def nested_logic(s, *a, **k):
        s._step_manager.do()

    def nested_done_logic(s, *a, **k):
        return s.run_counter == 2

    nested_step1 = NestedStep(
        "nested_step1",
        [step1_1, step1_2],
        nested_logic,
        done_logic=nested_done_logic,
    )
    nested_step2 = NestedStep(
        "nested_step2",
        [step2_1, step2_2],
        nested_logic,
        done_logic=nested_done_logic,
    )

    step_manager = StepManager([nested_step1, nested_step2])

    assert step_manager.current_step is nested_step1
    assert nested_step1.current_step is step1_1
    assert step1_1.logic_has_run == False

    step_manager.do()

    assert step1_1.logic_has_run == True
    assert nested_step1.current_step is step1_2
    assert step_manager.current_step is nested_step1
    assert step1_2.logic_has_run == False

    step_manager.do()

    assert step1_2.logic_has_run == True
    assert nested_step1.current_step is step1_2
    assert step_manager.current_step is nested_step2
    assert nested_step2.current_step is step2_1
    assert step2_1.logic_has_run == False

    step_manager.do()

    assert step2_1.logic_has_run == True
    assert step_manager.current_step is nested_step2
    assert nested_step2.current_step is step2_2
    assert step2_2.logic_has_run == False

    step_manager.do()

    assert step2_2.logic_has_run == True
    assert step_manager.current_step is nested_step2
    assert nested_step2.current_step is step2_2


def test_step_manager_with_nested_steps__outer_sequence_continues_when_nested_interrupts():
    step1_1 = FakeStep(
        "step1_1",
        logic,
        interrupt_logic=lambda s, *a, **k: True,
    )
    step1_2 = FakeStep("step1_2", logic)
    step2_1 = FakeStep("step2_1", logic)
    step2_2 = FakeStep("step2_2", logic)

    def nested_logic(s, *a, **k):
        s._step_manager.do()

    def nested_done_logic(s, *a, **k):
        return s.run_counter == 2 or s._step_manager.interrupted

    nested_step1 = NestedStep(
        "nested_step1",
        [step1_1, step1_2],
        nested_logic,
        done_logic=nested_done_logic,
    )
    nested_step2 = NestedStep(
        "nested_step2",
        [step2_1, step2_2],
        nested_logic,
        done_logic=nested_done_logic,
    )

    step_manager = StepManager([nested_step1, nested_step2])

    assert step_manager.current_step is nested_step1
    assert nested_step1.current_step is step1_1
    assert step1_1.logic_has_run == False

    step_manager.do()

    assert step1_1.logic_has_run == True
    assert nested_step1.current_step is step1_1  # Maybe we should not reset?
    assert step1_2.logic_has_run == False
    assert step_manager.current_step is nested_step2
    assert nested_step2.current_step is step2_1

    step_manager.do()

    assert step1_2.logic_has_run == False
    assert step2_1.logic_has_run == True
    assert step_manager.current_step is nested_step2
    assert nested_step2.current_step is step2_2
    assert step2_2.logic_has_run == False

    step_manager.do()

    assert step2_2.logic_has_run == True
    assert step_manager.current_step is nested_step2
    assert nested_step2.current_step is step2_2
