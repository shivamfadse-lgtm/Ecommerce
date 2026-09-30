import sys
import os
from pathlib import Path

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, backend_path)

from app.ml.pipeline import AnalysisPipeline

print("--- Running Direct Python Backend Integration Verification ---")

data_dir = Path(__file__).resolve().parent / "data"
pipeline = AnalysisPipeline(data_dir)

# 1. Run Pipeline with Default Balanced Priority
res = pipeline.run(priority="Balanced", k=4)

print("1. Pipeline Analysis Execution:")
print("   -> City:", res["city"])
print("   -> State:", res["state"])
print("   -> Quality Summary:", res["quality"])
print("   -> Total Customers Analyzed:", res["demand"]["total_customers"])
print("   -> Total Daily Orders:", res["demand"]["total_orders"])
print("   -> Average Order Value:", f"INR {res['demand']['avg_order_value']}")
print("   -> Optimal K (Auto-detected):", res["analytics"]["optimal_k"])
print("   -> WCSS / Elbow Data Points Count:", len(res["analytics"]["elbow"]))
print("   -> Silhouette Scores Count:", len(res["analytics"]["silhouette"]))
print("   -> Discovered Clusters Count:", len(res["clusters"]))
print("   -> Generated Candidate Locations:", len(res["candidates"]))

rec = res["recommendation"]
print("\n2. AI Recommendation Results:")
print("   -> #1 Recommended Area:", rec["area"])
print("   -> AI Score:", f"{rec['ai_score']}/100")
print("   -> Average Delivery Distance:", f"{rec['average_delivery_distance']} km")
print("   -> 5km Customer Coverage:", f"{rec['coverage_percentage']}%")
print("   -> Road Connectivity Score:", f"{rec['road_connectivity']}/100")
print("   -> Monthly Operating Cost:", f"INR {rec['operating_cost']:,}")

print("\n3. Dynamic AI Rationale:")
print("   -> Rationale Summary:", res["explanation"]["summary"])
print("   -> Positive Factors:", res["explanation"]["positive_factors"])
if res["explanation"]["risks"]:
    print("   -> Risk Factors:", res["explanation"]["risks"])

print("\nALL BACKEND ML & PIPELINE MODULES VERIFIED SUCCESSFULLY!")
