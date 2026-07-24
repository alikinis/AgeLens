"""Validate the governed AgeLens V2 Stage 3 release."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
from typing import Any
import pandas as pd

EXPECTED_BUILD="AgeLens-V2-Stage3-20260724e"

def parse_bool(value: Any)->bool:
    if isinstance(value,bool): return value
    v=str(value).strip().lower()
    if v in {"true","1","yes"}: return True
    if v in {"false","0","no"}: return False
    raise ValueError(f"Invalid boolean: {value!r}")

def close(a,b,tol=1e-10):
    return math.isclose(float(a),float(b),rel_tol=0,abs_tol=tol)

def validate(root: Path)->None:
    t=root/"results/tables/v2"; d=root/"docs/v2"
    required=[
      root/"config/v2_stage3_release.json",
      d/"V2_Stage3_Human_Review.md", d/"V2_Stage3_Release_Report.md",
      t/"13_stage3_transportability_global_tests.csv",
      t/"13_stage3_transportability_level_estimates.csv",
      t/"13_stage3_transportability_diagnostics.csv",
      t/"13_stage3_prediction_direction_metrics.csv",
      t/"13_stage3_point_prediction_reconciliation.csv",
      t/"13_stage3_prediction_bootstrap_summary.csv",
      t/"13_stage3_incremental_utility_decision.csv",
      t/"13_stage3_prediction_model_diagnostics.csv",
      t/"13_stage3_release_checks.csv",
      t/"13_stage3_runtime_versions.csv",
      t/"15_stage3_release_summary.csv",
      root/"results/figures/v2/13_stage3_transportability_forest.png",
      root/"results/figures/v2/13_stage3_incremental_performance.png",
    ]
    missing=[str(x) for x in required if not x.is_file()]
    if missing: raise FileNotFoundError("Missing Stage 3 release artifacts: "+", ".join(missing))
    cfg=json.loads((root/"config/v2_stage3_release.json").read_text(encoding="utf-8"))
    if cfg["status"]!="released_for_v2_development" or cfg["human_review_decision"]!="pass_with_guardrails": raise ValueError("Release decision changed.")
    if cfg["source_script_build"]!=EXPECTED_BUILD or cfg["relationship_to_v1"]["v1_immutable"] is not True: raise ValueError("Build or V1 protection changed.")
    perm=cfg["permissions"]
    if not perm["commit_to_v2_development_authorized"] or not perm["stage4_method_selection_authorized"]: raise ValueError("Required authorization missing.")
    if perm["explainable_model_implementation_authorized"] or perm["merge_to_main_authorized"] or perm["final_manuscript_claims_authorized"]: raise ValueError("A restricted permission was authorized prematurely.")

    gt=pd.read_csv(t/"13_stage3_transportability_global_tests.csv")
    if set(gt.dimension)!={"sex","age_group","race_ethnicity","NHANES_cycle"}: raise ValueError("Dimensions changed.")
    if not gt.converged.map(parse_bool).all() or not gt.finite_coefficients.map(parse_bool).all() or not gt.finite_covariance.map(parse_bool).all(): raise ValueError("Transportability fit failure.")
    if not gt.warning_n.fillna(0).astype(int).eq(0).all(): raise ValueError("Transportability warning recorded.")
    supported=set(gt.loc[gt.supported_at_q_0_10.map(parse_bool),"dimension"])
    if supported!={"race_ethnicity"}: raise ValueError("Supported family changed.")
    race=gt.set_index("dimension").loc["race_ethnicity"]
    if not close(race.p_value_raw,0.000255872749735952,1e-15) or not close(race.q_value_bh,0.00102349099894381,1e-14): raise ValueError("Race interaction result changed.")

    lv=pd.read_csv(t/"13_stage3_transportability_level_estimates.csv")
    if len(lv)!=13 or len(lv[lv.dimension=="race_ethnicity"])!=6: raise ValueError("Level family changed.")
    if lv.loc[lv.dimension=="race_ethnicity","positive_n"].min()<30: raise ValueError("Subgroup support changed.")
    if not lv.loc[lv.dimension=="race_ethnicity","supported_at_q_0_10"].map(parse_bool).all(): raise ValueError("Race reporting role changed.")
    if lv.loc[lv.dimension!="race_ethnicity","supported_at_q_0_10"].map(parse_bool).any(): raise ValueError("Non-race family became supported.")

    td=pd.read_csv(t/"13_stage3_transportability_diagnostics.csv").set_index("dimension")
    if int(td.loc["race_ethnicity","predicted_above_one_n"])!=14 or int(td.predicted_above_one_n.max())>14: raise ValueError("Transport diagnostic changed.")

    dr=pd.read_csv(t/"13_stage3_prediction_direction_metrics.csv")
    if set(dr.direction)!={"train_2015_2016_test_2017_2018","train_2017_2018_test_2015_2016"}: raise ValueError("Directions changed.")
    if not dr.brier_delta_c_minus_b.lt(0).all() or not dr.auc_delta_c_minus_b.gt(0).all(): raise ValueError("Directional improvement changed.")

    pdg=pd.read_csv(t/"13_stage3_prediction_model_diagnostics.csv")
    if not pdg.converged.map(parse_bool).all() or not pdg.finite_coefficients.map(parse_bool).all() or not pdg.warning_n.fillna(0).astype(int).eq(0).all(): raise ValueError("Prediction diagnostics failed.")

    rec=pd.read_csv(t/"13_stage3_point_prediction_reconciliation.csv")
    if not rec["pass"].map(parse_bool).all() or not (rec.absolute_difference<=rec.tolerance).all(): raise ValueError("Point reconciliation failed.")

    bs=pd.read_csv(t/"13_stage3_prediction_bootstrap_summary.csv").set_index("metric")
    if not bs.replicate_n.astype(int).eq(500).all() or not bs.failed_replicate_n.astype(int).eq(0).all(): raise ValueError("Bootstrap replication changed.")
    expected={
      "brier_delta_c_minus_b":(-0.003033916192,-0.0052223759,-0.00084545652),
      "auc_delta_c_minus_b":(0.034051046,0.016474428,0.051627664),
    }
    for m,vals in expected.items():
      row=bs.loc[m]
      for c,v in zip(("estimate","ci_low_95","ci_high_95"),vals):
        if not close(row[c],v,1e-8): raise ValueError(f"{m} {c} changed.")
    ci=bs.loc["calibration_intercept_c"]; cs=bs.loc["calibration_slope_c"]
    if not (float(ci.ci_low_95)<=0<=float(ci.ci_high_95)): raise ValueError("Calibration intercept gate failed.")
    if not (float(cs.ci_low_95)<=1<=float(cs.ci_high_95)): raise ValueError("Calibration slope gate failed.")

    dec=pd.read_csv(t/"13_stage3_incremental_utility_decision.csv")
    if len(dec)!=1 or not parse_bool(dec.iloc[0].positive_incremental_utility_claim): raise ValueError("Incremental utility gate failed.")
    rc=pd.read_csv(t/"13_stage3_release_checks.csv")
    if not rc["pass"].map(parse_bool).all(): raise ValueError("Stage 3 release checks failed.")
    rv=pd.read_csv(t/"13_stage3_runtime_versions.csv").set_index("component")
    if rv.loc["script_build","version"]!=EXPECTED_BUILD: raise ValueError("Runtime build changed.")
    sm=pd.read_csv(t/"15_stage3_release_summary.csv")
    if set(sm.component)!={"transportability_race_ethnicity","prediction_brier_delta_c_minus_b","prediction_auc_delta_c_minus_b","stage4_method_selection","merge_to_main"}: raise ValueError("Release summary changed.")

    combined=(d/"V2_Stage3_Human_Review.md").read_text(encoding="utf-8")+"\n"+(d/"V2_Stage3_Release_Report.md").read_text(encoding="utf-8")
    for phrase in ("pass with guardrails","global linear","external-cohort validation","No explainable model is yet authorized"):
      if phrase.lower() not in combined.lower(): raise ValueError("Release guardrail missing: "+phrase)
    print("STAGE 3 RELEASE VALIDATION PASSED")
    print("Human review decision: pass with guardrails.")
    print("Race/ethnicity global interaction is released with restricted wording.")
    print("Modest incremental cross-cycle prediction utility is released.")
    print("Stage 4 method selection is authorized; model implementation is not.")
    print("Merge to main remains unauthorized.")

def main():
    p=argparse.ArgumentParser(); p.add_argument("--project-root",type=Path,default=Path(".")); p.add_argument("--self-test",action="store_true"); a=p.parse_args()
    if a.self_test:
      assert close(1,1); assert parse_bool("True"); print("SELF-TEST PASSED"); return
    validate(a.project_root.resolve())
if __name__=="__main__": main()
