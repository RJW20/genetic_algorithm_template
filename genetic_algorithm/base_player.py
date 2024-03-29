from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from copy import deepcopy

from genetic_algorithm.genome import Genome

class BasePlayer(ABC):
    """Abstract base class for a Player in a population."""

    def __init__(self) -> None:
        pass

    @property
    def score(self) -> int:
        return self._score
    
    @score.setter
    def score(self, value: int) -> None:
        self._score = value

    @property
    def fitness(self) -> float:
        return self._fitness

    @fitness.setter
    def fitness(self, value: float) -> None:
        self._fitness = value

    @property
    def best_score(self) -> int:
        return self._best_score
    
    @best_score.setter
    def best_score(self, value: int) -> None:
        self._best_score = value

    @property
    def genome(self) -> Genome:
        return self._genome

    @genome.setter
    def genome(self, value: Genome) -> None:
        self._genome = value

    @abstractmethod
    def look(self) -> None:
        """Update the attributes used as input to the Genome."""
        pass

    @abstractmethod
    def think(self) -> Any:
        """Feed the input into the Genome and turn the output into a valid move."""
        pass

    @abstractmethod
    def move(self, move: Any) -> None:
        """Advance to the state achieved by carrying out move."""
        pass

    @property
    @abstractmethod
    def is_dead(self) -> bool:
        """Return True if the player has reached a state where the game is over."""
        pass

    @abstractmethod
    def start_state(self) -> None:
        """Put player in a state to begin simulation in its environment."""
        pass

    def __eq__(self, other: BasePlayer) -> bool:
        return self.genome == other.genome

    def empty_clone(self) -> BasePlayer:
        """Return a new instance of self's class without a genome."""
        
        clone = deepcopy(self)
        clone.fitness = 0
        clone.best_score = 0
        clone.genome = None

        return clone