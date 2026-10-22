#!/usr/bin/env python3
"""Synthetic, stdlib-only analysis tests; no KaSim runs or real-result writes."""
import copy
import csv
import json
import math
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile
import unittest

import analyze_benchmark as analysis


HERE = Path(__file__).resolve().parent


class StatisticsTests(unittest.TestCase):
    def test_sample_sd_mcse_and_empirical_quantiles(self):
        result = analysis.describe([1, 2, 3, 4, 5])
        self.assertEqual(result["n"], 5)
        self.assertEqual(result["mean"], 3)
        self.assertAlmostEqual(result["sd"], math.sqrt(2.5))
        self.assertAlmostEqual(result["mcse_mean"], math.sqrt(0.5))
        self.assertAlmostEqual(result["q05"], 1.2)
        self.assertAlmostEqual(result["q95"], 4.8)

    def test_singleton_has_no_estimated_sd_or_mcse(self):
        result = analysis.describe([3])
        self.assertIsNone(result["sd"])
        self.assertIsNone(result["mcse_mean"])
        self.assertEqual(result["q05"], 3)

    def test_empty_or_nonfinite_descriptions_rejected(self):
        for values in ([], [1, math.nan], [math.inf]):
            with self.subTest(values=values), self.assertRaises(ValueError):
                analysis.describe(values)

    def test_two_point_development_comparison_is_descriptive(self):
        metrics = analysis.error_metrics({"32": 10, "60": 17}, {"32": 12, "60": 14})
        self.assertEqual(metrics["errors_prediction_minus_target"], {"32": -2, "60": 3})
        self.assertEqual(metrics["mae"], 2.5)
        self.assertAlmostEqual(metrics["rmse"], math.sqrt(6.5))


class NumericComparisonTests(unittest.TestCase):
    def test_exact_replay_compares_all_columns_and_row_count(self):
        rows = [{"[T]": 0, "COL1 tot": 0.5, "qHSC": 100},
                {"[T]": 1, "COL1 tot": 0.6, "qHSC": 99}]
        self.assertEqual(analysis.compare_numeric_rows(rows, copy.deepcopy(rows))["status"], "match")
        changed = copy.deepcopy(rows)
        changed[1]["qHSC"] = 98
        self.assertEqual(analysis.compare_numeric_rows(rows, changed)["first_mismatching_row"], 1)
        self.assertEqual(analysis.compare_numeric_rows(rows, rows[:1])["status"], "mismatch")

    def test_prefix_equality_does_not_claim_full_trace_equality(self):
        old = [{"[T]": 0, "COL1 tot": 0.5}]
        new = old + [{"[T]": 1, "COL1 tot": 0.6}]
        result = analysis.compare_numeric_rows(old, new, prefix=True)
        self.assertEqual(result["status"], "match")
        self.assertTrue(result["prefix_only"])
        self.assertFalse(result["row_count_equal"])
        self.assertEqual(analysis.compare_numeric_rows(new, old, prefix=True)["status"], "not_comparable")

    def test_grid_tolerance_and_last_duplicate_state(self):
        left = [{"[T]": 0, "COL1 tot": 0.5}, {"[T]": 0.5, "COL1 tot": 1.0},
                {"[T]": 0.5, "COL1 tot": 2.0}, {"[T]": 1, "COL1 tot": 3.0}]
        right = [{"[T]": 0, "COL1 tot": 0.5}, {"[T]": 0.25, "COL1 tot": 0.8},
                 {"[T]": 0.5, "COL1 tot": 2.0 + 0.5e-8}, {"[T]": 0.75, "COL1 tot": 2.5},
                 {"[T]": 1, "COL1 tot": 3.0}]
        result = analysis.compare_grid(left, right, 0.5)
        self.assertEqual(result["status"], "match")
        self.assertEqual(result["common_timestamp_count"], 3)
        right[-1]["COL1 tot"] += 2e-8
        self.assertEqual(analysis.compare_grid(left, right, 0.5)["status"], "mismatch")

    def test_missing_common_grid_time_prevents_full_check_pass(self):
        left = [{"[T]": time, "COL1 tot": 0.5} for time in (0, 0.5, 1)]
        result = analysis.compare_grid(left, [left[0], left[-1]], 0.5)
        self.assertEqual(result["status"], "incomplete_comparison")
        self.assertEqual(result["missing_reference_grid_times"], [])
        self.assertEqual(result["missing_candidate_grid_times"], [0.25, 0.5, 0.75])
        self.assertEqual(result["sampling_grid_coverage"]["candidate"]["coverage_fraction"], 0.4)

    def test_five_matching_endpoints_are_not_a_complete_grid(self):
        endpoints = [{"[T]": day, "COL1 tot": 0.5} for day in (0, 32, 60, 90, 240)]
        result = analysis.compare_grid(endpoints, endpoints, 0.5, 0.25)
        self.assertEqual(result["status"], "incomplete_comparison")
        self.assertEqual(result["value_comparison_status"], "match")
        self.assertEqual(result["sampling_grid_coverage"]["reference"]["expected_count"], 481)
        self.assertEqual(result["sampling_grid_coverage"]["candidate"]["expected_count"], 961)
        self.assertEqual(len(result["missing_reference_grid_times"]), 476)
        self.assertEqual(len(result["missing_candidate_grid_times"]), 956)

    def test_grid_timestamp_offsets_use_fixed_tolerance_and_compare_shifted_values(self):
        left = [{"[T]": day, "COL1 tot": 0.5} for day in (0, 0.5, 1)]
        right = [{"[T]": day, "COL1 tot": 0.5} for day in (0, 0.25, 0.5 + 0.5e-8, 0.75, 1)]
        result = analysis.compare_grid(left, right, 0.5)
        self.assertEqual(result["status"], "match")
        self.assertEqual(result["common_scheduled_grid_count"], 3)
        offsets = result["sampling_grid_coverage"]["candidate"]["nonzero_timestamp_offsets"]
        self.assertEqual(len(offsets), 1)
        self.assertEqual(offsets[0]["scheduled_day"], 0.5)
        right[2]["COL1 tot"] = 1
        self.assertEqual(analysis.compare_grid(left, right, 0.5)["status"], "mismatch")
        right[2]["[T]"] = 0.5 + 2e-8
        result = analysis.compare_grid(left, right, 0.5)
        self.assertEqual(result["status"], "incomplete_comparison")
        self.assertIn(0.5, result["missing_candidate_grid_times"])


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.results = self.root / "current"
        self.results.mkdir()
        self.spec = json.loads((HERE / "benchmark-v1.1.0.json").read_text())
        (self.results / "specification.json").write_text(json.dumps(self.spec))
        self.jobs = {job["job_id"]: job for job in analysis.runner.make_jobs(self.spec)}

    def write_run(self, job_id, folds=(1, 12, 14, 8, 2), times=(0, 32, 60, 90, 240),
                  status="completed", results=None, gc=True, overrides=None):
        results = results or self.results
        if results != self.results and not (results / "specification.json").exists():
            results.mkdir(parents=True, exist_ok=True)
            (results / "specification.json").write_bytes((HERE / "benchmark-v1.0.0.json").read_bytes())
        folder = results / job_id
        folder.mkdir(parents=True, exist_ok=True)
        job = self.jobs[job_id]
        trace = folder / "trace.csv"
        with trace.open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["[T]", "COL1 tot", "qHSC", "iHSC", "aSMA-cells"])
            for day, fold in zip(times, folds):
                writer.writerow([day, fold * 0.5, 100, 0, 0])
        argv = ["/fixture/KaSim", str(HERE / "vendor/HSC_model_Kappa" / job["file"]), "-l", "243", "-p", str(job["period"]),
                "-seed", str(job["seed"]), "-mode", "batch", "-d", str(folder), "-o", "trace.csv",
                "-log", "inputs", "--print-efficiency"]
        if gc:
            argv.append("--gluttony")
        for name, value in sorted(job["overrides"].items()):
            argv.extend(["-var", name, str(value)])
        record = {"job_id": job_id, "condition": job["id"], "seed": job["seed"],
                  "status": status, "returncode": 0 if status == "completed" else -15,
                  "overrides": job["overrides"], "period_days": job["period"],
                  "model_sha256": analysis.runner.digest(HERE / "vendor/HSC_model_Kappa" / job["file"]),
                  "trace_sha256": analysis.runner.digest(trace), "argv": argv}
        record.update(overrides or {})
        (folder / "run.json").write_text(json.dumps(record))
        return record

    def fill_condition(self, condition_id="repository_default", varying=False, delta=0):
        condition = next(item for item in self.spec["conditions"] if item["id"] == condition_id)
        for index, seed in enumerate(condition["seeds"]):
            offset = index if varying else 0
            self.write_run(f"{condition_id}-{seed}", (1, 12 + offset + delta, 14 + offset + delta,
                                                     8 + offset + delta, 2 + offset + delta))

    def report(self, previous_results=None):
        return analysis.analyze(self.results, self.spec, previous_results)

    def test_missing_jobs_have_explicit_status_and_no_ensemble(self):
        report = self.report()
        self.assertEqual(report["status"], "incomplete")
        condition = report["conditions"][0]
        self.assertEqual(condition["missing_or_unusable_seeds"], list(range(101, 111)))
        self.assertEqual(condition["runs"][0]["analysis_status"], "missing")
        self.assertIsNone(condition["ensemble"])
        self.assertEqual(report["independent_biological_validation"], "NOT PERFORMED")

    def test_partial_condition_retains_completed_individual_but_withholds_statistics(self):
        self.write_run("repository_default-101")
        self.write_run("repository_default-102", status="timeout")
        condition = self.report()["conditions"][0]
        self.assertEqual(condition["completed_seeds"], [101])
        self.assertEqual(condition["runs"][0]["samples"]["32"]["collagen_fold"], 12)
        self.assertEqual(condition["runs"][1]["runner_status"], "timeout")
        self.assertEqual(condition["runs"][1]["samples"], {})
        for name in ("ensemble", "split_half", "paired_changes", "development_summary_comparison", "directional_reproduction"):
            self.assertIsNone(condition[name])

    def test_unfinished_trace_is_not_parsed_or_used(self):
        self.write_run("repository_default-101", status="not_started")
        (self.results / "repository_default-101" / "trace.csv").write_text("in-progress incomplete CSV")
        run = self.report()["conditions"][0]["runs"][0]
        self.assertEqual(run["analysis_status"], "not_completed")
        self.assertEqual(run["samples"], {})

    def test_at_time_has_no_hidden_tolerance_and_exposes_actual_day(self):
        self.write_run("repository_default-101", folds=(1, 11, 12, 14, 8, 2),
                       times=(0, 31.5, 32.00000001, 60, 90, 240))
        sample = self.report()["conditions"][0]["runs"][0]["samples"]["32"]
        self.assertEqual(sample["requested_day"], 32)
        self.assertEqual(sample["actual_day"], 31.5)
        self.assertEqual(sample["collagen_fold"], 11)

    def test_last_duplicate_time_selected(self):
        self.write_run("repository_default-101", folds=(1, 11, 12, 14, 8, 2), times=(0, 32, 32, 60, 90, 240))
        sample = self.report()["conditions"][0]["runs"][0]["samples"]["32"]
        self.assertEqual(sample["collagen_fold"], 12)

    def test_incomplete_time_coverage_cannot_extrapolate(self):
        self.write_run("repository_default-101", times=(0, 32, 60, 90, 239.5))
        run = self.report()["conditions"][0]["runs"][0]
        self.assertEqual(run["analysis_status"], "invalid_input")
        self.assertEqual(run["samples"], {})

    def test_modified_trace_hash_rejected(self):
        self.write_run("repository_default-101")
        trace = self.results / "repository_default-101" / "trace.csv"
        trace.write_text(trace.read_text() + "241,1,100,0,0\n")
        run = self.report()["conditions"][0]["runs"][0]
        self.assertEqual(run["analysis_status"], "invalid_input")
        self.assertIn("digest", run["reason"])

    def test_mismatched_seed_and_unsuccessful_returncode_rejected(self):
        for metadata in ({"seed": 102}, {"returncode": 7}):
            with self.subTest(metadata=metadata):
                self.write_run("repository_default-101", overrides=metadata)
                self.assertEqual(self.report()["conditions"][0]["runs"][0]["analysis_status"], "invalid_input")

    def test_duplicate_actual_seeds_and_hidden_override_cannot_form_ensemble(self):
        self.fill_condition()
        for seed in range(101, 111):
            path = self.results / f"repository_default-{seed}" / "run.json"
            record = json.loads(path.read_text())
            record["argv"][record["argv"].index("-seed") + 1] = "101"
            record["argv"].extend(["-var", "TGFB1_pool_by_cell", "1"])
            path.write_text(json.dumps(record))
        condition = self.report()["conditions"][0]
        self.assertEqual(condition["status"], "incomplete")
        self.assertEqual(condition["completed_seeds"], [])
        self.assertIsNone(condition["ensemble"])

    def test_argv_mismatches_rejected_despite_matching_metadata(self):
        changes = [("-seed", "102"), ("-p", "0.25"), ("-l", "23"), ("-mode", "interactive"),
                   ("-d", "/different/results"), ("-o", "different.csv"), ("-log", "different")]
        for option, value in changes:
            with self.subTest(option=option):
                record = self.write_run("repository_default-101")
                record["argv"][record["argv"].index(option) + 1] = value
                path = self.results / "repository_default-101" / "run.json"
                path.write_text(json.dumps(record))
                self.assertEqual(self.report()["conditions"][0]["runs"][0]["analysis_status"], "invalid_input")

    def test_argv_source_runtime_flags_and_extra_tokens_rejected(self):
        for mutation in ("source", "missing_gc", "duplicate_gc", "duplicate_seed", "hidden_var", "unknown_flag"):
            with self.subTest(mutation=mutation):
                record = self.write_run("repository_default-101")
                if mutation == "source":
                    record["argv"][1] = str(HERE / "vendor/HSC_model_Kappa/reactMFB-wo-inactivation.ka")
                elif mutation == "missing_gc":
                    record["argv"].remove("--gluttony")
                else:
                    record["argv"].extend({"duplicate_gc": ["--gluttony"], "duplicate_seed": ["-seed", "101"],
                                           "hidden_var": ["-var", "TGFB1_pool_by_cell", "1"],
                                           "unknown_flag": ["--unknown"]}[mutation])
                (self.results / "repository_default-101" / "run.json").write_text(json.dumps(record))
                self.assertEqual(self.report()["conditions"][0]["runs"][0]["analysis_status"], "invalid_input")

    def test_declared_override_value_required_in_argv(self):
        for mutation in ("missing", "wrong_value", "extra_override"):
            with self.subTest(mutation=mutation):
                record = self.write_run("caption_literal-101")
                if mutation == "missing":
                    record["argv"] = record["argv"][:-3]
                elif mutation == "wrong_value":
                    record["argv"][-1] = "6"
                else:
                    record["argv"].extend(["-var", "unlisted_parameter", "4"])
                (self.results / "caption_literal-101" / "run.json").write_text(json.dumps(record))
                self.assertEqual(self.report()["conditions"][1]["runs"][0]["analysis_status"], "invalid_input")

    def test_historical_source_path_prefix_is_portable(self):
        record = self.write_run("repository_default-101")
        record["argv"][1] = "/historical/computer/project/vendor/HSC_model_Kappa/reactMFB-with-inactivation.ka"
        (self.results / "repository_default-101" / "run.json").write_text(json.dumps(record))
        run = self.report()["conditions"][0]["runs"][0]
        self.assertEqual(run["analysis_status"], "eligible")
        self.assertEqual(run["recorded_paths"]["model"], record["argv"][1])

    def test_unchanged_archived_results_remain_analyzable_after_relocation(self):
        self.fill_condition()
        self.write_run("seed-replay-101")
        before = self.report()
        archived = self.root / "different-computer" / "unpacked-results"
        shutil.copytree(self.results, archived)
        shutil.rmtree(self.results)
        after = analysis.analyze(archived, self.spec)
        self.assertEqual(after["conditions"][0], before["conditions"][0])
        self.assertEqual([condition["status"] for condition in after["conditions"]],
                         [condition["status"] for condition in before["conditions"]])
        self.assertEqual(after["conditions"][0]["status"], "complete")
        self.assertEqual(after["technical_checks"]["seed_replay"]["status"], "match")

    def test_wrong_recorded_model_suffix_or_job_folder_is_rejected(self):
        changes = [(1, "/historical/vendor/other_repository/reactMFB-with-inactivation.ka"),
                   (1, "/historical/vendor/HSC_model_Kappa/reactMFB-wo-inactivation.ka"),
                   (11, "/historical/results/repository_default-102")]
        for index, value in changes:
            with self.subTest(path=value):
                record = self.write_run("repository_default-101")
                record["argv"][index] = value
                (self.results / "repository_default-101" / "run.json").write_text(json.dumps(record))
                self.assertEqual(self.report()["conditions"][0]["runs"][0]["analysis_status"], "invalid_input")

    def test_technical_comparison_ignores_only_historical_path_prefixes(self):
        self.write_run("repository_default-101")
        record = self.write_run("seed-replay-101")
        record["argv"][0] = "/historical/computer/bin/KaSim"
        record["argv"][1] = "/historical/project/vendor/HSC_model_Kappa/reactMFB-with-inactivation.ka"
        record["argv"][11] = "/historical/results/seed-replay-101"
        (self.results / "seed-replay-101" / "run.json").write_text(json.dumps(record))
        check = self.report()["technical_checks"]["seed_replay"]
        self.assertEqual(check["status"], "match")
        self.assertEqual(check["check_job"]["recorded_paths"]["runtime"], record["argv"][0])

    def test_replay_and_grid_commands_checked_against_their_own_jobs(self):
        self.write_run("repository_default-101")
        for job_id, option, wrong_value, label in (("seed-replay-101", "-seed", "102", "seed_replay"),
                                                   ("grid-quarter-day-101", "-p", "0.5", "observation_grid")):
            with self.subTest(job=job_id):
                record = self.write_run(job_id)
                record["argv"][record["argv"].index(option) + 1] = wrong_value
                (self.results / job_id / "run.json").write_text(json.dumps(record))
                check = self.report()["technical_checks"][label]
                self.assertEqual(check["status"], "not_performed")
                self.assertEqual(check["check_job"]["analysis_status"], "invalid_input")

    def test_complete_condition_has_expected_statistics_pairing_and_split(self):
        self.fill_condition(varying=True)
        condition = self.report()["conditions"][0]
        self.assertEqual(condition["status"], "complete")
        self.assertEqual(condition["ensemble"]["32"]["n"], 10)
        self.assertEqual(condition["ensemble"]["32"]["mean"], 16.5)
        self.assertAlmostEqual(condition["ensemble"]["32"]["sd"], statistics.stdev(range(10)))
        self.assertAlmostEqual(condition["ensemble"]["32"]["q05"], 12.45)
        comparison = condition["development_summary_comparison"]
        self.assertEqual(comparison["ensemble_mean"]["mae"], 4.5)
        self.assertEqual(comparison["ensemble_mean"]["rmse"], 4.5)
        self.assertEqual(comparison["constant_fold_1"]["mae"], 12)
        self.assertAlmostEqual(comparison["constant_fold_1"]["rmse"], math.sqrt(145))
        withdrawal = condition["paired_changes"]["withdrawal_90_minus_60"]
        self.assertEqual(withdrawal["collagen_fold"]["mean"], -6)
        self.assertEqual(withdrawal["collagen_fold"]["sd"], 0)
        self.assertEqual(withdrawal["collagen_model_units"]["mean"], -3)
        split = condition["split_half"]["by_day"]["32"]
        self.assertEqual(split["mean_second_minus_first"], 5)
        self.assertAlmostEqual(split["mcse_difference"], 1)

    def test_failed_withdrawal_direction_reported_without_retuning(self):
        self.fill_condition()
        for seed in range(101, 111):
            self.write_run(f"repository_default-{seed}", folds=(1, 12, 14, 16, 20))
        direction = self.report()["conditions"][0]["directional_reproduction"]
        self.assertEqual(direction["status"], "failed_mean_direction")

    def test_replay_and_grid_never_inflate_ensemble(self):
        self.fill_condition()
        self.write_run("seed-replay-101", folds=(1, 1000, 1000, 1000, 1000))
        self.write_run("grid-quarter-day-101", folds=(1, 1000, 1000, 1000, 1000))
        report = self.report()
        self.assertEqual(report["conditions"][0]["ensemble"]["32"]["n"], 10)
        self.assertEqual(report["conditions"][0]["ensemble"]["32"]["mean"], 12)
        self.assertEqual(report["technical_checks"]["seed_replay"]["status"], "mismatch")
        grid = report["technical_checks"]["observation_grid"]
        self.assertEqual(grid["status"], "incomplete_comparison")
        self.assertEqual(grid["value_comparison_status"], "mismatch")

    def test_valid_replay_and_grid_report_numeric_match(self):
        for job in ("repository_default-101", "seed-replay-101", "grid-quarter-day-101"):
            period = self.jobs[job]["period"]
            times = [index * period for index in range(round(240 / period) + 1)]
            self.write_run(job, folds=[1] * len(times), times=times)
        checks = self.report()["technical_checks"]
        self.assertEqual(checks["seed_replay"]["status"], "match")
        self.assertEqual(checks["observation_grid"]["status"], "match")
        self.assertEqual(checks["observation_grid"]["absolute_tolerance"], 1e-8)

    def test_technical_comparison_refuses_changed_model_hash(self):
        self.write_run("repository_default-101")
        self.write_run("seed-replay-101", overrides={"model_sha256": "changed-model"})
        check = self.report()["technical_checks"]["seed_replay"]
        self.assertEqual(check["status"], "not_performed")
        self.assertEqual(check["check_job"]["analysis_status"], "invalid_input")

    def test_primary_run_model_digest_must_match_pinned_source(self):
        self.write_run("repository_default-101", overrides={"model_sha256": "altered"})
        run = self.report()["conditions"][0]["runs"][0]
        self.assertEqual(run["analysis_status"], "invalid_input")
        self.assertIn("source-lock", run["reason"])

    def test_missing_environment_is_explicitly_unverified(self):
        provenance = self.report()["provenance"]
        self.assertTrue(provenance["frozen_original_specification_verified"])
        self.assertEqual(provenance["environment_verification"]["status"], "missing")

    def write_environment(self, benchmark_hash):
        environment = {"benchmark_sha256": benchmark_hash,
                       "source_lock_sha256": analysis.runner.digest(HERE / "source-lock.json"),
                       "runner_sha256": analysis.runner.digest(HERE / "run_benchmark.py")}
        (self.results / "environment.json").write_text(json.dumps(environment))

    def test_environment_checked_against_original_bytes_not_json_reserialization(self):
        frozen_hash = analysis.runner.digest(HERE / "benchmark-v1.1.0.json")
        self.assertNotEqual(analysis.runner.digest(self.results / "specification.json"), frozen_hash)
        self.write_environment(frozen_hash)
        status = self.report()["provenance"]["environment_verification"]["status"]
        self.assertEqual(status, "benchmark_and_source_lock_hashes_verified")

    def test_wrong_environment_benchmark_hash_rejected(self):
        self.write_environment(analysis.runner.digest(self.results / "specification.json"))
        with self.assertRaisesRegex(ValueError, "original frozen bytes"):
            self.report()

    def test_wrong_environment_source_lock_hash_rejected(self):
        self.write_environment(analysis.runner.digest(HERE / "benchmark-v1.1.0.json"))
        path = self.results / "environment.json"
        environment = json.loads(path.read_text())
        environment["source_lock_sha256"] = "altered"
        path.write_text(json.dumps(environment))
        with self.assertRaisesRegex(ValueError, "source-lock digest"):
            self.report()

    def test_timeout_prefix_comparison_is_separate_from_ensemble(self):
        previous = self.root / "previous"
        self.write_run("repository_default-101")
        self.write_run("repository_default-101", folds=(1,), times=(0,), status="timeout", results=previous, gc=False)
        report = self.report(previous)
        check = report["technical_checks"]["gc_amendment_prefix"]
        self.assertEqual(check["status"], "match")
        self.assertTrue(check["prefix_only"])
        self.assertEqual(check["compared_rows"], 1)
        self.assertEqual(check["previous_run"]["analysis_status"], "partial_for_technical_comparison_only")
        self.assertIsNone(report["conditions"][0]["ensemble"])

    def test_gc_comparison_refuses_undeclared_argument_change(self):
        previous = self.root / "previous"
        self.write_run("repository_default-101")
        record = self.write_run("repository_default-101", folds=(1,), times=(0,), status="timeout", results=previous, gc=False)
        record["argv"].append("--other-behavior")
        (previous / "repository_default-101" / "run.json").write_text(json.dumps(record))
        check = self.report(previous)["technical_checks"]["gc_amendment_prefix"]
        self.assertEqual(check["status"], "not_performed")
        self.assertEqual(check["previous_run"]["analysis_status"], "invalid_input")

    def test_previous_v1_command_cannot_inherit_v11_gc_flag(self):
        previous = self.root / "previous"
        self.write_run("repository_default-101")
        self.write_run("repository_default-101", folds=(1,), times=(0,), status="timeout", results=previous, gc=True)
        check = self.report(previous)["technical_checks"]["gc_amendment_prefix"]
        self.assertEqual(check["status"], "not_performed")
        self.assertEqual(check["previous_run"]["analysis_status"], "invalid_input")
        self.assertIn("argv", check["previous_run"]["reason"])

    def test_previous_specification_is_required_for_prefix_check(self):
        previous = self.root / "previous"
        self.write_run("repository_default-101")
        self.write_run("repository_default-101", folds=(1,), times=(0,), status="timeout", results=previous, gc=False)
        (previous / "specification.json").unlink()
        check = self.report(previous)["technical_checks"]["gc_amendment_prefix"]
        self.assertEqual(check["status"], "not_performed")
        self.assertEqual(check["previous_provenance"]["status"], "missing")

    def test_contrasts_require_full_conditions_and_use_fixed_paired_seeds(self):
        self.fill_condition()
        self.fill_condition("without_reinactivation", delta=3)
        contrasts = self.report()["condition_contrasts"]
        self.assertEqual(contrasts[0]["status"], "withheld")
        variant = contrasts[1]
        self.assertEqual(variant["status"], "descriptive_only")
        self.assertEqual(variant["by_day"]["32"]["paired_difference"]["mean"], 3)
        self.assertEqual(variant["by_day"]["32"]["paired_difference"]["n"], 5)
        self.assertNotEqual(variant["reference_model_file"], variant["alternative_model_file"])
        self.assertIn("not necessarily a single-parameter", variant["interpretation"])
        (self.results / "repository_default-110" / "run.json").unlink()
        self.assertEqual(self.report()["condition_contrasts"][1]["status"], "withheld")

    def test_five_seed_condition_has_no_invented_split_half(self):
        self.fill_condition("without_reinactivation")
        condition = self.report()["conditions"][2]
        self.assertEqual(condition["status"], "complete")
        self.assertEqual(condition["split_half"]["status"], "not_applicable")

    def test_all_primary_conditions_complete_without_technical_jobs(self):
        for condition in self.spec["conditions"]:
            self.fill_condition(condition["id"])
        report = self.report()
        self.assertEqual(report["status"], "all_primary_conditions_complete")
        self.assertEqual(report["technical_checks"]["seed_replay"]["status"], "not_performed")
        json.dumps(report, allow_nan=False)

    def test_specification_mismatch_rejected(self):
        changed = copy.deepcopy(self.spec)
        changed["version"] = "different"
        with self.assertRaises(ValueError):
            analysis.analyze(self.results, changed)

    def test_unexpected_job_directory_is_reported_and_excluded(self):
        folder = self.results / "unplanned-seed"
        folder.mkdir()
        (folder / "run.json").write_text("{}")
        self.assertEqual(self.report()["unexpected_job_directories_ignored"], ["unplanned-seed"])

    def test_cli_outputs_valid_json_and_refuses_overwrite(self):
        self.write_run("repository_default-101")
        output = self.root / "analysis.json"
        command = [sys.executable, "-B", str(HERE / "analyze_benchmark.py"),
                   "--results", str(self.results), "--output", str(output)]
        first = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        content = output.read_bytes()
        self.assertEqual(json.loads(content)["status"], "incomplete")
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(second.returncode, 2)
        self.assertEqual(output.read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
