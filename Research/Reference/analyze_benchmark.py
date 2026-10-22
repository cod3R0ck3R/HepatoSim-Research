#!/usr/bin/env python3
"""Describe frozen KaSim benchmark results; no fitting or biological validation.

Example: python3 -B Research/Reference/analyze_benchmark.py --results RUN_DIRECTORY
         --previous-results V1_DIRECTORY --output NEW_ANALYSIS_JSON
An omitted --spec uses the run directory's frozen specification.json snapshot.
"""
import argparse
import bisect
import datetime as dt
import hashlib
import json
import math
from pathlib import Path, PurePath
import statistics

import run_benchmark as runner


BASELINE_COLLAGEN = 0.5
GRID_TOLERANCE = 1e-8
HERE = Path(__file__).resolve().parent
TERMINAL_STATUSES = {"completed", "timeout", "runtime_error", "invalid_output", "missing_output"}
LIMITATIONS = [
    "Published 12/14-fold targets are approximate development summaries, not independent measurements; no invented measurement error or sample size.",
    "Stochastic seed spread and Monte Carlo error do not quantify parameter, measurement, or structural uncertainty; quantiles are not confidence intervals.",
    "Incomplete conditions have individual completed-run observations only; ensemble, split-half, and paired summaries are withheld to avoid survivor selection.",
    "Original model-file variants can differ in multiple mechanisms; a condition contrast is not automatically a single-parameter or drug effect.",
    "COL1 tokens and mouse-model time are not human fibrosis, hepatic function, or clinical prognosis. Independent biological validation NOT PERFORMED; clinical validity NOT ASSESSED.",
    "This is a read-only snapshot; not_started records may be running. Later finished jobs require a new analysis output.",
    "Historical path prefixes are retained as recorded provenance, not resolved on the analysis machine. Runtime paths do not attest which executable actually ran.",
]


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def quantile(values, probability):
    """Empirical linear interpolation, h=(n-1)*p (Hyndman-Fan type 7)."""
    if not values or not 0 <= probability <= 1:
        raise ValueError("Quantile requires observations and probability in [0, 1]")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    fraction = position - lower
    return ordered[lower] + fraction * (ordered[min(lower + 1, len(ordered) - 1)] - ordered[lower])


def describe(values):
    if not values or not all(math.isfinite(value) for value in values):
        raise ValueError("Description requires finite observations")
    sd = statistics.stdev(values) if len(values) > 1 else None
    return {"n": len(values), "mean": statistics.mean(values), "sd": sd,
            "min": min(values), "max": max(values),
            "q05": quantile(values, 0.05), "q95": quantile(values, 0.95),
            "mcse_mean": sd / math.sqrt(len(values)) if sd is not None else None}


def day_key(day):
    return f"{day:g}"


def verify_provenance(results, spec):
    """Check original frozen bytes, not the runner's reserialized JSON snapshot."""
    frozen_path = HERE / f"benchmark-v{spec['version']}.json"
    frozen_bytes = frozen_path.read_bytes()
    frozen_hash = sha256_bytes(frozen_bytes)
    if frozen_path.with_suffix(".sha256").read_text().split()[0] != frozen_hash:
        raise ValueError("Original frozen specification digest mismatch")
    if json.loads(frozen_bytes) != spec:
        raise ValueError("Specification differs from the verified original frozen document")
    source_lock_path = HERE / "source-lock.json"
    source_hash = runner.digest(source_lock_path)
    lock = json.loads(source_lock_path.read_text())
    models = {}
    for condition in spec["conditions"]:
        entries = [item for item in lock["artifacts"] if item["repository"].endswith("/HSC_model_Kappa")
                   and item["path"] == condition["file"] and item["commit"] == spec["sources"]["model_commit"]]
        if len(entries) != 1:
            raise ValueError("Model has no unique matching source-lock entry")
        expected = entries[0]["sha256"]
        if runner.digest(HERE / "vendor/HSC_model_Kappa" / condition["file"]) != expected:
            raise ValueError("Original model file differs from source-lock")
        models[condition["file"]] = expected
    provenance = {"frozen_original_specification_sha256": frozen_hash,
                  "frozen_original_specification_verified": True,
                  "source_lock_sha256": source_hash, "verified_model_sha256": models,
                  "environment_verification": {"status": "missing", "reason": "No environment.json; execution-environment provenance is unverified."}}
    environment_path = Path(results) / "environment.json"
    if environment_path.exists():
        environment = json.loads(environment_path.read_text())
        if environment.get("benchmark_sha256") != frozen_hash:
            raise ValueError("Environment benchmark digest differs from original frozen bytes")
        if environment.get("source_lock_sha256") != source_hash:
            raise ValueError("Environment source-lock digest differs from current pinned lock")
        provenance["environment_verification"] = {
            "status": "benchmark_and_source_lock_hashes_verified",
            "recorded_runner_sha256": environment.get("runner_sha256"),
            "runner_matches_current_file": environment.get("runner_sha256") == runner.digest(HERE / "run_benchmark.py"),
            "limitation": "Recorded environment metadata; no independent re-execution or medical validation."}
    return provenance, models


def verify_run_command(record, job, spec):
    """Require the frozen runner's complete argv, including all flags/overrides.

    Historical prefixes are portable: verify model vendor suffix and job folder.
    Original model bytes are checked separately against the source lock.
    Duplicate, missing, extra,
    reordered, or changed tokens fail closed; metadata cannot substitute for argv.
    """
    argv = record.get("argv")
    if not isinstance(argv, list) or len(argv) < 17 or not all(isinstance(value, str) and value for value in argv):
        raise ValueError("Run argv is missing or malformed")
    model_suffix = str(PurePath("vendor", "HSC_model_Kappa", job["file"]))
    expected = [argv[0], model_suffix, "-l", str(spec["sampling"]["duration_limit_days"]),
                "-p", str(job["period"]), "-seed", str(job["seed"]), "-mode", "batch",
                "-d", job["job_id"], "-o", "trace.csv", "-log", "inputs", "--print-efficiency"]
    expected.extend(spec.get("runtime_arguments", []))
    for name, value in sorted(job["overrides"].items()):
        expected.extend(["-var", name, str(value)])
    actual = list(argv)
    actual[1] = str(PurePath(*PurePath(actual[1]).parts[-3:]))
    actual[11] = PurePath(actual[11]).name
    if actual != expected:
        raise ValueError("Run argv differs from frozen job/specification (source, seed, period, duration, flags, output, or overrides)")
    return {"runtime": argv[0], "model": argv[1], "output_directory": argv[11]}


def load_run(results, job, spec, expected_model_hash, allow_partial=False):
    """Return public status, numeric rows, raw metadata; unfinished CSVs stay unread."""
    folder = Path(results) / job["job_id"]
    result = {"job_id": job["job_id"], "seed": job["seed"], "runner_status": "missing",
              "analysis_status": "missing", "samples": {}}
    record = {}
    try:
        raw_record = (folder / "run.json").read_bytes()
        record = json.loads(raw_record)
        result["run_json_sha256"] = sha256_bytes(raw_record)
        result["runner_status"] = record["status"]
        result["analysis_status"] = "not_completed"
        if record["status"] != "completed" and not (allow_partial and record["status"] in TERMINAL_STATUSES):
            return result, None, record
        expected = {"job_id": job["job_id"], "condition": job["id"], "seed": job["seed"],
                    "overrides": job["overrides"], "period_days": job["period"]}
        if any(record.get(key) != value for key, value in expected.items()):
            raise ValueError("Run identity/condition/seed/overrides/period differs from specification")
        if record.get("model_sha256") != expected_model_hash:
            raise ValueError("Run model digest differs from verified original source-lock artifact")
        result["recorded_paths"] = verify_run_command(record, job, spec)
        result["argv_matches_frozen_job"] = True
        if record["status"] == "completed" and record.get("returncode") != 0:
            raise ValueError("Completed run has no successful return code")
        trace = folder / "trace.csv"
        trace_hash = runner.digest(trace)
        if record.get("trace_sha256") != trace_hash:
            raise ValueError("Trace digest differs from finalized run record")
        rows = runner.read_trace(trace)
        if runner.digest(trace) != trace_hash or (folder / "run.json").read_bytes() != raw_record:
            raise ValueError("Run changed while reading; retry after finalization")
        if rows[0]["[T]"] != 0 or rows[0]["COL1 tot"] != BASELINE_COLLAGEN:
            raise ValueError("Expected time-zero collagen baseline 0.5")
        result.update(trace_sha256=trace_hash, model_sha256=record.get("model_sha256"),
                      rows=len(rows), first_day=rows[0]["[T]"], last_day=rows[-1]["[T]"],
                      minimum_observation=min(value for row in rows for key, value in row.items() if key != "[T]"))
        if allow_partial and record["status"] != "completed":
            result["analysis_status"] = "partial_for_technical_comparison_only"
            return result, rows, record
        for day in spec["sampling"]["evaluation_times_days"]:
            selected = runner.at_time(rows, day)
            result["samples"][day_key(day)] = {
                "requested_day": day, "actual_day": selected["[T]"],
                "collagen_model_units": selected["COL1 tot"],
                "collagen_fold": selected["COL1 tot"] / BASELINE_COLLAGEN}
        result["analysis_status"] = "eligible"
        return result, rows, record
    except FileNotFoundError as error:
        result["analysis_status"] = "missing" if not record else "invalid_input"
        result["reason"] = str(error)
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as error:
        result["analysis_status"] = "invalid_input"
        result["reason"] = str(error)
    result["samples"] = {}
    return result, None, record


def error_metrics(predictions, targets):
    errors = {day: predictions[day] - target for day, target in targets.items()}
    return {"errors_prediction_minus_target": errors,
            "mae": statistics.mean(abs(error) for error in errors.values()),
            "rmse": math.sqrt(statistics.mean(error * error for error in errors.values()))}


def summarize_condition(condition, runs, days, targets):
    complete = all(run["analysis_status"] == "eligible" for run in runs)
    summary = {"id": condition["id"], "model_file": condition["file"],
               "declared_overrides": condition["overrides"], "expected_seeds": condition["seeds"],
               "completed_seeds": [run["seed"] for run in runs if run["analysis_status"] == "eligible"],
               "missing_or_unusable_seeds": [run["seed"] for run in runs if run["analysis_status"] != "eligible"],
               "status": "complete" if complete else "incomplete", "runs": runs,
               "ensemble": None, "paired_changes": None, "split_half": None,
               "development_summary_comparison": None, "directional_reproduction": None}
    if not complete:
        summary["withheld_reason"] = "Not all prespecified primary seeds are eligible; no survivor-subset ensemble metrics."
        return summary
    summary["ensemble"] = {day_key(day): describe([run["samples"][day_key(day)]["collagen_fold"] for run in runs]) for day in days}
    mean_predictions = {day: summary["ensemble"][day]["mean"] for day in targets}
    summary["development_summary_comparison"] = {
        "status": "descriptive_only", "targets": targets,
        "ensemble_mean": error_metrics(mean_predictions, targets),
        "constant_fold_1": error_metrics(dict.fromkeys(targets, 1.0), targets),
        "quantitative_pass_fail": "NOT DEFINED; approximate development targets have no calibrated acceptance threshold"}
    changes = {}
    for label, start, end, sign in (("injury_60_minus_0", 0, 60, 1),
                                  ("withdrawal_90_minus_60", 60, 90, -1),
                                  ("withdrawal_240_minus_60", 60, 240, -1)):
        values = [{"seed": run["seed"],
                   "start_actual_day": run["samples"][str(start)]["actual_day"],
                   "end_actual_day": run["samples"][str(end)]["actual_day"],
                   "delta_collagen_model_units": run["samples"][str(end)]["collagen_model_units"] - run["samples"][str(start)]["collagen_model_units"],
                   "delta_collagen_fold": run["samples"][str(end)]["collagen_fold"] - run["samples"][str(start)]["collagen_fold"]}
                  for run in runs]
        fold_stats = describe([value["delta_collagen_fold"] for value in values])
        changes[label] = {"per_seed": values, "collagen_fold": fold_stats,
                          "collagen_model_units": describe([value["delta_collagen_model_units"] for value in values]),
                          "expected_ensemble_mean_sign": "positive" if sign == 1 else "negative",
                          "expected_mean_sign_observed": sign * fold_stats["mean"] > 0}
    summary["paired_changes"] = changes
    summary["directional_reproduction"] = {
        "status": "observed_mean_directions" if all(value["expected_mean_sign_observed"] for value in changes.values()) else "failed_mean_direction",
        "interpretation": "Signs of full-ensemble paired means only; no biological validation or measurement uncertainty test."}
    by_seed = {run["seed"]: run for run in runs}
    batches = [list(range(101, 106)), list(range(106, 111))]
    if set(by_seed) == set(batches[0] + batches[1]):
        split = {}
        for day in days:
            key = day_key(day)
            first, second = [describe([by_seed[seed]["samples"][key]["collagen_fold"] for seed in seeds]) for seeds in batches]
            split[key] = {"seeds_101_to_105": first, "seeds_106_to_110": second,
                          "mean_second_minus_first": second["mean"] - first["mean"],
                          "mcse_difference": math.hypot(first["mcse_mean"], second["mcse_mean"])}
        summary["split_half"] = {"status": "computed", "by_day": split,
                                 "limitation": "Two fixed batches do not establish convergence of distribution tails."}
    else:
        summary["split_half"] = {"status": "not_applicable", "reason": "Prespecified batches require all seeds 101 through 110."}
    return summary


def normalized_command(argv, ignore_period=False, ignore_gc=False):
    result = []
    index = 0
    while index < len(argv):
        value = argv[index]
        if value == "-d" or (ignore_period and value == "-p"):
            index += 2
            continue
        if not (ignore_gc and value == "--gluttony"):
            if index == 0:
                value = PurePath(value).name
            elif index == 1:
                value = str(PurePath(*PurePath(value).parts[-3:]))
            result.append(value)
        index += 1
    return result


def comparable_metadata(left, right, grid=False, gc=False):
    keys = ["condition", "seed", "overrides", "model_sha256"]
    if not grid:
        keys.append("period_days")
    return (all(key in left and left[key] == right.get(key) for key in keys)
            and bool(left.get("argv")) and bool(right.get("argv"))
            and normalized_command(left["argv"], grid, gc) == normalized_command(right["argv"], grid, gc))


def compare_numeric_rows(left, right, prefix=False):
    if prefix and len(left) > len(right):
        return {"status": "not_comparable", "reason": "New trace is shorter than prior prefix", "left_rows": len(left), "right_rows": len(right)}
    mismatch = next((index for index, (a, b) in enumerate(zip(left, right)) if a != b), None)
    equal_length = len(left) == len(right)
    return {"status": "match" if mismatch is None and (prefix or equal_length) else "mismatch",
            "left_rows": len(left), "right_rows": len(right), "compared_rows": min(len(left), len(right)),
            "first_mismatching_row": mismatch, "row_count_equal": equal_length,
            "comparison": "exact numeric rows; comments/UUID/path text excluded", "prefix_only": prefix}


def grid_coverage(by_time, period, end):
    """Check every scheduled time, using only the prespecified 1e-8 tolerance."""
    times = sorted(by_time)
    expected = [index * period for index in range(math.floor(end / period) + 1)]
    matches, missing, offsets = {}, [], []
    for requested in expected:
        insertion = bisect.bisect_left(times, requested)
        candidates = times[max(0, insertion - 1):insertion + 1]
        actual = min(candidates, key=lambda value: abs(value - requested))
        if abs(actual - requested) <= GRID_TOLERANCE:
            matches[requested] = actual
            if actual != requested:
                offsets.append({"scheduled_day": requested, "actual_day": actual, "offset_days": actual - requested})
        else:
            missing.append(requested)
    return {"period_days": period, "checked_until_day": end,
            "expected_count": len(expected), "matched_count": len(matches),
            "coverage_fraction": len(matches) / len(expected),
            "missing_expected_times": missing, "nonzero_timestamp_offsets": offsets}, matches


def compare_grid(left, right, reference_period, candidate_period=0.25):
    """Verify both full grids, then compare shared rows and matched grid states."""
    left_by_time = {row["[T]"]: row for row in left}
    right_by_time = {row["[T]"]: row for row in right}
    common = sorted(left_by_time.keys() & right_by_time.keys())
    end = min(max(left_by_time), max(right_by_time))
    reference_coverage, reference_matches = grid_coverage(left_by_time, reference_period, end)
    candidate_coverage, candidate_matches = grid_coverage(right_by_time, candidate_period, end)
    common_scheduled = sorted(reference_matches.keys() & candidate_matches.keys())
    pairs = [(time, time, time) for time in common]
    pairs.extend((scheduled, reference_matches[scheduled], candidate_matches[scheduled])
                 for scheduled in common_scheduled if reference_matches[scheduled] != candidate_matches[scheduled])
    mismatches = []
    maximum_error = 0.0
    for scheduled, left_time, right_time in pairs:
        a, b = left_by_time[left_time], right_by_time[right_time]
        location = {"comparison_day": scheduled, "reference_actual_day": left_time, "candidate_actual_day": right_time}
        if a.keys() != b.keys():
            mismatches.append({**location, "reason": "Column sets differ"})
            continue
        error = max(abs(a[key] - b[key]) for key in a)
        maximum_error = max(maximum_error, error)
        if error > GRID_TOLERANCE:
            mismatches.append({**location, "maximum_absolute_error": error})
    incomplete = reference_coverage["missing_expected_times"] or candidate_coverage["missing_expected_times"]
    status = "incomplete_comparison" if incomplete or not pairs else ("mismatch" if mismatches else "match")
    return {"status": status, "absolute_tolerance": GRID_TOLERANCE,
            "value_comparison_status": "mismatch" if mismatches else ("match" if pairs else "not_performed"),
            "timestamp_absolute_tolerance_days": GRID_TOLERANCE,
            "sampling_grid_coverage": {"reference": reference_coverage, "candidate": candidate_coverage},
            "common_scheduled_grid_count": len(common_scheduled), "compared_pair_count": len(pairs),
            "common_timestamp_count": len(common), "common_first_day": common[0] if common else None,
            "common_last_day": common[-1] if common else None,
            "left_unique_times": len(left_by_time), "right_unique_times": len(right_by_time),
            "missing_reference_grid_times": reference_coverage["missing_expected_times"],
            "missing_candidate_grid_times": candidate_coverage["missing_expected_times"],
            "mismatching_timestamp_count": len(mismatches),
            "first_mismatches": mismatches[:10], "maximum_absolute_error": maximum_error,
            "duplicate_time_policy": "Last numeric row at timestamp; compare all columns at exact shared timestamps and scheduled times matched within 1e-8. Biological endpoint selection remains strict without tolerance."}


def condition_contrasts(conditions, days, seeds=tuple(range(101, 106))):
    reference = conditions[0]
    contrasts = []
    for alternative in conditions[1:]:
        contrast = {"reference": reference["id"], "alternative": alternative["id"],
                    "status": "withheld", "seeds": list(seeds),
                    "interpretation": "Whole-condition sensitivity contrast; not necessarily a single-parameter change, no drug-effect claim.",
                    "reference_model_file": reference["model_file"], "alternative_model_file": alternative["model_file"]}
        if reference["status"] != "complete" or alternative["status"] != "complete":
            contrast["reason"] = "Both prespecified primary conditions must be complete."
        else:
            first = {run["seed"]: run for run in reference["runs"]}
            second = {run["seed"]: run for run in alternative["runs"]}
            if not set(contrast["seeds"]).issubset(first.keys() & second.keys()):
                contrast["reason"] = "Prespecified paired seeds absent."
            else:
                contrast["status"] = "descriptive_only"
                contrast["by_day"] = {}
                for day in days:
                    key = day_key(day)
                    differences = [{"seed": seed,
                                    "alternative_minus_reference_fold": second[seed]["samples"][key]["collagen_fold"] - first[seed]["samples"][key]["collagen_fold"]}
                                   for seed in contrast["seeds"]]
                    contrast["by_day"][key] = {"per_seed": differences, "paired_difference": describe([value["alternative_minus_reference_fold"] for value in differences])}
        contrasts.append(contrast)
    return contrasts


def analyze(results, spec, previous_results=None):
    results = Path(results)
    if not results.is_dir():
        raise ValueError("Results directory does not exist")
    days = spec["sampling"]["evaluation_times_days"]
    if set(days) != {0, 32, 60, 90, 240}:
        raise ValueError("This analysis implements only the prespecified days 0/32/60/90/240")
    targets = spec["comparators"]["published_development_fold_targets"]
    if targets != {"32": 12, "60": 14}:
        raise ValueError("Development targets differ from supported frozen benchmark")
    snapshot = results / "specification.json"
    if snapshot.exists() and json.loads(snapshot.read_text()) != spec:
        raise ValueError("Requested specification differs from run snapshot")
    jobs = runner.make_jobs(spec)
    provenance, model_hashes = verify_provenance(results, spec)
    loaded = {job["job_id"]: load_run(results, job, spec, model_hashes[job["file"]]) for job in jobs}
    conditions = []
    for condition in spec["conditions"]:
        primary = [loaded[f"{condition['id']}-{seed}"][0] for seed in condition["seeds"]]
        conditions.append(summarize_condition(condition, primary, days, targets))
    original_job = jobs[0]
    original, original_rows, original_record = loaded[original_job["job_id"]]
    checks = {}
    for label, job_id, grid in (("seed_replay", "seed-replay-101", False),
                                ("observation_grid", "grid-quarter-day-101", True)):
        check, rows, record = loaded[job_id]
        detail = {"reference_job": original_job["job_id"], "check_job": check}
        if original_rows is None or rows is None:
            detail.update(status="not_performed", reason="Both complete, eligible traces are required.")
        elif not comparable_metadata(original_record, record, grid=grid):
            detail.update(status="not_comparable", reason="Metadata or commands differ beyond the declared output-directory/grid changes.")
        else:
            detail.update(compare_grid(original_rows, rows, original_job["period"], record["period_days"]) if grid else compare_numeric_rows(original_rows, rows))
        checks[label] = detail
    gc_check = {"status": "not_requested", "interpretation": "GC/runtime amendment prefix check only; not full-run or biological equivalence."}
    if previous_results is not None:
        previous_snapshot = Path(previous_results) / "specification.json"
        if previous_snapshot.exists():
            previous_spec = json.loads(previous_snapshot.read_text())
            prior_provenance, prior_hashes = verify_provenance(previous_results, previous_spec)
            gc_check["previous_provenance"] = prior_provenance
            prior_job = next(job for job in runner.make_jobs(previous_spec) if job["job_id"] == original_job["job_id"])
            prior, prior_rows, prior_record = load_run(Path(previous_results), prior_job, previous_spec,
                                                      prior_hashes[prior_job["file"]], allow_partial=True)
            gc_check["previous_run"] = prior
            gc_check["current_run"] = original
            if prior_rows is None or original_rows is None:
                gc_check.update(status="not_performed", reason="Finalized prior trace and complete current trace with verified commands required.")
            elif (spec.get("amendment", {}).get("previous_spec_sha256") != prior_provenance["frozen_original_specification_sha256"]
                  or previous_spec.get("runtime_arguments", []) != [] or spec.get("runtime_arguments", []) != ["--gluttony"]):
                gc_check.update(status="not_comparable", reason="Specifications do not declare the expected no-GC-flag to --gluttony amendment.")
            elif not comparable_metadata(prior_record, original_record, gc=True):
                gc_check.update(status="not_comparable", reason="Metadata/commands differ beyond output directory and declared --gluttony amendment.")
            else:
                gc_check.update(compare_numeric_rows(prior_rows, original_rows, prefix=True))
                gc_check["prefix_last_day"] = prior_rows[-1]["[T]"]
        else:
            gc_check["previous_provenance"] = {"status": "missing", "reason": "Previous specification missing; version identity is unverified."}
            gc_check.update(status="not_performed", reason="Previous frozen specification is required to verify its command.")
    checks["gc_amendment_prefix"] = gc_check
    known_ids = set(loaded)
    unexpected = sorted(path.parent.name for path in results.glob("*/run.json") if path.parent.name not in known_ids)
    provenance.update(results_directory=str(results.resolve()), analysis_source_sha256=runner.digest(__file__))
    for filename in ("specification.json", "environment.json"):
        path = results / filename
        if path.exists():
            provenance[filename + "_sha256"] = runner.digest(path)
    return {"analysis_schema_version": "1.0.0", "benchmark_id": spec["benchmark_id"],
            "benchmark_version": spec["version"], "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "status": "all_primary_conditions_complete" if all(condition["status"] == "complete" for condition in conditions) else "incomplete",
            "normalization": {"divisor": BASELINE_COLLAGEN, "unit": "fold of model baseline collagen"},
            "methods": {"sd": "Sample SD, denominator n-1; undefined for n<2", "quantiles": "Empirical linear interpolation, h=(n-1)p, type 7",
                        "mcse_mean": "Sample SD / sqrt(n), stochastic replicates only", "sampling": "Last row at or before requested day; actual timestamp retained; no extrapolation",
                        "ensemble_membership": "Prespecified primary jobs only; seed replay and quarter-day grid runs excluded"},
            "provenance": provenance, "conditions": conditions,
            "condition_contrasts": condition_contrasts(conditions, days,
                spec["conditions"][0]["seeds"] if "mechanism_design" in spec else tuple(range(101, 106))),
            "technical_checks": checks,
            "unexpected_job_directories_ignored": unexpected, "limitations": LIMITATIONS,
            "independent_biological_validation": "NOT PERFORMED", "clinical_validity": "NOT ASSESSED"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--spec", type=Path)
    parser.add_argument("--previous-results", type=Path)
    parser.add_argument("--output", type=Path, help="New JSON file; existing output is never overwritten. Omit for stdout.")
    args = parser.parse_args(argv)
    try:
        spec_path = args.spec or args.results / "specification.json"
        report = analyze(args.results, json.loads(spec_path.read_text()), args.previous_results)
        encoded = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        if args.output:
            with args.output.open("x") as stream:
                stream.write(encoded)
        else:
            print(encoded, end="")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(2, f"Analysis failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
