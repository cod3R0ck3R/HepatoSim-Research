#!/usr/bin/env python3
"""Runner-contract tests with synthetic CSVs and a fake process, never KaSim.

Run with ``python3 -B -m unittest discover -s Research/Reference -p test_benchmark.py``.
All test-created files are confined to TemporaryDirectory instances.
"""
import copy
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import signal
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
MODULE_SPEC = importlib.util.spec_from_file_location("benchmark_runner", HERE / "run_benchmark.py")
runner = importlib.util.module_from_spec(MODULE_SPEC)
with patch.object(sys, "dont_write_bytecode", True):
    MODULE_SPEC.loader.exec_module(runner)

HEADER = ["[T]", "COL1 tot", "qHSC", "iHSC", "aSMA-cells"]
COMPLETE_TRACE = "'[T]','COL1 tot','qHSC','iHSC','aSMA-cells'\n0,0.5,100,0,0\n240,1.5,80,10,10\n"


def frozen_spec():
    return json.loads((HERE / "benchmark-v1.0.0.json").read_text())


class TraceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.trace = Path(self.temp.name) / "trace.csv"

    def write_rows(self, rows, header=HEADER):
        with self.trace.open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(header)
            writer.writerows(rows)
        return self.trace

    def test_comments_and_single_quoted_column_names(self):
        self.trace.write_text("# KaSim provenance\n" + COMPLETE_TRACE.replace(
            "240,", "# intermediate comment\n240,"))
        rows = runner.read_trace(self.trace)
        self.assertEqual(set(rows[0]), set(HEADER))
        self.assertEqual(rows[0]["COL1 tot"], 0.5)
        self.assertEqual(rows[-1]["[T]"], 240.0)
        self.assertEqual(len(rows), 2)

    def test_standard_csv_quoted_headers(self):
        self.trace.write_text('"[T]","COL1 tot","qHSC","iHSC","aSMA-cells"\n0,0.5,100,0,0\n')
        self.assertEqual(runner.read_trace(self.trace)[0], dict(zip(HEADER, [0, 0.5, 100, 0, 0])))

    def test_nonfinite_values_rejected_in_every_column(self):
        for column in range(len(HEADER)):
            for nonfinite in ("nan", "inf", "-inf"):
                with self.subTest(column=HEADER[column], value=nonfinite):
                    values = [0, 0.5, 100, 0, 0]
                    values[column] = nonfinite
                    self.write_rows([values])
                    with self.assertRaises(ValueError):
                        runner.read_trace(self.trace)

    def test_descending_times_rejected(self):
        self.write_rows([[1, 0.5, 100, 0, 0], [0, 0.6, 99, 0, 1]])
        with self.assertRaises(ValueError):
            runner.read_trace(self.trace)

    def test_repeated_event_times_allowed_by_frozen_contract(self):
        self.write_rows([[0, 0.5, 100, 0, 0], [0, 0.6, 99, 0, 1]])
        rows = runner.read_trace(self.trace)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[1]["COL1 tot"], 0.6)

    def test_missing_header_observations_and_columns_rejected(self):
        for content in ("", "# comments only\n", ",".join(HEADER) + "\n",
                        "[T],COL1 tot\n0,0.5\n"):
            with self.subTest(content=content):
                self.trace.write_text(content)
                with self.assertRaises(ValueError):
                    runner.read_trace(self.trace)

    def test_nonnumeric_value_rejected(self):
        self.write_rows([[0, "unavailable", 100, 0, 0]])
        with self.assertRaises(ValueError):
            runner.read_trace(self.trace)

    def test_malformed_row_width_rejected_as_validation_error(self):
        for values in ([0, 0.5, 100, 0], [0, 0.5, 100, 0, 0, 7]):
            with self.subTest(values=values):
                self.write_rows([values])
                with self.assertRaisesRegex(ValueError, 'row width'):
                    runner.read_trace(self.trace)

    def test_negative_observation_preserved_for_reporting(self):
        self.write_rows([[0, 0.5, 100, -0.01, 0]])
        self.assertEqual(runner.read_trace(self.trace)[0]["iHSC"], -0.01)


class SamplingTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{"[T]": 0, "COL1 tot": 0.5},
                     {"[T]": 0.5, "COL1 tot": 1.0},
                     {"[T]": 1.0, "COL1 tot": 2.0}]

    def test_exact_time_selects_that_observation(self):
        for row in self.rows:
            with self.subTest(time=row["[T]"]):
                self.assertIs(runner.at_time(self.rows, row["[T]"]), row)

    def test_between_samples_uses_preceding_state_and_actual_timestamp(self):
        self.assertIs(runner.at_time(self.rows, 0.49), self.rows[0])
        self.assertIs(runner.at_time(self.rows, 0.75), self.rows[1])
        self.assertEqual(runner.at_time(self.rows, 0.75)["[T]"], 0.5)

    def test_repeated_event_time_selects_last_recorded_state(self):
        post_event = {"[T]": 0.5, "COL1 tot": 1.5}
        rows = self.rows[:2] + [post_event] + self.rows[2:]
        self.assertIs(runner.at_time(rows, 0.5), post_event)
        self.assertIs(runner.at_time(rows, 0.75), post_event)

    def test_extrapolation_rejected_before_and_after_trace(self):
        for requested in (-0.001, 1.001):
            with self.subTest(time=requested):
                with self.assertRaises(ValueError):
                    runner.at_time(self.rows, requested)


class JobDefinitionTests(unittest.TestCase):
    def test_exactly_32_unique_jobs_match_declared_conditions_and_seeds(self):
        spec = frozen_spec()
        jobs = runner.make_jobs(spec)
        self.assertEqual(len(jobs), 32)
        self.assertEqual(len({job["job_id"] for job in jobs}), 32)
        expected = {
            "repository_default": ("reactMFB-with-inactivation.ka", {}, list(range(101, 111))),
            "caption_literal": ("reactMFB-with-inactivation.ka", {"TGFB1_pool_by_cell": 1}, list(range(101, 111))),
            "without_reinactivation": ("reactMFB-wo-inactivation.ka", {}, list(range(101, 106))),
            "reinactivation_10pct": ("reactMFB-with-inactivation.ka", {"inactivation_pourcentage_react": 0.1}, list(range(101, 106))),
        }
        declared_jobs = jobs[:-2]
        self.assertEqual({job["id"] for job in declared_jobs}, set(expected))
        for condition, (model, overrides, seeds) in expected.items():
            selected = [job for job in declared_jobs if job["id"] == condition]
            with self.subTest(condition=condition):
                self.assertEqual([job["seed"] for job in selected], seeds)
                for job in selected:
                    self.assertEqual(job["file"], model)
                    self.assertEqual(job["overrides"], overrides)
                    self.assertEqual(job["period"], 0.5)
                    self.assertEqual(job["job_id"], f"{condition}-{job['seed']}")

    def test_replay_and_grid_jobs_change_only_declared_fields(self):
        jobs = runner.make_jobs(frozen_spec())
        replay = dict(jobs[0], job_id="seed-replay-101")
        quarter_day = dict(jobs[0], job_id="grid-quarter-day-101", period=0.25)
        self.assertEqual(jobs[-2], replay)
        self.assertEqual(jobs[-1], quarter_day)

    def test_job_creation_does_not_mutate_frozen_spec(self):
        spec = frozen_spec()
        original = copy.deepcopy(spec)
        runner.make_jobs(spec)
        self.assertEqual(spec, original)

    def test_job_budget_cannot_silently_drop_declared_jobs(self):
        spec = frozen_spec()
        spec["budget"]["maximum_runs"] = 31
        with self.assertRaises(ValueError):
            runner.make_jobs(spec)


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.output = self.root / "results"
        self.output.mkdir()
        self.spec = frozen_spec()
        self.spec["budget"]["per_run_timeout_seconds"] = 5
        self.job = runner.make_jobs(self.spec)[0]
        model = self.root / "vendor" / "HSC_model_Kappa" / self.job["file"]
        model.parent.mkdir(parents=True)
        model.write_text("// synthetic process fixture, not an executable Kappa model\n")
        self.model = model
        self.executable = self.root / "fake-kasim"
        self.here_patch = patch.object(runner, "HERE", self.root)
        self.here_patch.start()
        self.addCleanup(self.here_patch.stop)

    def fake_process(self, body):
        self.executable.write_text(
            f"#!{sys.executable}\n"
            "import json, pathlib, sys, time\n"
            "args = sys.argv[1:]\n"
            "folder = pathlib.Path(args[args.index('-d') + 1])\n"
            "(folder / 'received.json').write_text(json.dumps(args))\n"
            "print('synthetic process fixture', flush=True)\n" + body + "\n")
        self.executable.chmod(0o755)

    def execute(self, deadline=None):
        record = runner.run_job(self.job, self.spec, self.executable, self.output,
                                time.monotonic() + 15 if deadline is None else deadline)
        persisted = json.loads((self.output / self.job["job_id"] / "run.json").read_text())
        self.assertEqual(persisted, record)
        return record

    def test_complete_trace_records_provenance_and_declared_arguments(self):
        self.fake_process(f"(folder / 'trace.csv').write_text({COMPLETE_TRACE!r})")
        self.job["overrides"] = {"z_parameter": 2, "a_parameter": 0.1}
        record = self.execute()
        self.assertEqual(record["status"], "completed")
        self.assertEqual(record["returncode"], 0)
        self.assertEqual(record["rows"], 2)
        self.assertEqual(record["last_day"], 240.0)
        self.assertEqual(record["initial_collagen"], 0.5)
        self.assertEqual(record["minimum_observation"], 0.0)
        self.assertEqual(record["trace_sha256"], hashlib.sha256(COMPLETE_TRACE.encode()).hexdigest())
        self.assertEqual(record["model_sha256"], hashlib.sha256(self.model.read_bytes()).hexdigest())
        folder = self.output / self.job["job_id"]
        received = json.loads((folder / "received.json").read_text())
        self.assertEqual(received, record["argv"][1:])
        self.assertEqual(received[:11], [str(self.model), "-l", "243", "-p", "0.5", "-seed", "101", "-mode", "batch", "-d", str(folder)])
        self.assertEqual(received[-6:], ["-var", "a_parameter", "0.1", "-var", "z_parameter", "2"])
        self.assertIn("synthetic process fixture", (folder / "stdout.log").read_text())
        self.assertGreaterEqual(record["wall_seconds"], 0)
        self.assertNotIn("validation_error", record)

    def test_successful_exit_without_trace_is_missing_output(self):
        self.fake_process("sys.exit(0)")
        record = self.execute()
        self.assertEqual(record["status"], "missing_output")
        self.assertEqual(record["returncode"], 0)
        self.assertNotIn("trace_sha256", record)

    def test_nonzero_exit_is_retained_even_with_a_complete_trace(self):
        self.fake_process(f"(folder / 'trace.csv').write_text({COMPLETE_TRACE!r})\nsys.exit(7)")
        record = self.execute()
        self.assertEqual(record["status"], "runtime_error")
        self.assertEqual(record["returncode"], 7)
        self.assertEqual(record["rows"], 2)

    @unittest.skipUnless(hasattr(signal, "SIGTERM") and hasattr(runner.os, "killpg"),
                         "Runner uses POSIX process groups")
    def test_timeout_terminates_process_and_persists_failure(self):
        self.fake_process("time.sleep(30)")
        self.spec["budget"]["per_run_timeout_seconds"] = 0.1
        started = time.monotonic()
        record = self.execute()
        self.assertEqual(record["status"], "timeout")
        self.assertEqual(record["returncode"], -signal.SIGTERM)
        self.assertLess(time.monotonic() - started, 6)

    def test_incomplete_time_coverage_is_invalid_output(self):
        trace = COMPLETE_TRACE.replace("240,", "239.5,")
        self.fake_process(f"(folder / 'trace.csv').write_text({trace!r})")
        record = self.execute()
        self.assertEqual(record["status"], "invalid_output")
        self.assertIn("validation_error", record)
        self.assertEqual(record["last_day"], 239.5)

    def test_unexpected_initial_collagen_is_invalid_output(self):
        trace = COMPLETE_TRACE.replace("0,0.5,", "0,0.6,")
        self.fake_process(f"(folder / 'trace.csv').write_text({trace!r})")
        record = self.execute()
        self.assertEqual(record["status"], "invalid_output")
        self.assertIn("validation_error", record)

    def test_nonfinite_trace_is_invalid_output(self):
        trace = COMPLETE_TRACE.replace("240,1.5,", "240,nan,")
        self.fake_process(f"(folder / 'trace.csv').write_text({trace!r})")
        record = self.execute()
        self.assertEqual(record["status"], "invalid_output")
        self.assertIn("validation_error", record)

    def test_negative_observation_is_reported_without_clamping(self):
        trace = COMPLETE_TRACE.replace("240,1.5,80,10,10", "240,1.5,80,-0.01,10")
        self.fake_process(f"(folder / 'trace.csv').write_text({trace!r})")
        record = self.execute()
        self.assertEqual(record["status"], "completed")
        self.assertEqual(record["minimum_observation"], -0.01)

    def test_expired_budget_does_not_launch_executable(self):
        self.fake_process("raise AssertionError('must not launch')")
        record = self.execute(deadline=time.monotonic() - 1)
        self.assertEqual(record["status"], "budget_exhausted")
        self.assertFalse((self.output / self.job["job_id"] / "received.json").exists())
        self.assertNotIn("returncode", record)

    def test_existing_job_directory_is_never_overwritten(self):
        folder = self.output / self.job["job_id"]
        folder.mkdir()
        marker = folder / "retained.txt"
        marker.write_text("previous evidence")
        self.fake_process("sys.exit(0)")
        with self.assertRaises(FileExistsError):
            self.execute()
        self.assertEqual(marker.read_text(), "previous evidence")


if __name__ == "__main__":
    unittest.main()
