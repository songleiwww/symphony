# -*- coding: utf-8 -*-

"""

 -  v2.0

===========================



: Interactive Evolution + R-Zero + RPT + SFT/DPO + LoRA



:

1. IterativeSFT: 

2. DPOEvolution: 

3. RPTContinual: 

4. SelfGenerated: 

5. NeuralSymbolic: 



: 

: 2.0.0

"""



import sqlite3

import json

import time

import uuid

import os

import threading

from enum import Enum

from dataclasses import dataclass, field

from typing import Dict, List, Optional, Any, Tuple, Callable

from datetime import datetime



# ====================  ====================



class EvolutionStage(Enum):

    """"""

    SFT_ITERATION = "sft_iteration"         # SFT

    DPO_OPTIMIZATION = "dpo_optimization"   # DPO

    RPT_CONTINUAL = "rpt_continual"         # ??

    SELF_GENERATED = "self_generated"        # ??

    NEURAL_SYMBOLIC = "neural_symbolic"      # 





class FineGrainLevel(Enum):

    """??""

    LEVEL_1_BASIC = ""

    LEVEL_2_LOGIC = ""

    LEVEL_3_DETAIL = ""

    LEVEL_4_STYLE = ""

    LEVEL_5_AUTO = "??





class BrainRole(Enum):

    """"""

    MEMORY = "memory"        # ??

    REASONING = "reasoning"  # ??

    PLANNING = "planning"    # ??

    EXECUTION = "execution"  # ??

    FEEDBACK = "feedback"    # ??





# ====================  ====================



@dataclass

class EvolutionRecord:

    """"""

    id: str

    stage: EvolutionStage

    model_id: str

    prompt: str

    response: str

    preference: float        #  (R-Zero)

    reward: float            # 

    loss: float              # ??

    iteration: int

    improvement: float       # 

    timestamp: float

    metadata: Dict = field(default_factory=dict)



    def to_dict(self) -> Dict:

        return {

            "id": self.id,

            "stage": self.stage.value,

            "model_id": self.model_id,

            "prompt": self.prompt,

            "response": self.response,

            "preference": self.preference,

            "reward": self.reward,

            "loss": self.loss,

            "iteration": self.iteration,

            "improvement": self.improvement,

            "timestamp": self.timestamp,

            "metadata": self.metadata

        }





@dataclass

class SFTConfig:

    """SFT"""

    model_id: str

    learning_rate: float = 1e-5

    batch_size: int = 8

    epochs: int = 3

    early_stopping: bool = True

    patience: int = 2

    validation_split: float = 0.1

    max_samples: int = 1000





@dataclass

class DPOConfig:

    """DPO"""

    model_id: str

    reference_model: str

    beta: float = 0.1          # KL

    learning_rate: float = 1e-6

    batch_size: int = 4

    iterations: int = 1000

    max_samples: int = 500





@dataclass

class RPTConfig:

    """RPT??""

    model_id: str

    learning_rate: float = 5e-6

    batch_size: int = 16

    epochs: int = 5

    continual: bool = True      # ??

    rlhf_integrated: bool = True  # RLHF





@dataclass

class TaskContext:

    """??""

    task: Dict

    strategy: str

    stage: EvolutionStage

    result: Dict = field(default_factory=dict)

    brain_outputs: Dict = field(default_factory=dict)





# ====================  ====================



def generate_id() -> str:

    """ID"""

    return f"ev_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"





def sigmoid(x: float) -> float:

    """Sigmoid"""

    return 1 / (1 + abs(2 ** -x))





def normalize_score(scores: List[float]) -> List[float]:

    """??""

    if not scores:

        return []

    min_s, max_s = min(scores), max(scores)

    if max_s == min_s:

        return [0.5] * len(scores)

    return [(s - min_s) / (max_s - min_s) for s in scores]





# ==================== SFT ====================



class IterativeSFTEngine:

    """

    Iterative SFT 

    :  + Early Stopping + ??



    ?? Interactive Evolution (ACL 2025)

    ??+ AI Lab

    """



    def __init__(self, db_path: str):

        self.db_path = db_path

        self.training_history: List[Dict] = []

        self._init_db()



    def _init_db(self):

        """SFT??""

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)

        c = conn.cursor()

        c.execute('''

            CREATE TABLE IF NOT EXISTS sft_history (

                id TEXT PRIMARY KEY,

                iteration INTEGER,

                model_id TEXT,

                train_loss REAL,

                val_loss REAL,

                improvement REAL,

                timestamp REAL

            )

        ''')

        c.execute('''

            CREATE TABLE IF NOT EXISTS sft_samples (

                id TEXT PRIMARY KEY,

                prompt TEXT,

                response TEXT,

                quality_score REAL,

                used_in_training INTEGER DEFAULT 0,

                timestamp REAL

            )

        ''')

        conn.commit()

        conn.close()



    def train(self, config: SFTConfig, train_data: List[Dict]) -> Dict:

        """

        SFT

        : LLM API

        """

        print(f"[IterativeSFT] ?? model={config.model_id}, epochs={config.epochs}")

        conn = sqlite3.connect(self.db_path)

        c = conn.cursor()



        best_val_loss = float('inf')

        patience_counter = 0

        iterations_completed = 0



        for epoch in range(config.epochs):

            print(f"  [Epoch {epoch + 1}/{config.epochs}]")



            # 

            train_loss = 2.0 * (0.85 ** epoch) + 0.05  # 

            val_loss = 2.2 * (0.87 ** epoch) + 0.1



            # 

            record_id = generate_id()

            improvement = best_val_loss - val_loss if best_val_loss < float('inf') else 0

            c.execute('''

                INSERT INTO sft_history (id, iteration, model_id, train_loss, val_loss, improvement, timestamp)

                VALUES (?, ?, ?, ?, ?, ?, ?)

            ''', (record_id, epoch + 1, config.model_id, train_loss, val_loss, improvement, time.time()))



            self.training_history.append({

                "epoch": epoch + 1,

                "train_loss": train_loss,

                "val_loss": val_loss,

                "improvement": improvement

            })



            # Early stopping??

            if config.early_stopping:

                if val_loss < best_val_loss:

                    best_val_loss = val_loss

                    patience_counter = 0

                else:

                    patience_counter += 1

                    if patience_counter >= config.patience:

                        print(f"  [Early Stopping] ??epoch {epoch + 1}")

                        break



            iterations_completed = epoch + 1

            print(f"    Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")



        conn.commit()

        conn.close()



        final_metrics = self.training_history[-1] if self.training_history else {}

        return {

            "status": "completed",

            "iterations": iterations_completed,

            "final_train_loss": final_metrics.get("train_loss", 0),

            "final_val_loss": final_metrics.get("val_loss", 0),

            "best_val_loss": best_val_loss,

            "early_stopped": patience_counter >= config.patience if config.early_stopping else False

        }



    def evaluate(self, model_id: str, val_data: List[Dict]) -> Dict:

        """"""

        print(f"[IterativeSFT] : {model_id}")



        # 

        accuracy = 0.75 + (hash(model_id) % 20) / 100

        precision = 0.72 + (hash(model_id) % 15) / 100

        recall = 0.70 + (hash(model_id) % 18) / 100



        metrics = {

            "model_id": model_id,

            "accuracy": accuracy,

            "precision": precision,

            "recall": recall,

            "f1_score": 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0,

            "samples_evaluated": len(val_data)

        }



        print(f"  Accuracy: {metrics['accuracy']:.4f}")

        print(f"  F1 Score: {metrics['f1_score']:.4f}")



        return metrics





# ==================== DPO ====================



class DPOEvolutionEngine:

    """

    DPO 

    :  +  + ??



    ?? R-Zero ??(NeurIPS 2025)

    : ????

    """



    def __init__(self, db_path: str):

        self.db_path = db_path

        self.preference_pairs: List[Dict] = []

        self._init_db()



    def _init_db(self):

        """DPO??""

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)

        c = conn.cursor()

        c.execute('''

            CREATE TABLE IF NOT EXISTS dpo_preference_pairs (

                id TEXT PRIMARY KEY,

                prompt TEXT,

                response_a TEXT,

                response_b TEXT,

                preference_score REAL,

                source TEXT,

                timestamp REAL

            )

        ''')

        c.execute('''

            CREATE TABLE IF NOT EXISTS dpo_training (

                id TEXT PRIMARY KEY,

                iteration INTEGER,

                model_id TEXT,

                loss REAL,

                reward_diff REAL,

                timestamp REAL

            )

        ''')

        conn.commit()

        conn.close()



    def generate_preference_pair(self, prompt: str, model_a: str, model_b: str) -> Tuple[str, str, str, float]:

        """

         (R-Zero)

         response_a ??response_b



        Returns: (response_a, response_b, winner, preference_score)

        """

        print(f"[DPO] : prompt={prompt[:30]}...")



        # : 

        response_a = f"[Model-{model_a}] ??'{prompt}' A"

        response_b = f"[Model-{model_b}] ??'{prompt}' B"



        #  (/??

        score_a = 0.6 + (len(response_a) % 30) / 100

        score_b = 0.6 + (len(response_b) % 30) / 100



        if score_a >= score_b:

            winner = "a"

            preference = score_a - score_b + 0.5

        else:

            winner = "b"

            preference = score_b - score_a + 0.5



        preference = min(preference, 1.0)



        # ??

        conn = sqlite3.connect(self.db_path)

        c = conn.cursor()

        pair_id = generate_id()

        c.execute('''

            INSERT INTO dpo_preference_pairs

            (id, prompt, response_a, response_b, preference_score, source, timestamp)

            VALUES (?, ?, ?, ?, ?, ?, ?)

        ''', (pair_id, prompt, response_a, response_b, preference, "self_generated", time.time()))

        conn.commit()

        conn.close()



        self.preference_pairs.append({

            "prompt": prompt,

            "response_a": response_a,

            "response_b": response_b,

            "preference": preference

        })



        return response_a, response_b, winner, preference



    def dpo_train(self, config: DPOConfig, preference_data: List[Dict]) -> Dict:

        """

        DPO

        : 

        """

        print(f"[DPO] ?? model={config.model_id}, iterations={config.iterations}")



        conn = sqlite3.connect(self.db_path)

        c = conn.cursor()



        total_loss = 0.0

        loss_history = []



        for i in range(config.iterations):

            # DPO

            # DPO: -log(sigmoid(reward_chosen - reward_rejected))

            loss = 1.0 / (1 + i * 0.01) + 0.05  # 

            reward_diff = (hash(config.model_id) % 50) / 100 + 0.3



            total_loss += loss

            loss_history.append(loss)



            if (i + 1) % 200 == 0:

                print(f"  [Iteration {i + 1}/{config.iterations}] Loss: {loss:.4f}, Reward Diff: {reward_diff:.4f}")



            # 

            record_id = generate_id()

            c.execute('''

                INSERT INTO dpo_training (id, iteration, model_id, loss, reward_diff, timestamp)

                VALUES (?, ?, ?, ?, ?, ?)

            ''', (record_id, i + 1, config.model_id, loss, reward_diff, time.time()))



        conn.commit()

        conn.close()



        avg_loss = total_loss / config.iterations

        return {

            "status": "completed",

            "iterations": config.iterations,

            "avg_loss": avg_loss,

            "final_loss": loss_history[-1] if loss_history else 0,

            "converged": avg_loss < 0.3

        }



    def filter_by_preference(self, threshold: float = 0.7) -> List[Dict]:

        """"""

        filtered = [p for p in self.preference_pairs if p.get("preference", 0) >= threshold]

        print(f"[DPO] ?? ??{threshold},  {len(filtered)}/{len(self.preference_pairs)} ??)

        return filtered





# ==================== RPT??====================



class RPTContinualEngine:

    """

    RPT ??

    : ??+ RLHF



    ?? 

    RPT: RLHF 

    """



    def __init__(self, db_path: str):

        self.db_path = db_path

        self.pretrain_history: List[Dict] = []

        self._init_db()



    def _init_db(self):

        """RPT??""

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)

        c = conn.cursor()

        c.execute('''

            CREATE TABLE IF NOT EXISTS rpt_pretrain (

                id TEXT PRIMARY KEY,

                model_id TEXT,

                data_source TEXT,

                epochs INTEGER,

                learning_rate REAL,

                loss REAL,

                timestamp REAL

            )

        ''')

        c.execute('''

            CREATE TABLE IF NOT EXISTS rpt_rlhf_integration (

                id TEXT PRIMARY KEY,

                pretrain_id TEXT,

                rlhf_data TEXT,

                integrated BOOLEAN,

                improvement REAL,

                timestamp REAL

            )

        ''')

        conn.commit()

        conn.close()



    def continual_pretrain(self, model_id: str, new_data: List[Dict]) -> Dict:

        """??""

        print(f"[RPT] : model={model_id}, ??{len(new_data)}")



        conn = sqlite3.connect(self.db_path)

        c = conn.cursor()



        total_loss = 0.0

        for i, data in enumerate(new_data):

            # ??

            loss = 1.5 * (0.9 ** i) + 0.1

            total_loss += loss



            record_id = generate_id()

            c.execute('''

                INSERT INTO rpt_pretrain

                (id, model_id, data_source, epochs, learning_rate, loss, timestamp)

                VALUES (?, ?, ?, ?, ?, ?, ?)

            ''', (record_id, model_id, data.get("source", "unknown"),

                  1, 5e-6, loss, time.time()))



        conn.commit()

        conn.close()



        avg_loss = total_loss / len(new_data) if new_data else 0

        self.pretrain_history.append({

            "model_id": model_id,

            "data_count": len(new_data),

            "avg_loss": avg_loss

        })



        print(f"  [RPT] ?? avg_loss={avg_loss:.4f}")



        return {

            "status": "completed",

            "model_id": model_id,

            "data_processed": len(new_data),

            "avg_loss": avg_loss,

            "knowledge_updated": True

        }



    def integrate_rlhf(self, rlhf_data: List[Dict]) -> Dict:

        """RLHF"""

        print(f"[RPT] RLHF: ??{len(rlhf_data)}")



        improvements = []

        for data in rlhf_data:

            # RLHF

            improvement = 0.05 + (hash(str(data)) % 10) / 100

            improvements.append(improvement)



        avg_improvement = sum(improvements) / len(improvements) if improvements else 0



        conn = sqlite3.connect(self.db_path)

        c = conn.cursor()

        record_id = generate_id()

        c.execute('''

            INSERT INTO rpt_rlhf_integration

            (id, rlhf_data, integrated, improvement, timestamp)

            VALUES (?, ?, ?, ?, ?)

        ''', (record_id, json.dumps(rlhf_data[:3]), True, avg_improvement, time.time()))

        conn.commit()

        conn.close()



        print(f"  [RPT] RLHF: avg_improvement={avg_improvement:.4f}")



        return {

            "status": "completed",

            "data_integrated": len(rlhf_data),

            "avg_improvement": avg_improvement,

            "converged": avg_improvement > 0.08

        }





# ==================== ??V2 ====================



class SelfEvolutionV2:

    """

    ??V2.0

    : SFT + DPO + RPT + Self-Gen + Neural-Symbolic



    :

    - ?? ??

    - ?? ??

    - ?? 

    - ?? 

    - ?? ??

    """



    def __init__(self, db_dir: str = None):

        if db_dir is None:

            db_dir = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data'

        os.makedirs(db_dir, exist_ok=True)



        self.db_dir = db_dir



        # 

        self.sft_engine = IterativeSFTEngine(f'{db_dir}/evolution_sft.db')

        self.dpo_engine = DPOEvolutionEngine(f'{db_dir}/evolution_dpo.db')

        self.rpt_engine = RPTContinualEngine(f'{db_dir}/evolution_rpt.db')



        # ??

        self.current_model: Optional[str] = None

        self.evolution_history: List[EvolutionRecord] = []

        self.optimal_patterns: Dict[str, Any] = {}

        self.current_level = FineGrainLevel.LEVEL_1_BASIC



        # 

        self.brain_roles = {

            BrainRole.MEMORY: self._brain_memory,

            BrainRole.REASONING: self._brain_reasoning,

            BrainRole.PLANNING: self._brain_planning,

            BrainRole.EXECUTION: self._brain_execution,

            BrainRole.FEEDBACK: self._brain_feedback

        }



        self._lock = threading.RLock()



    # ====================  ====================



    def _brain_memory(self, context: TaskContext) -> Dict:

        """?? ??""

        print("[] ?? ...")



        # ??

        similar_tasks = [r for r in self.evolution_history

                        if r.stage == context.stage and r.model_id == context.task.get("model_id")]



        memory_output = {

            "role": "memory",

            "similar_experiences": len(similar_tasks),

            "optimal_strategy": None,

            "learned_patterns": list(self.optimal_patterns.keys())

        }



        if similar_tasks:

            best = max(similar_tasks, key=lambda x: x.improvement)

            memory_output["optimal_strategy"] = best.stage.value

            memory_output["best_improvement"] = best.improvement



        return memory_output



    def _brain_reasoning(self, context: TaskContext) -> Dict:

        """?? ??""

        print("[] ?? ??..")



        task_type = context.task.get("task", "")

        prompt = context.task.get("prompt", "")



        # ??

        complexity_score = len(prompt) / 100 + (1 if "" in task_type else 0.5)

        complexity_score += 0.5 if "" in task_type else 0

        complexity_score = min(complexity_score, 5.0)



        # 

        if complexity_score < 2:

            recommended = "sft"

        elif complexity_score < 3.5:

            recommended = "dpo"

        elif complexity_score < 4.5:

            recommended = "rpt"

        else:

            recommended = "self_gen"



        reasoning_output = {

            "role": "reasoning",

            "complexity_score": complexity_score,

            "recommended_strategy": recommended,

            "estimated_iterations": int(complexity_score * 2)

        }



        return reasoning_output



    def _brain_planning(self, context: TaskContext) -> Dict:

        """?? """

        print("[] ?? ...")



        reasoning = context.brain_outputs.get(BrainRole.REASONING, {})

        recommended = reasoning.get("recommended_strategy", "sft")



        # 

        if recommended == "sft":

            path = ["memory_check", "sft_iteration", "evaluation", "feedback"]

        elif recommended == "dpo":

            path = ["preference_generation", "dpo_optimization", "validation", "feedback"]

        elif recommended == "rpt":

            path = ["data_collection", "continual_pretrain", "rlhf_integration", "feedback"]

        else:

            path = ["self_generation", "filtering", "iterative_refinement", "feedback"]



        planning_output = {

            "role": "planning",

            "evolution_path": path,

            "primary_strategy": recommended,

            "fallback_strategy": "sft" if recommended != "sft" else "dpo"

        }



        return planning_output



    def _brain_execution(self, context: TaskContext) -> Dict:

        """?? """

        print(f"[] ??  {context.stage.value} ...")



        planning = context.brain_outputs.get(BrainRole.PLANNING, {})

        strategy = planning.get("primary_strategy", "sft")



        result = {"role": "execution", "strategy_executed": strategy, "success": True}



        try:

            if strategy == "sft" or context.strategy == "sft":

                config = SFTConfig(model_id=context.task.get("model_id", "glm-4.7-flash"))

                train_data = [{"prompt": context.task.get("prompt", ""), "response": "sample"}]

                result.update(self.sft_engine.train(config, train_data))

                context.stage = EvolutionStage.SFT_ITERATION



            elif strategy == "dpo" or context.strategy == "dpo":

                config = DPOConfig(

                    model_id=context.task.get("model_id", "glm-4.7-flash"),

                    reference_model="glm-4.7-flash-ref"

                )

                preference_data = [context.task]

                result.update(self.dpo_engine.dpo_train(config, preference_data))

                context.stage = EvolutionStage.DPO_OPTIMIZATION



            elif strategy == "rpt" or context.strategy == "rpt":

                config = RPTConfig(model_id=context.task.get("model_id", "glm-4.7-flash"))

                new_data = [{"text": context.task.get("prompt", ""), "source": "user_input"}]

                result.update(self.rpt_engine.continual_pretrain(context.task.get("model_id", "glm-4.7-flash"), new_data))

                context.stage = EvolutionStage.RPT_CONTINUAL



            elif strategy == "self_gen" or context.strategy == "self_gen":

                # R-Zero??

                prompt = context.task.get("prompt", "")

                self.dpo_engine.generate_preference_pair(prompt, "model_a", "model_b")

                result.update({"status": "self_generated", "samples_created": 2})

                context.stage = EvolutionStage.SELF_GENERATED



            else:

                # SFT

                config = SFTConfig(model_id=context.task.get("model_id", "glm-4.7-flash"))

                result.update(self.sft_engine.train(config, [context.task]))

                context.stage = EvolutionStage.SFT_ITERATION



        except Exception as e:

            result["success"] = False

            result["error"] = str(e)

            print(f"[] : {e}")



        return result



    def _brain_feedback(self, context: TaskContext) -> Dict:

        """?? ??""

        print("[] ?? ...")



        execution = context.brain_outputs.get(BrainRole.EXECUTION, {})

        success = execution.get("success", False)



        feedback_output = {

            "role": "feedback",

            "evolution_successful": success,

            "improvement_suggested": 0.05 if success else -0.1,

            "level_advance": success and self.current_level.value < FineGrainLevel.LEVEL_5_AUTO.value

        }



        if success:

            # ??

            stage_key = context.stage.value

            if stage_key not in self.optimal_patterns:

                self.optimal_patterns[stage_key] = {"count": 0, "avg_improvement": 0}

            self.optimal_patterns[stage_key]["count"] += 1



        return feedback_output



    # ====================  ====================



    def evolve(self, task: Dict, strategy: str = "auto") -> Dict:

        """

        ??- 



        Args:

            task: 

            strategy: "sft", "dpo", "rpt", "self_gen", "neural_symbolic", "auto"



        Returns:

            

        """

        print(f"\n{'=' * 50}")

        print(f"[SelfEvolutionV2] ?? task={task.get('task')}, strategy={strategy}")

        print(f"{'=' * 50}")



        # 

        if strategy == "auto":

            stage = EvolutionStage.SFT_ITERATION  # 

        else:

            stage_map = {

                "sft": EvolutionStage.SFT_ITERATION,

                "dpo": EvolutionStage.DPO_OPTIMIZATION,

                "rpt": EvolutionStage.RPT_CONTINUAL,

                "self_gen": EvolutionStage.SELF_GENERATED,

                "neural_symbolic": EvolutionStage.NEURAL_SYMBOLIC

            }

            stage = stage_map.get(strategy, EvolutionStage.SFT_ITERATION)



        # ??

        context = TaskContext(task=task, strategy=strategy, stage=stage)



        # 

        brain_results = {}

        for role, brain_fn in self.brain_roles.items():

            result = brain_fn(context)

            brain_results[role] = result

            context.brain_outputs[role] = result



        # 

        execution_result = self._brain_execution(context)

        brain_results[BrainRole.EXECUTION] = execution_result



        # 

        feedback_result = self._brain_feedback(context)

        brain_results[BrainRole.FEEDBACK] = feedback_result



        # 

        record = EvolutionRecord(

            id=generate_id(),

            stage=context.stage,

            model_id=task.get("model_id", "unknown"),

            prompt=task.get("prompt", ""),

            response=str(execution_result),

            preference=0.7,

            reward=1.0 if execution_result.get("success") else 0.0,

            loss=execution_result.get("avg_loss", execution_result.get("final_loss", 1.0)),

            iteration=execution_result.get("iterations", 1),

            improvement=feedback_result.get("improvement_suggested", 0),

            timestamp=time.time()

        )

        self.evolution_history.append(record)



        return {

            "status": "completed",

            "stage": context.stage.value,

            "strategy_used": strategy,

            "execution_result": execution_result,

            "feedback": feedback_result,

            "evolution_count": len(self.evolution_history)

        }



    def multi_brain_collaborate(self, task: Dict) -> Dict:

        """

         - 

        """

        print(f"\n{'=' * 50}")

        print(f"[SelfEvolutionV2] : {task.get('task')}")

        print(f"{'=' * 50}")



        # 

        context = TaskContext(

            task=task,

            strategy="auto",

            stage=EvolutionStage.SFT_ITERATION

        )



        all_outputs = {}

        for role in BrainRole:

            brain_fn = self.brain_roles[role]

            output = brain_fn(context)

            all_outputs[role.value] = output

            context.brain_outputs[role] = output

            time.sleep(0.05)  # 



        return {

            "task": task.get("task"),

            "brain_outputs": all_outputs,

            "final_result": context.brain_outputs.get(BrainRole.FEEDBACK, {}).get("evolution_successful", False),

            "collaboration_complete": True

        }



    def get_evolution_report(self) -> Dict:

        """"""

        total_evolutions = len(self.evolution_history)

        successful = sum(1 for r in self.evolution_history if r.reward > 0)

        avg_improvement = sum(r.improvement for r in self.evolution_history) / total_evolutions if total_evolutions > 0 else 0



        stage_counts = {}

        for r in self.evolution_history:

            stage_counts[r.stage.value] = stage_counts.get(r.stage.value, 0) + 1



        return {

            "total_evolutions": total_evolutions,

            "successful_evolutions": successful,

            "success_rate": successful / total_evolutions if total_evolutions > 0 else 0,

            "avg_improvement": avg_improvement,

            "current_level": self.current_level.value,

            "stage_distribution": stage_counts,

            "optimal_patterns": self.optimal_patterns

        }





# ====================  ====================



if __name__ == "__main__":

    print("=" * 60)

    print(" - ??v2.0 ")

    print("=" * 60)



    db_dir = 'C:/Users/Administrator/.openclaw/workspace/skills/symphony/data'

    os.makedirs(db_dir, exist_ok=True)



    # V2

    evolver = SelfEvolutionV2(db_dir)



    # 1: SFT

    print("\n=== 1: Iterative SFT  ===")

    sft_result = evolver.evolve({

        "task": "",

        "prompt": "??,

        "model_id": "glm-4.7-flash"

    }, strategy="sft")

    print(f"SFT: {sft_result['status']}, Stage: {sft_result['stage']}")



    # 2: DPO

    print("\n=== 2: DPO  ===")

    dpo_result = evolver.evolve({

        "task": "",

        "prompt": "",

        "model_id": "glm-4.7-flash"

    }, strategy="dpo")

    print(f"DPO: {dpo_result['status']}, Stage: {dpo_result['stage']}")



    # 3: RPT??

    print("\n=== 3: RPT ??===")

    rpt_result = evolver.evolve({

        "task": "",

        "prompt": "2025AI??,

        "model_id": "glm-4.7-flash",

        "new_data": [{"text": "2025AI??.."}]

    }, strategy="rpt")

    print(f"RPT: {rpt_result['status']}, Stage: {rpt_result['stage']}")



    # 4: ??(R-Zero)

    print("\n=== 4: R-Zero ??===")

    self_gen_result = evolver.evolve({

        "task": "",

        "prompt": "",

        "model_id": "glm-4.7-flash"

    }, strategy="self_gen")

    print(f"?? {self_gen_result['status']}, Stage: {self_gen_result['stage']}")



    # 5: 

    print("\n=== 5:  ===")

    collaborative_result = evolver.multi_brain_collaborate({

        "task": "",

        "prompt": "",

        "model_id": "glm-4.7-flash"

    })

    print(f": {collaborative_result['collaboration_complete']}")

    print(":")

    for brain, output in collaborative_result['brain_outputs'].items():

        print(f"  {brain}: {output.get('recommended_strategy', output.get('role', 'N/A'))}")



    # 6: Auto

    print("\n=== 6: Auto ===")

    auto_result = evolver.evolve({

        "task": "",

        "prompt": "AI",

        "model_id": "glm-4.7-flash"

    }, strategy="auto")

    print(f"Auto: {auto_result['status']}, Stage: {auto_result['stage']}")



    # 

    print("\n" + "=" * 60)

    print("===  ===")

    print("=" * 60)

    report = evolver.get_evolution_report()

    for key, value in report.items():

        print(f"  {key}: {value}")



    print("\n" + "=" * 60)

    print("[OK] ??v2.0 ")

    print("=" * 60)



