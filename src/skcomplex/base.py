"""Base classes for systems their components."""

# Author: Georgios Douzas <gdouzas@icloud.com> License: MIT

import inspect
from abc import abstractmethod
from typing import Any, Self

import numpy as np
import numpy.typing as npt
from sage.all import var
from sklearn.utils import check_array


class BaseSystemComponent:
    """Base class for all system components.

    Args:
        label:
            The label of the component.
    """

    def __init__(self: Self, label: str) -> None:
        """Initialize the system component with a label."""
        self.label = label
        self._init()

    @abstractmethod
    def _init_param(self: Self, param_name: str) -> Self:
        return self

    def _init(self: Self) -> Self:
        """Initialize the component's properties."""
        parameters = inspect.signature(self.__init__).parameters.values()  # type: ignore[misc]
        labels = [
            getattr(self, parameter.name)
            for parameter in parameters
            if parameter.name == 'label' or parameter.name.endswith('_label')
        ]
        for parameter in parameters:
            if parameter.name != 'label' and not parameter.name.endswith('_label'):
                value = getattr(self, parameter.name)
                if value is None:
                    setattr(self, f'{parameter.name}_', var(f'{parameter.name}__{"__".join(labels)}'))
                else:
                    self._init_param(parameter.name)
        return self


class BaseElement(BaseSystemComponent):
    """Base class for all elements."""


class BaseElementsInteraction(BaseSystemComponent):
    """Base class for all between elements interactions.

    Args:
        label:
            The label of the interaction.

        element_1_label:
            The label of the first element.

        element_2_label:
            The label of the second element.
    """

    def __init__(self: Self, label: str, element_1_label: str, element_2_label: str) -> None:
        """Initialize the interaction with interaction and elements labels."""
        self.element_1_label = element_1_label
        self.element_2_label = element_2_label
        super().__init__(label)


class BaseEnvironmentInteraction(BaseSystemComponent):
    """Base class for all elements interactions with the environment.

    Args:
        label:
            The label of the interaction.

        element_label:
            The label of the element.
    """

    def __init__(self: Self, label: str, element_label: str) -> None:
        """Initialize the interaction with interaction and element labels."""
        self.element_label = element_label
        super().__init__(label)


class BaseSpace(BaseSystemComponent):
    """Base class for all spaces."""


class BaseSystem:
    """Base class for all systems.

    Args:
        elements:
            A collection of elements that constitute the system.

        elements_interactions:
            A collection of the interactions between elements.

        environment_interactions:
            A collection of the interactions of the elements with the environment.

        space:
            The space of the system.
    """

    def __init__(
        self: Self,
        elements: list[BaseElement],
        elements_interactions: list[BaseElementsInteraction],
        environment_interactions: list[BaseEnvironmentInteraction],
        space: BaseSpace | None = None,
    ) -> None:
        """Initialize the system with elements and interactions."""
        self.elements = elements
        self.elements_interactions = elements_interactions
        self.environment_interactions = environment_interactions
        self.space = space

    def _get_element_interactions(
        self: Self,
        element: BaseElement,
    ) -> list[BaseElementsInteraction | BaseEnvironmentInteraction]:
        label = element.label
        interactions: list[BaseElementsInteraction | BaseEnvironmentInteraction] = []
        for interaction in self.elements_interactions_:
            if label == interaction.element_1_label and isinstance(interaction, BaseElementsInteraction):
                interactions.append(interaction)
        for interaction in self.environment_interactions_:
            if label == interaction.element_label and isinstance(interaction, BaseEnvironmentInteraction):
                interactions.append(interaction)
        return interactions

    def _check_elements(self: Self) -> Self:
        """Check elements."""
        self.elements_: npt.NDArray[np.object_]
        self.elements_labels_: npt.NDArray[np.str_]
        if self.elements is None:
            self.elements_ = np.array([], dtype=object)
            self.elements_labels_ = np.array([], dtype=str)
            return self
        if not isinstance(self.elements, list) or not all(
            isinstance(element, BaseElement) for element in self.elements
        ):
            error_msg = 'Parameter `elements` should be an list of `Element` objects.'
            raise TypeError(error_msg)
        elements_labels = check_array([element.label for element in self.elements], ensure_2d=False, dtype=str)
        assert np.unique(elements_labels).size == elements_labels.size, 'Elements should have unique labels.'
        self.elements_ = check_array(self.elements, ensure_2d=False, dtype=object)
        self.elements_labels_ = check_array(elements_labels, ensure_2d=False, dtype=str)
        return self

    def _check_elements_interactions(self: Self) -> Self:
        self.elements_interactions_: npt.NDArray[np.object_]
        self.elements_interactions_labels_: npt.NDArray[np.str_]
        if self.elements_interactions is None:
            self.elements_interactions_ = np.array([], dtype=object)
            self.elements_interactions_labels_ = np.array([], dtype=str)
            return self
        if not isinstance(self.elements_interactions, list) or not all(
            isinstance(interaction, BaseElementsInteraction) for interaction in self.elements_interactions
        ):
            error_msg = 'Parameter `elements_interactions` should be an list of `ElementsInteraction` object.'
            raise TypeError(error_msg)
        for interaction in self.elements_interactions:
            if interaction.element_1_label not in self.elements_labels_:
                error_msg = (
                    'Element label 1 should be one of the available elements '
                    f'labels. Got {interaction.element_1_label} instead.'
                )
                raise ValueError(error_msg)
            if interaction.element_2_label not in self.elements_labels_:
                error_msg = (
                    'Element label 2 should be one of the available elements labels. '
                    f'Got {interaction.element_2_label} instead.'
                )
                raise ValueError(error_msg)
            if interaction.element_1_label == interaction.element_2_label:
                error_msg = (
                    'Element labels 1 and 2 should be different. '
                    f'Got {interaction.element_1_label} and {interaction.element_2_label} instead.'
                )
                raise ValueError(error_msg)
        elements_interactions_labels = check_array(
            [
                (interaction.label, interaction.element_1_label, interaction.element_2_label)
                for interaction in self.elements_interactions
            ],
            ensure_2d=False,
            dtype=str,
        )
        error_msg = (
            'Interactions between elements should '
            'have unique labels of the form (label, element_1_label, element_2_label).'
        )
        assert np.unique(elements_interactions_labels, axis=0).size == elements_interactions_labels.size, error_msg
        self.elements_interactions_ = check_array(self.elements_interactions, ensure_2d=False, dtype=object)
        self.elements_interactions_labels_ = check_array(elements_interactions_labels, dtype=str)
        return self

    def _check_environment_interactions(self: Self) -> Self:
        self.environment_interactions_: npt.NDArray[np.object_]
        self.environment_interactions_labels_: npt.NDArray[np.str_]
        if self.environment_interactions is None:
            self.environment_interactions_ = np.array([], dtype=object)
            self.environment_interactions_labels_ = np.array([], dtype=str)
            return self
        if not isinstance(self.environment_interactions, list) or not all(
            isinstance(interaction, BaseEnvironmentInteraction) for interaction in self.environment_interactions
        ):
            error_msg = 'Parameter `environment_interactions` should be an list of `EnvironmentInteraction` object.'
            raise TypeError(error_msg)
        for interaction in self.environment_interactions:
            if interaction.element_label not in self.elements_labels_:
                error_msg = (
                    'Element label should be one of the available elements labels. '
                    f'Got {interaction.element_label} instead.'
                )
                raise ValueError(error_msg)
        environment_interactions_labels = check_array(
            [(interaction.label, interaction.element_label) for interaction in self.environment_interactions],
            ensure_2d=False,
            dtype=str,
        )
        assert (
            np.unique(environment_interactions_labels, axis=0).size == environment_interactions_labels.size
        ), 'Interactions of elements with environment should have unique labels of the form (label, element_label).'
        self.environment_interactions_ = check_array(self.environment_interactions, ensure_2d=False, dtype=object)
        self.environment_interactions_labels_ = check_array(environment_interactions_labels, dtype=str)
        return self

    def _check_space(self: Self) -> Self:
        if not isinstance(self.space, BaseSpace):
            error_msg = 'Parameter `space` should be a `Space` object.'
            raise TypeError(error_msg)
        else:
            self.space_ = self.space
        return self

    def simulate(self: Self) -> Self:
        """Simulate the complex systems."""
        self._check_elements()
        self._check_elements_interactions()
        self._check_environment_interactions()
        self._check_space()
        self.simulation_results_: dict[str, Any] = {}
        return self

    def __repr__(self: Self) -> str:
        """Representation of the system."""
        n_elements = len(self.elements) if self.elements is not None else 0
        n_elements_interactions = len(self.elements_interactions) if self.elements_interactions is not None else 0
        n_environment_interactions = (
            len(self.environment_interactions) if self.environment_interactions is not None else 0
        )
        return (
            f'{self.__class__.__name__} with {n_elements} element(s), {n_elements_interactions} elements'
            f' interactions and {n_environment_interactions} environment interactions.'
        )
