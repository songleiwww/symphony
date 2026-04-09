# -*- coding: utf-8 -*-
"""
swarm_hybrid_algorithms.py - 11种混合智能优化算法内核实??集成到序境系统内核，支持自动加载和自然语言调用
遵循统一接口规范，与现有算法完全兼容
"""

import math
import random
import numpy as np
from typing import List, Callable, Tuple, Dict, Any

# 统一接口基类
class BaseOptimizer:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.num_iterations = kwargs.get('num_iterations', 50)
        self.verbose = kwargs.get('verbose', False)
        self.stats = {
            'iterations': 0,
            'best_fitness': float('inf'),
            'best_solution': None,
            'history': []
        }
    
    def set_problem(self, dimensions: int, objective_func: Callable, **kwargs):
        self.dimensions = dimensions
        self.objective_func = objective_func
        self.bounds = kwargs.get('bounds', [(-100, 100)] * dimensions)
        self.stats['best_fitness'] = float('inf')
        self.stats['best_solution'] = None
        self.stats['history'] = []
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        raise NotImplementedError("子类必须实现run方法")
    
    def adapt_parameters(self, success_rate: float, avg_latency: float, **kwargs) -> Dict[str, float]:
        """自适应参数调整接口"""
        adjustments = {}
        # 根据成功率调整迭代次??        if success_rate < 0.7:
            new_iter = min(self.num_iterations + 10, 200)
            if new_iter != self.num_iterations:
                adjustments['num_iterations'] = new_iter
                self.num_iterations = new_iter
        elif success_rate > 0.95:
            new_iter = max(self.num_iterations - 10, 20)
            if new_iter != self.num_iterations:
                adjustments['num_iterations'] = new_iter
                self.num_iterations = new_iter
        return adjustments
    
    def get_stats(self) -> Dict[str, Any]:
        return self.stats.copy()

# 1. 遗传算法 (Genetic Algorithm)
class GeneticAlgorithmOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__("GeneticAlgorithm", **kwargs)
        self.population_size = kwargs.get('population_size', 50)
        self.crossover_rate = kwargs.get('crossover_rate', 0.8)
        self.mutation_rate = kwargs.get('mutation_rate', 0.1)
        self.elitism_rate = kwargs.get('elitism_rate', 0.1)
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        # 初始化种??        population = []
        for _ in range(self.population_size):
            ind = [random.uniform(low, high) for (low, high) in self.bounds]
            population.append(ind)
        
        for iter in range(self.num_iterations):
            # 计算适应??            fitness = [self.objective_func(ind) for ind in population]
            
            # 记录最优解
            min_idx = np.argmin(fitness)
            if fitness[min_idx] < self.stats['best_fitness']:
                self.stats['best_fitness'] = fitness[min_idx]
                self.stats['best_solution'] = population[min_idx].copy()
            self.stats['history'].append(self.stats['best_fitness'])
            
            if verbose and iter % 10 == 0:
                print(f"GA Iter {iter}: Best Fitness = {self.stats['best_fitness']:.4f}")
            
            # 精英保留
            elite_count = int(self.elitism_rate * self.population_size)
            elite_indices = np.argsort(fitness)[:elite_count]
            new_population = [population[i].copy() for i in elite_indices]
            
            # 选择、交叉、变??            while len(new_population) < self.population_size:
                # 轮盘赌选择
                total_fit = sum(1/(f + 1e-6) for f in fitness)
                p = [ (1/(f + 1e-6))/total_fit for f in fitness ]
                parent1 = population[np.random.choice(len(population), p=p)]
                parent2 = population[np.random.choice(len(population), p=p)]
                
                # 交叉
                if random.random() < self.crossover_rate:
                    point = random.randint(1, self.dimensions-1)
                    child = parent1[:point] + parent2[point:]
                else:
                    child = parent1.copy()
                
                # 变异
                for i in range(self.dimensions):
                    if random.random() < self.mutation_rate:
                        low, high = self.bounds[i]
                        child[i] = random.uniform(low, high)
                
                new_population.append(child)
            
            population = new_population
        
        self.stats['iterations'] = self.num_iterations
        return self.stats['best_solution'], self.stats['best_fitness']

# 2. 模拟退火算??(Simulated Annealing)
class SimulatedAnnealingOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__("SimulatedAnnealing", **kwargs)
        self.initial_temperature = kwargs.get('initial_temperature', 100.0)
        self.cooling_rate = kwargs.get('cooling_rate', 0.95)
        self.min_temperature = kwargs.get('min_temperature', 1e-8)
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        # 初始化当前解
        current = [random.uniform(low, high) for (low, high) in self.bounds]
        current_fitness = self.objective_func(current)
        self.stats['best_solution'] = current.copy()
        self.stats['best_fitness'] = current_fitness
        temperature = self.initial_temperature
        
        iter = 0
        while temperature > self.min_temperature and iter < self.num_iterations:
            # 生成邻域??            neighbor = current.copy()
            idx = random.randint(0, self.dimensions-1)
            low, high = self.bounds[idx]
            neighbor[idx] += random.uniform(-(high-low)*0.1, (high-low)*0.1)
            neighbor[idx] = max(low, min(high, neighbor[idx]))
            
            neighbor_fitness = self.objective_func(neighbor)
            delta = neighbor_fitness - current_fitness
            
            # 接受准则
            if delta < 0 or random.random() < math.exp(-delta / temperature):
                current = neighbor
                current_fitness = neighbor_fitness
                
                if current_fitness < self.stats['best_fitness']:
                    self.stats['best_solution'] = current.copy()
                    self.stats['best_fitness'] = current_fitness
            
            self.stats['history'].append(self.stats['best_fitness'])
            
            if verbose and iter % 10 == 0:
                print(f"SA Iter {iter}, Temp {temperature:.2f}: Best Fitness = {self.stats['best_fitness']:.4f}")
            
            temperature *= self.cooling_rate
            iter += 1
        
        self.stats['iterations'] = iter
        return self.stats['best_solution'], self.stats['best_fitness']

# 3. 禁忌搜索算法 (Tabu Search)
class TabuSearchOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__("TabuSearch", **kwargs)
        self.tabu_size = kwargs.get('tabu_size', 10)
        self.neighborhood_size = kwargs.get('neighborhood_size', 20)
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        # 初始??        current = [random.uniform(low, high) for (low, high) in self.bounds]
        current_fitness = self.objective_func(current)
        self.stats['best_solution'] = current.copy()
        self.stats['best_fitness'] = current_fitness
        
        tabu_list = []
        
        for iter in range(self.num_iterations):
            # 生成邻域??            neighbors = []
            for _ in range(self.neighborhood_size):
                neighbor = current.copy()
                idx = random.randint(0, self.dimensions-1)
                low, high = self.bounds[idx]
                neighbor[idx] += random.uniform(-(high-low)*0.1, (high-low)*0.1)
                neighbor[idx] = max(low, min(high, neighbor[idx]))
                neighbors.append((neighbor, self.objective_func(neighbor)))
            
            # 排序邻域??            neighbors.sort(key=lambda x: x[1])
            
            # 选择非禁忌最优解或特??            best_neighbor = None
            best_fitness = float('inf')
            for n, f in neighbors:
                n_tuple = tuple(round(x, 4) for x in n)
                if n_tuple not in tabu_list or f < self.stats['best_fitness']:
                    best_neighbor = n
                    best_fitness = f
                    break
            
            if best_neighbor is None:
                best_neighbor, best_fitness = neighbors[0]
            
            # 更新当前解和禁忌??            current = best_neighbor
            current_fitness = best_fitness
            tabu_list.append(tuple(round(x, 4) for x in current))
            if len(tabu_list) > self.tabu_size:
                tabu_list.pop(0)
            
            # 更新全局最??            if current_fitness < self.stats['best_fitness']:
                self.stats['best_solution'] = current.copy()
                self.stats['best_fitness'] = current_fitness
            
            self.stats['history'].append(self.stats['best_fitness'])
            
            if verbose and iter % 10 == 0:
                print(f"TS Iter {iter}: Best Fitness = {self.stats['best_fitness']:.4f}")
        
        self.stats['iterations'] = self.num_iterations
        return self.stats['best_solution'], self.stats['best_fitness']

# 4. 差分进化算法 (Differential Evolution)
class DifferentialEvolutionOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__("DifferentialEvolution", **kwargs)
        self.population_size = kwargs.get('population_size', 50)
        self.mutation_factor = kwargs.get('mutation_factor', 0.8)
        self.crossover_rate = kwargs.get('crossover_rate', 0.7)
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        # 初始化种??        population = []
        for _ in range(self.population_size):
            ind = [random.uniform(low, high) for (low, high) in self.bounds]
            population.append(ind)
        
        for iter in range(self.num_iterations):
            new_population = []
            for i in range(self.population_size):
                # 选择3个不同的个体
                candidates = [j for j in range(self.population_size) if j != i]
                a, b, c = random.sample(candidates, 3)
                
                # 变异
                mutant = [
                    population[a][d] + self.mutation_factor * (population[b][d] - population[c][d])
                    for d in range(self.dimensions)
                ]
                # 边界处理
                for d in range(self.dimensions):
                    low, high = self.bounds[d]
                    mutant[d] = max(low, min(high, mutant[d]))
                
                # 交叉
                trial = []
                j_rand = random.randint(0, self.dimensions-1)
                for d in range(self.dimensions):
                    if random.random() < self.crossover_rate or d == j_rand:
                        trial.append(mutant[d])
                    else:
                        trial.append(population[i][d])
                
                # 选择
                trial_fitness = self.objective_func(trial)
                target_fitness = self.objective_func(population[i])
                if trial_fitness < target_fitness:
                    new_population.append(trial)
                else:
                    new_population.append(population[i])
            
            population = new_population
            
            # 记录最??            fitness = [self.objective_func(ind) for ind in population]
            min_idx = np.argmin(fitness)
            if fitness[min_idx] < self.stats['best_fitness']:
                self.stats['best_fitness'] = fitness[min_idx]
                self.stats['best_solution'] = population[min_idx].copy()
            
            self.stats['history'].append(self.stats['best_fitness'])
            
            if verbose and iter % 10 == 0:
                print(f"DE Iter {iter}: Best Fitness = {self.stats['best_fitness']:.4f}")
        
        self.stats['iterations'] = self.num_iterations
        return self.stats['best_solution'], self.stats['best_fitness']

# 5. 人工免疫算法 (Artificial Immune Algorithm)
class ArtificialImmuneOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__("ArtificialImmune", **kwargs)
        self.population_size = kwargs.get('population_size', 50)
        self.clone_rate = kwargs.get('clone_rate', 0.5)
        self.mutation_rate = kwargs.get('mutation_rate', 0.2)
        self.suppression_threshold = kwargs.get('suppression_threshold', 0.1)
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        # 初始化种??        population = []
        for _ in range(self.population_size):
            ind = [random.uniform(low, high) for (low, high) in self.bounds]
            population.append(ind)
        
        for iter in range(self.num_iterations):
            # 计算亲和??            affinity = [1/(self.objective_func(ind) + 1e-6) for ind in population]
            
            # 克隆选择
            clone_count = int(self.clone_rate * self.population_size)
            top_indices = np.argsort(affinity)[-clone_count:]
            clones = []
            for i in top_indices:
                clones.append(population[i].copy())
            
            # 高频变异
            for clone in clones:
                for i in range(self.dimensions):
                    if random.random() < self.mutation_rate:
                        low, high = self.bounds[i]
                        clone[i] += random.uniform(-(high-low)*0.1, (high-low)*0.1)
                        clone[i] = max(low, min(high, clone[i]))
            
            # 合并种群
            population += clones
            
            # 计算新的亲和??            affinity = [1/(self.objective_func(ind) + 1e-6) for ind in population]
            
            # 免疫抑制：删除相似个??            unique = []
            for i in range(len(population)):
                duplicate = False
                for j in range(len(unique)):
                    dist = np.linalg.norm(np.array(population[i]) - np.array(unique[j]))
                    if dist < self.suppression_threshold:
                        duplicate = True
                        break
                if not duplicate:
                    unique.append(population[i])
            
            # 选择最优个??            population = sorted(unique, key=lambda x: self.objective_func(x))[:self.population_size]
            
            # 记录最??            current_best_fitness = self.objective_func(population[0])
            if current_best_fitness < self.stats['best_fitness']:
                self.stats['best_fitness'] = current_best_fitness
                self.stats['best_solution'] = population[0].copy()
            
            self.stats['history'].append(self.stats['best_fitness'])
            
            if verbose and iter % 10 == 0:
                print(f"AIA Iter {iter}: Best Fitness = {self.stats['best_fitness']:.4f}")
        
        self.stats['iterations'] = self.num_iterations
        return self.stats['best_solution'], self.stats['best_fitness']

# 6. 鱼群算法 (Fish Swarm Algorithm)
class FishSwarmOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__("FishSwarm", **kwargs)
        self.fish_count = kwargs.get('fish_count', 50)
        self.visual = kwargs.get('visual', 2.0)
        self.step = kwargs.get('step', 0.5)
        self.try_number = kwargs.get('try_number', 10)
        self.delta = kwargs.get('delta', 0.618)
    
    def _distance(self, a, b):
        return np.linalg.norm(np.array(a) - np.array(b))
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        # 初始化鱼??        fish = []
        for _ in range(self.fish_count):
            ind = [random.uniform(low, high) for (low, high) in self.bounds]
            fish.append(ind)
        
        for iter in range(self.num_iterations):
            new_fish = []
            for i in range(self.fish_count):
                current = fish[i]
                current_fitness = self.objective_func(current)
                
                # 觅食行为
                found = False
                for _ in range(self.try_number):
                    random_dir = [random.uniform(-self.visual, self.visual) for _ in range(self.dimensions)]
                    next_pos = [current[d] + random_dir[d] for d in range(self.dimensions)]
                    for d in range(self.dimensions):
                        low, high = self.bounds[d]
                        next_pos[d] = max(low, min(high, next_pos[d]))
                    next_fitness = self.objective_func(next_pos)
                    if next_fitness < current_fitness:
                        step_dir = [next_pos[d] - current[d] for d in range(self.dimensions)]
                        step_len = np.linalg.norm(step_dir)
                        if step_len > 0:
                            step_dir = [d/step_len * self.step for d in step_dir]
                        new_pos = [current[d] + step_dir[d] for d in range(self.dimensions)]
                        for d in range(self.dimensions):
                            low, high = self.bounds[d]
                            new_pos[d] = max(low, min(high, new_pos[d]))
                        new_fish.append(new_pos)
                        found = True
                        break
                if found:
                    continue
                
                # 聚群行为
                neighbors = []
                for j in range(self.fish_count):
                    if i != j and self._distance(current, fish[j]) < self.visual:
                        neighbors.append(fish[j])
                if len(neighbors) > 0:
                    center = np.mean(neighbors, axis=0).tolist()
                    center_fitness = self.objective_func(center)
                    if center_fitness < current_fitness and len(neighbors)/self.fish_count < self.delta:
                        step_dir = [center[d] - current[d] for d in range(self.dimensions)]
                        step_len = np.linalg.norm(step_dir)
                        if step_len > 0:
                            step_dir = [d/step_len * self.step for d in step_dir]
                        new_pos = [current[d] + step_dir[d] for d in range(self.dimensions)]
                        for d in range(self.dimensions):
                            low, high = self.bounds[d]
                            new_pos[d] = max(low, min(high, new_pos[d]))
                        new_fish.append(new_pos)
                        continue
                
                # 追尾行为
                best_neighbor_fitness = float('inf')
                best_neighbor = None
                for j in range(self.fish_count):
                    if i != j and self._distance(current, fish[j]) < self.visual:
                        f = self.objective_func(fish[j])
                        if f < best_neighbor_fitness:
                            best_neighbor_fitness = f
                            best_neighbor = fish[j]
                if best_neighbor is not None:
                    step_dir = [best_neighbor[d] - current[d] for d in range(self.dimensions)]
                    step_len = np.linalg.norm(step_dir)
                    if step_len > 0:
                        step_dir = [d/step_len * self.step for d in step_dir]
                    new_pos = [current[d] + step_dir[d] for d in range(self.dimensions)]
                    for d in range(self.dimensions):
                        low, high = self.bounds[d]
                        new_pos[d] = max(low, min(high, new_pos[d]))
                    new_fish.append(new_pos)
                    continue
                
                # 随机移动
                random_dir = [random.uniform(-self.step, self.step) for _ in range(self.dimensions)]
                new_pos = [current[d] + random_dir[d] for d in range(self.dimensions)]
                for d in range(self.dimensions):
                    low, high = self.bounds[d]
                    new_pos[d] = max(low, min(high, new_pos[d]))
                new_fish.append(new_pos)
            
            fish = new_fish
            
            # 记录最??            fitness = [self.objective_func(f) for f in fish]
            min_idx = np.argmin(fitness)
            if fitness[min_idx] < self.stats['best_fitness']:
                self.stats['best_fitness'] = fitness[min_idx]
                self.stats['best_solution'] = fish[min_idx].copy()
            
            self.stats['history'].append(self.stats['best_fitness'])
            
            if verbose and iter % 10 == 0:
                print(f"FSA Iter {iter}: Best Fitness = {self.stats['best_fitness']:.4f}")
        
        self.stats['iterations'] = self.num_iterations
        return self.stats['best_solution'], self.stats['best_fitness']

# 7. 烟花算法 (Fireworks Algorithm)
class FireworksAlgorithmOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__("FireworksAlgorithm", **kwargs)
        self.num_fireworks = kwargs.get('num_fireworks', 5)
        self.max_sparks = kwargs.get('max_sparks', 50)
        self.a = kwargs.get('a', 0.04)
        self.b = kwargs.get('b', 0.8)
        self.A = kwargs.get('A', 40)
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        # 初始化烟??        fireworks = []
        for _ in range(self.num_fireworks):
            ind = [random.uniform(low, high) for (low, high) in self.bounds]
            fireworks.append(ind)
        
        for iter in range(self.num_iterations):
            sparks = []
            fitness = [self.objective_func(fw) for fw in fireworks]
            min_fit = min(fitness)
            max_fit = max(fitness)
            
            for i, fw in enumerate(fireworks):
                # 计算火花数量
                s = self.max_sparks * (max_fit - fitness[i] + 1e-6) / (max_fit - min_fit + 1e-6)
                s = int(max(self.a * self.max_sparks, min(s, self.b * self.max_sparks)))
                
                # 计算爆炸幅度
                amp = self.A * (fitness[i] - min_fit + 1e-6) / (max_fit - min_fit + 1e-6)
                
                # 生成普通火??                for _ in range(s):
                    spark = fw.copy()
                    # 随机选择维度
                    z = random.randint(1, self.dimensions)
                    dims = random.sample(range(self.dimensions), z)
                    for d in dims:
                        offset = random.uniform(-amp, amp)
                        spark[d] += offset
                        low, high = self.bounds[d]
                        spark[d] = max(low, min(high, spark[d]))
                    sparks.append(spark)
            
            # 生成高斯火花
            gaussian_count = self.num_fireworks
            for _ in range(gaussian_count):
                fw = random.choice(fireworks)
                spark = fw.copy()
                z = random.randint(1, self.dimensions)
                dims = random.sample(range(self.dimensions), z)
                for d in dims:
                    spark[d] *= random.gauss(1, 1)
                    low, high = self.bounds[d]
                    spark[d] = max(low, min(high, spark[d]))
                sparks.append(spark)
            
            # 合并并选择下一??            all_candidates = fireworks + sparks
            all_fitness = [self.objective_func(c) for c in all_candidates]
            sorted_indices = np.argsort(all_fitness)
            fireworks = [all_candidates[i] for i in sorted_indices[:self.num_fireworks]]
            
            # 记录最??            if all_fitness[sorted_indices[0]] < self.stats['best_fitness']:
                self.stats['best_fitness'] = all_fitness[sorted_indices[0]]
                self.stats['best_solution'] = all_candidates[sorted_indices[0]].copy()
            
            self.stats['history'].append(self.stats['best_fitness'])
            
            if verbose and iter % 10 == 0:
                print(f"FWA Iter {iter}: Best Fitness = {self.stats['best_fitness']:.4f}")
        
        self.stats['iterations'] = self.num_iterations
        return self.stats['best_solution'], self.stats['best_fitness']

# 8. 布谷鸟搜索算??(Cuckoo Search)
class CuckooSearchOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__("CuckooSearch", **kwargs)
        self.population_size = kwargs.get('population_size', 50)
        self.pa = kwargs.get('pa', 0.25)  # 宿主发现鸟蛋的概??    
    def _levy_flight(self, dim):
        beta = 1.5
        sigma = (math.gamma(1 + beta) * math.sin(math.pi * beta / 2) / 
                 (math.gamma((1 + beta)/2) * beta * 2**((beta-1)/2))) ** (1/beta)
        u = np.random.normal(0, sigma, dim)
        v = np.random.normal(0, 1, dim)
        step = u / np.power(np.abs(v), 1/beta)
        return step
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        # 初始化种??        nests = []
        for _ in range(self.population_size):
            ind = [random.uniform(low, high) for (low, high) in self.bounds]
            nests.append(ind)
        
        # 记录初始最??        fitness = [self.objective_func(nest) for nest in nests]
        min_idx = np.argmin(fitness)
        self.stats['best_solution'] = nests[min_idx].copy()
        self.stats['best_fitness'] = fitness[min_idx]
        
        for iter in range(self.num_iterations):
            # 生成新解
            new_nests = []
            for nest in nests:
                step = self._levy_flight(self.dimensions)
                new_nest = [nest[d] + step[d] * 0.01 * (self.bounds[d][1] - self.bounds[d][0]) for d in range(self.dimensions)]
                for d in range(self.dimensions):
                    low, high = self.bounds[d]
                    new_nest[d] = max(low, min(high, new_nest[d]))
                new_nests.append(new_nest)
            
            # 评价新解
            new_fitness = [self.objective_func(n) for n in new_nests]
            for i in range(self.population_size):
                if new_fitness[i] < fitness[i]:
                    nests[i] = new_nests[i]
                    fitness[i] = new_fitness[i]
            
            # 发现并替换最差巢??            abandon_count = int(self.pa * self.population_size)
            worst_indices = np.argsort(fitness)[-abandon_count:]
            for i in worst_indices:
                nests[i] = [random.uniform(low, high) for (low, high) in self.bounds]
                fitness[i] = self.objective_func(nests[i])
            
            # 更新最??            min_idx = np.argmin(fitness)
            if fitness[min_idx] < self.stats['best_fitness']:
                self.stats['best_fitness'] = fitness[min_idx]
                self.stats['best_solution'] = nests[min_idx].copy()
            
            self.stats['history'].append(self.stats['best_fitness'])
            
            if verbose and iter % 10 == 0:
                print(f"CS Iter {iter}: Best Fitness = {self.stats['best_fitness']:.4f}")
        
        self.stats['iterations'] = self.num_iterations
        return self.stats['best_solution'], self.stats['best_fitness']

# 9. 蝙蝠算法 (Bat Algorithm)
class BatAlgorithmOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__("BatAlgorithm", **kwargs)
        self.num_bats = kwargs.get('num_bats', 50)
        self.loudness = kwargs.get('loudness', 1.0)
        self.pulse_rate = kwargs.get('pulse_rate', 0.5)
        self.alpha = kwargs.get('alpha', 0.9)
        self.gamma = kwargs.get('gamma', 0.9)
        self.f_min = kwargs.get('f_min', 0)
        self.f_max = kwargs.get('f_max', 10)
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        # 初始化蝙??        bats = []
        velocities = []
        frequencies = []
        loudnesses = [self.loudness] * self.num_bats
        pulse_rates = [self.pulse_rate] * self.num_bats
        
        for _ in range(self.num_bats):
            pos = [random.uniform(low, high) for (low, high) in self.bounds]
            bats.append(pos)
            velocities.append([0.0] * self.dimensions)
            frequencies.append(random.uniform(self.f_min, self.f_max))
        
        # 初始最??        fitness = [self.objective_func(b) for b in bats]
        min_idx = np.argmin(fitness)
        self.stats['best_solution'] = bats[min_idx].copy()
        self.stats['best_fitness'] = fitness[min_idx]
        
        for iter in range(self.num_iterations):
            for i in range(self.num_bats):
                # 调整频率
                frequencies[i] = self.f_min + (self.f_max - self.f_min) * random.random()
                
                # 更新速度和位??                for d in range(self.dimensions):
                    velocities[i][d] += (bats[i][d] - self.stats['best_solution'][d]) * frequencies[i]
                    bats[i][d] += velocities[i][d]
                    low, high = self.bounds[d]
                    bats[i][d] = max(low, min(high, bats[i][d]))
                
                # 局部搜??                if random.random() > pulse_rates[i]:
                    step = random.uniform(-1, 1) * np.mean(loudnesses)
                    new_pos = [self.stats['best_solution'][d] + step * random.uniform(-1,1) for d in range(self.dimensions)]
                    for d in range(self.dimensions):
                        low, high = self.bounds[d]
                        new_pos[d] = max(low, min(high, new_pos[d]))
                else:
                    new_pos = bats[i].copy()
                
                # 评估新解
                new_fitness = self.objective_func(new_pos)
                
                # 接受准则
                if (new_fitness < fitness[i]) and (random.random() < loudnesses[i]):
                    bats[i] = new_pos
                    fitness[i] = new_fitness
                    loudnesses[i] *= self.alpha
                    pulse_rates[i] = self.pulse_rate * (1 - math.exp(-self.gamma * iter))
                
                # 更新全局最??                if new_fitness < self.stats['best_fitness']:
                    self.stats['best_fitness'] = new_fitness
                    self.stats['best_solution'] = new_pos.copy()
            
            self.stats['history'].append(self.stats['best_fitness'])
            
            if verbose and iter % 10 == 0:
                print(f"BA Iter {iter}: Best Fitness = {self.stats['best_fitness']:.4f}")
        
        self.stats['iterations'] = self.num_iterations
        return self.stats['best_solution'], self.stats['best_fitness']

# 10. 灰狼优化算法 (Grey Wolf Optimizer)
class GreyWolfOptimizer(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__("GreyWolfOptimizer", **kwargs)
        self.pack_size = kwargs.get('pack_size', 50)
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        # 初始化狼??        pack = []
        for _ in range(self.pack_size):
            ind = [random.uniform(low, high) for (low, high) in self.bounds]
            pack.append(ind)
        
        # 初始化Alpha, Beta, Delta??        fitness = [self.objective_func(wolf) for wolf in pack]
        sorted_indices = np.argsort(fitness)
        alpha = pack[sorted_indices[0]].copy()
        alpha_fit = fitness[sorted_indices[0]]
        beta = pack[sorted_indices[1]].copy()
        beta_fit = fitness[sorted_indices[1]]
        delta = pack[sorted_indices[2]].copy()
        delta_fit = fitness[sorted_indices[2]]
        
        self.stats['best_solution'] = alpha.copy()
        self.stats['best_fitness'] = alpha_fit
        
        for iter in range(self.num_iterations):
            a = 2 - iter * (2 / self.num_iterations)  # 线性递减
            
            for i in range(self.pack_size):
                # 计算A和C系数
                A1 = 2 * a * random.random() - a
                C1 = 2 * random.random()
                A2 = 2 * a * random.random() - a
                C2 = 2 * random.random()
                A3 = 2 * a * random.random() - a
                C3 = 2 * random.random()
                
                # 向Alpha, Beta, Delta移动
                D_alpha = [abs(C1 * alpha[d] - pack[i][d]) for d in range(self.dimensions)]
                X1 = [alpha[d] - A1 * D_alpha[d] for d in range(self.dimensions)]
                
                D_beta = [abs(C2 * beta[d] - pack[i][d]) for d in range(self.dimensions)]
                X2 = [beta[d] - A2 * D_beta[d] for d in range(self.dimensions)]
                
                D_delta = [abs(C3 * delta[d] - pack[i][d]) for d in range(self.dimensions)]
                X3 = [delta[d] - A3 * D_delta[d] for d in range(self.dimensions)]
                
                # 更新位置
                pack[i] = [(X1[d] + X2[d] + X3[d])/3 for d in range(self.dimensions)]
                # 边界处理
                for d in range(self.dimensions):
                    low, high = self.bounds[d]
                    pack[i][d] = max(low, min(high, pack[i][d]))
            
            # 更新Alpha, Beta, Delta
            fitness = [self.objective_func(wolf) for wolf in pack]
            sorted_indices = np.argsort(fitness)
            if fitness[sorted_indices[0]] < alpha_fit:
                alpha = pack[sorted_indices[0]].copy()
                alpha_fit = fitness[sorted_indices[0]]
            if fitness[sorted_indices[1]] < beta_fit:
                beta = pack[sorted_indices[1]].copy()
                beta_fit = fitness[sorted_indices[1]]
            if fitness[sorted_indices[2]] < delta_fit:
                delta = pack[sorted_indices[2]].copy()
                delta_fit = fitness[sorted_indices[2]]
            
            # 更新全局最??            if alpha_fit < self.stats['best_fitness']:
                self.stats['best_fitness'] = alpha_fit
                self.stats['best_solution'] = alpha.copy()
            
            self.stats['history'].append(self.stats['best_fitness'])
            
            if verbose and iter % 10 == 0:
                print(f"GWO Iter {iter}: Best Fitness = {self.stats['best_fitness']:.4f}")
        
        self.stats['iterations'] = self.num_iterations
        return self.stats['best_solution'], self.stats['best_fitness']

# 11. 鲸鱼优化算法 (Whale Optimization Algorithm)
class WhaleOptimizationAlgorithm(BaseOptimizer):
    def __init__(self, **kwargs):
        super().__init__("WhaleOptimizationAlgorithm", **kwargs)
        self.population_size = kwargs.get('population_size', 50)
        self.b = kwargs.get('b', 1.0)  # 螺旋形状常数
    
    def run(self, verbose: bool = False) -> Tuple[List[float], float]:
        # 初始化鲸鱼种??        whales = []
        for _ in range(self.population_size):
            ind = [random.uniform(low, high) for (low, high) in self.bounds]
            whales.append(ind)
        
        # 初始最??        fitness = [self.objective_func(w) for w in whales]
        min_idx = np.argmin(fitness)
        self.stats['best_solution'] = whales[min_idx].copy()
        self.stats['best_fitness'] = fitness[min_idx]
        
        for iter in range(self.num_iterations):
            a = 2 - iter * (2 / self.num_iterations)
            
            for i in range(self.population_size):
                r1 = random.random()
                r2 = random.random()
                A = 2 * a * r1 - a
                C = 2 * r2
                p = random.random()
                
                if p < 0.5:
                    if abs(A) < 1:
                        # 包围猎物
                        D = [abs(C * self.stats['best_solution'][d] - whales[i][d]) for d in range(self.dimensions)]
                        whales[i] = [self.stats['best_solution'][d] - A * D[d] for d in range(self.dimensions)]
                    else:
                        # 随机选择鲸鱼
                        rand_idx = random.randint(0, self.population_size-1)
                        rand_whale = whales[rand_idx]
                        D = [abs(C * rand_whale[d] - whales[i][d]) for d in range(self.dimensions)]
                        whales[i] = [rand_whale[d] - A * D[d] for d in range(self.dimensions)]
                else:
                    # 泡泡网攻击（螺旋更新??                    D = [abs(self.stats['best_solution'][d] - whales[i][d]) for d in range(self.dimensions)]
                    l = random.uniform(-1, 1)
                    whales[i] = [
                        D[d] * math.exp(self.b * l) * math.cos(2 * math.pi * l) + self.stats['best_solution'][d]
                        for d in range(self.dimensions)
                    ]
                
                # 边界处理
                for d in range(self.dimensions):
                    low, high = self.bounds[d]
                    whales[i][d] = max(low, min(high, whales[i][d]))
            
            # 评估新位??            fitness = [self.objective_func(w) for w in whales]
            min_idx = np.argmin(fitness)
            if fitness[min_idx] < self.stats['best_fitness']:
                self.stats['best_fitness'] = fitness[min_idx]
                self.stats['best_solution'] = whales[min_idx].copy()
            
            self.stats['history'].append(self.stats['best_fitness'])
            
            if verbose and iter % 10 == 0:
                print(f"WOA Iter {iter}: Best Fitness = {self.stats['best_fitness']:.4f}")
        
        self.stats['iterations'] = self.num_iterations
        return self.stats['best_solution'], self.stats['best_fitness']

# 导出所有算??__all__ = [
    'GeneticAlgorithmOptimizer',
    'SimulatedAnnealingOptimizer',
    'TabuSearchOptimizer',
    'DifferentialEvolutionOptimizer',
    'ArtificialImmuneOptimizer',
    'FishSwarmOptimizer',
    'FireworksAlgorithmOptimizer',
    'CuckooSearchOptimizer',
    'BatAlgorithmOptimizer',
    'GreyWolfOptimizer',
    'WhaleOptimizationAlgorithm',
]
