import re

class KeywordTrigger:
    def __init__(self):
        self.pattern = re.compile(r'(?i)(交响|序境|symphony|\b[沈苏等][\u4e00-\u9fa5]{1,3}\b)', re.UNICODE)

    def trigger_service(self, message):
        if self.pattern.search(message):
            print("服务已触发")
            return True
        return False

class PersonnelResponseModule:
    def __init__(self):
        self.models = {}  # 存储模型映射

    def identify_person(self, message):
        # 识别消息中的姓名，此处简化为直接匹配"沈"或"苏"
        if "沈" in message or "苏" in message:
            return "沈" if "沈" in message else "苏"
        return None

    def dispatch_model(self, person):
        # 调度对应模型
        if person in self.models:
            print(f"已调度{person}模型")
            return self.models[person]
        return None

class ProactiveHelp:
    def __init__(self):
        self.rule_engine = RuleEngine()

    def analyze_intent(self, message):
        # 解析用户意图，此处简化为直接返回用户消息
        return message

    def provide_help(self, message):
        # 提供主动帮助
        intent = self.analyze_intent(message)
        solution = self.rule_engine.match_rule(intent)
        if solution:
            print(f"主动帮助：{solution}")
            return solution
        return None

class RuleEngine:
    def match_rule(self, message):
        # 匹配预设规则库，此处简化为直接返回消息
        return message

class ModelScheduler:
    def schedule_model(self, task_type, models):
        primary_model = models.get(task_type)
        if primary_model and primary_model.is_alive():
            return primary_model
        else:
            backup_model = models.get(f"{task_type}_backup")
            if backup_model and backup_model.is_alive():
                return backup_model
            print(f"无可用模型，任务类型：{task_type}")
            return None

# 示例使用
if __name__ == "__main__":
    keyword_trigger = KeywordTrigger()
    personnel_response = PersonnelResponseModule()
    proactive_help = ProactiveHelp()
    model_scheduler = ModelScheduler()

    # 模拟模型
    class MockModel:
        def __init__(self, name):
            self.name = name
            self.alive = True
        def is_alive(self):
            return self.alive

    models = {
        "文本生成": MockModel("文本生成"),
        "文本生成_backup": MockModel("文本生成_backup"),
    }

    message = "序境系统中沈工部的建议"
    if keyword_trigger.trigger_service(message):
        person = personnel_response.identify_person(message)
        if person:
            model = personnel_response.dispatch_model(person)
            if model:
                task_type = "文本生成"  # 假设任务类型为文本生成
                primary_model = model_scheduler.schedule_model(task_type, models)
                if primary_model:
                    print(f"使用模型：{primary_model.name}")
                else:
                    print("无可用模型")
        solution = proactive_help.provide_help(message)
        if solution:
            print(f"问题解决建议：{solution}")