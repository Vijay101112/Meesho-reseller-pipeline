"""Run the whole pipeline in order with one command:  python run_pipeline.py"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def step(title, args, cwd=ROOT):
    print(f"\n=== {title} ===")
    subprocess.run([sys.executable, *args], cwd=cwd, check=True)


step("Data: regenerate dataset", ["data/generate_dataset.py"])
step("Part 1: SQL queries -> part1_sql/output/*.csv", ["part1_sql/run_queries.py"])
step("Part 1 -> 2: copy validated feed into Part 2 fixtures", ["-c",
     "import shutil; shutil.copy('part1_sql/output/monthly_category_revenue.csv', "
     "'part2_engine/fixtures/monthly_category_revenue.csv')"])
step("Part 2: engine tests", ["-m", "unittest", "-v"], cwd=os.path.join(ROOT, "part2_engine"))
step("Part 3: masking / template tests", ["-m", "unittest", "-v"], cwd=os.path.join(ROOT, "part3_narrative"))
step("Part 4: agent tests", ["-m", "unittest", "-v"], cwd=os.path.join(ROOT, "part4_agent"))
step("Part 4: run the three scenarios", ["part4_agent/mock_agent_runner.py"])
print("\nPipeline complete (no API keys used).")
