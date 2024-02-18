import os
from collections.abc import Sequence

import numpy as np

from .base_player import BasePlayer
from .genome import Genome
from evolution.selection import fitness_weighted_selection
from evolution.crossover import one_point_crossover, uniform_crossover, crossover_by_name
from evolution.mutation import gaussian_mutation, uniform_mutation, mutation_by_name


class Population:
    """Population of (subclasses of) BasePlayers."""

    def __init__(self, size: int, players: Sequence[BasePlayer], gen: int = 1) -> None:
        self.size = size
        self.players = players
        self.current_generation = gen
    
    @property
    def average_fitness(self) -> float:
        return (sum(player.fitness for player in self.players) / float(len(self.players)))
    
    @property
    def champ(self) -> BasePlayer:
        return max(self.players, key = lambda player: player.fitness)

    def cull(self, percentage: float) -> None:
        """Remove all but top percentage of players with highest fitness."""

        self.players.sort(key = lambda player: player.fitness, reverse=True)
        num_left = max(int(self.size * percentage), 2)  #need at least 2 left to be able to repopulate 
        self.players = self.players[:num_left]

    def repopulate(self, crossover_type: str, mutation_type: str, mutation_rate: float) -> None:
        """Add players to self.players until it has size self.size.
        
        Players are generated by crossing over two unique parents that are already in the population and then mutating the results.
        """

        crossover = crossover_by_name(crossover_type)
        mutate = mutation_by_name(mutation_type)
        self.current_generation += 1
        
        parents = self.players[:]
        while len(self.players) < self.size:

            parent1, parent2 = fitness_weighted_selection(parents)
            offspring1, offspring2 = parent1.empty_clone(), parent2.empty_clone()
            offspring1.genome, offspring2.genome = crossover(parent1.genome, parent2.genome, self.current_generation)
            offspring1.genome, offspring2.genome = mutate(offspring1.genome, mutation_rate), mutate(offspring2.genome, mutation_rate)
            self.players.extend([offspring1, offspring2])
            
        if len(self.players) == self.size + 1: self.players.pop()   #adding 2 at a time can cause us to add one too many

    def new_genomes(self, structure: tuple[tuple[int,str]]) -> None:
        """Fill the population with newly randomized Genomes of given structure.
        
        Structure must be a tuple of tuples (size, activation).
        """

        for player in self.players:
            player.genome = Genome.new(structure)

    def save(self, folder_name: str) -> None:
        """Save population stats and players' Genomes.
        
        Designed to be done after a cull so that a new population can be repopulated from the save and continue evolution.
        """

        #check folder exists, create if it doesn't
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        #clear the folder
        for file in os.listdir(folder_name):
            os.remove(f'{folder_name}/{file}')

        #create a dictionary of stats
        stats = dict()
        stats['current_generation'] = self.current_generation

        #save the Genomes and record their fitness for repopulation
        for id, player in enumerate(self.players):
            player.genome.save(id, folder_name, player.fitness)

        np.savez(f'{folder_name}/stats', **stats)

    def load(self, folder_name: str) -> None:
        """Load Genomes saved in the given folder into the population's players.
        
        If there are more Genomes than players then the excess Genomes will be ignored.
        If there are more players than Genomes then the additional players will be removed.
        """

        #check folder exists
        if not os.path.exists(folder_name):
            raise Exception("Prescribed parent folder doesn't exist")
        
        #load the stats
        stats = np.load(f'{folder_name}/stats')
        self.current_generation = stats['current_generation']

        #load the Genomes and assign their fitness
        id = 0
        for file_name in os.listdir(folder_name):

            if file_name == 'stats.npz': continue   #already opened

            if id > self.size: break    #run out of players to load genomes into

            #load the Genome and its corresponding fitness
            genome, fitness = Genome.load(file_name, folder_name)
            genome.fitness = fitness

            #add the Genome to a (unique) player
            self.players[id].genome = genome
            id += 1

        #remove the rest of the players
        self.players = self.players[:id]