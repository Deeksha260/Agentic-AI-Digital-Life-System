import time
from plyer import notification
import pygetwindow as gw

# ================= TASK INPUT =================
def get_tasks():
    print("\n Enter your pending tasks (type 'done' to finish):")
    tasks = []

    while True:
        name = input("Task name: ").strip()
        if name.lower() == "done":
            break

        days = int(input("Days left to complete: "))
        tasks.append({"task": name, "days_left": days})

    return tasks 

# ================= BEHAVIOR AGENT =================
class BehaviorAgent:

    def get_active_window(self):
        try:
            window = gw.getActiveWindow()
            if window:
                return window.title
            return ""
        except:
            return ""

    def run(self):
        title = self.get_active_window().lower()

        if not title:
            return "IGNORE"

        if any(x in title for x in [
            "youtube", "instagram", "reel", "netflix",
            "prime video", "hotstar", "game", "pubg",
            "freefire", "valorant"
        ]):
            category = "ENTERTAINMENT"

        elif any(x in title for x in [
            "code", "visual studio", "github", "notepad",
            "pdf","document", "word", "powerpoint",
            "excel", "colab", "jupyter"
        ]):
            category = "PRODUCTIVE"

        elif any(x in title for x in [
            "new tab", "search","browser", "msn",
            "start page", "bing", "about:blank"
        ]):
            return "IGNORE"

        else:
            return "IGNORE"

        print("\nBehavior Agent:")
        print(f"-> Active Window: {title}")
        print(f"-> Category: {category}")

        return category

# ================= TASK AGENT =================
class TaskAgent:
    def run(self, tasks):
        print("\nTask Agent:")

        urgent_tasks = []

        for t in tasks:
            days = t["days_left"]

            if days <= 1:
                score = 5
                priority = "HIGH"
            elif days <= 3:
                score = 3
                priority = "MEDIUM"
            else:
                score = 1
                priority = "LOW"

            t["score"] = score
            t["priority"] = priority

            print(f"-> {t['task']} ({days} days left) | Score: {score} | Priority: {priority}")

            if priority in ["HIGH", "MEDIUM"]:
                urgent_tasks.append(t)

        return urgent_tasks

# ================= DECISION AGENT =================
class DecisionAgent:
    def run(self, category, urgent_tasks):
        print("\nDecision Agent:")

        reasons = []

        if category == "ENTERTAINMENT":
            reasons.append("User is distracted")

        if urgent_tasks:
            reasons.append("Urgent tasks pending")

        if category == "ENTERTAINMENT" and urgent_tasks:
            decision = "HIGH_ALERT"
        elif category == "ENTERTAINMENT":
            decision = "ALERT"
        else:
            decision = "GOOD"

        print(f"-> Reasons: {', '.join(reasons)}")
        print(f"-> Final Decision: {decision}")

        return decision, reasons

# ================= ACTION AGENT =================
class ActionAgent:
    def run(self, decision, tasks, category, reasons):
        print("\nAction Agent:")

        if not tasks:
            print("-> No important tasks")
            return

        # FIX: sort HIGH first
        tasks_sorted = sorted(tasks, key=lambda x: x["score"], reverse=True)
        top_tasks = tasks_sorted[:2]

        task_list = ", ".join([t["task"] for t in top_tasks])

        if decision == "HIGH_ALERT":
            msg = f"STOP NOW\n-> Focus on: {task_list}"
        elif decision == "ALERT":
            msg = f"Work on: {task_list}"
        else:
            msg = f"Continue working\n-> Next: {task_list}"

        print(msg)
        print(f"-> Reason: {', '.join(reasons)}")

        if category == "ENTERTAINMENT":
            notification.notify(
                title="Agentic AI Alert",
                message=msg,
                timeout=5
            )

# ================= TASK FILTER =================
class TaskFilterAgent:
    def run(self, tasks):

        filtered = []

        for t in tasks:
            name = t["task"].lower()

            if any(x in name for x in [
                "game", "play", "youtube", "facebook",
                "watch", "sleep", "movie", "scroll", "instagram"
            ]):
                print(f"Removed non-productive task: {t['task']}")
            else:
                filtered.append(t)

        return filtered

# ================= ORCHESTRATOR =================
class OrchestratorAgent:
    def __init__(self, tasks):
        self.tasks = tasks
        self.behavior = BehaviorAgent()
        self.task_agent = TaskAgent()
        self.decision = DecisionAgent()
        self.action = ActionAgent()
        self.filter_agent = TaskFilterAgent()

    def run(self):
        print("\nORCHESTRATOR: Smart Monitoring Started...")

        print("\nTask Filter Agent:")
        self.filtered_tasks = self.filter_agent.run(self.tasks)
        
        print("\n---- Verbose Mode Enabled----:")
              
        last_window = None
        check_count = 1

        start_time = time.time()
        duration = 180  # 3 minutes

        while time.time() - start_time < duration:
            title = self.behavior.get_active_window().lower()

            if title and title != last_window:
           
               
               category = self.behavior.run()

               if category == "IGNORE":
                  last_window = title
                  continue
              
               print(f"\n========== CHECK {check_count} ==========")

               urgent = self.task_agent.run(self.filtered_tasks)

               decision, reasons = self.decision.run(category, urgent)

               self.action.run(decision, self.filtered_tasks, category, reasons)

               last_window = title
               check_count += 1

            time.sleep(2)

        print("\nMonitoring completed (3 minutes).")
        
# ================= MAIN =================
if __name__ == "__main__":
    print("AGENTIC AI DIGITAL LIFE SYSTEM")

    tasks = get_tasks()

    if not tasks:
        print("No tasks entered. Exiting...")
    else:
        system = OrchestratorAgent(tasks)
        system.run()