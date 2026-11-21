"""Static and local-behavior regression tests for the OpenCode V2 sandbox kit.

These tests exercise the kit sources and the shell behavior that can run
without Docker, a network, an sbx/Windows host, or provider credentials. They do
NOT prove runtime properties such as native ``sbx`` creation, host proxy
credential injection, or ChatGPT OAuth; those stay on the manual checklist in
``sandbox/opencode/README.md``.
"""

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "sandbox" / "opencode"
DOCKERFILE = KIT / "opencode.dockerfile"
DESCRIPTOR = KIT / "opencode.yaml"
ENTRYPOINT = KIT / "files" / "entrypoint.sh"
SHELL_ENV = KIT / "files" / "shell-env.sh"
SMOKE_TEST = KIT / "files" / "smoke-test.sh"
GITATTRIBUTES = ROOT / ".gitattributes"

# Descriptor argument name -> companion Dockerfile build argument.
VERSION_PAIRS = {
    "opencodeVersion": "OPENCODE_VERSION",
    "goVersion": "GO_VERSION",
    "gvmCommit": "GVM_COMMIT",
    "nodeVersion": "NODE_VERSION",
    "uvVersion": "UV_VERSION",
}


class OpenCodeSandboxTests(unittest.TestCase):
    # -- parsing helpers ---------------------------------------------------

    def descriptor_arg_block(self):
        text = DESCRIPTOR.read_text(encoding="utf-8")
        match = re.search(r"^args:\n(.*?)(?=^\S)", text, re.M | re.S)
        self.assertIsNotNone(match, "descriptor args block not found")
        return match.group(1)

    def descriptor_arg_default(self, name):
        block = self.descriptor_arg_block()
        match = re.search(rf"^  {re.escape(name)}:\n((?:    .*\n?)+)", block, re.M)
        self.assertIsNotNone(match, f"descriptor arg {name!r} not found")
        default = re.search(r'^\s+default:\s*"?([^"\n]+)"?\s*$', match.group(1), re.M)
        self.assertIsNotNone(default, f"descriptor arg {name!r} has no default")
        return default.group(1)

    def dockerfile_arg(self, name):
        match = re.search(
            rf"^ARG {re.escape(name)}=(.+)$", DOCKERFILE.read_text(encoding="utf-8"), re.M
        )
        self.assertIsNotNone(match, f"dockerfile build arg {name!r} not found")
        return match.group(1).strip()

    def run_shell_script(self, script_body):
        """Source shell-env.sh under ``set -u`` in a clean, offline shell.

        ``GVM_ROOT`` points at an empty temp directory so the real gvm loader is
        never present and the source script's fallback path is exercised.
        """
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            gvm_root = home / "gvm"
            env = os.environ.copy()
            env.pop("BASH_ENV", None)
            for variable in ("GO_VERSION", "GOROOT", "GOPATH", "GOTOOLCHAIN", "GVM_NO_GIT_BAK"):
                env.pop(variable, None)
            env.update(
                {"HOME": str(home), "GVM_ROOT": str(gvm_root), "PATH": "/usr/bin:/bin"}
            )
            script = f'set -u\n. "{SHELL_ENV}"\n{script_body}'
            result = subprocess.run(
                ["bash", "-c", script], env=env, text=True, capture_output=True
            )
            return result, gvm_root

    def run_entrypoint(self, args, exit_code=0):
        """Run entrypoint.sh against a mock ``opencode`` and return (result, argv).

        The mock lives in a directory whose name contains a space, records each
        argument on its own line, and exits with ``exit_code`` so argument
        boundaries and exit-code propagation are observable.
        """
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        bindir = root / "bin dir"
        bindir.mkdir()
        mock = bindir / "opencode"
        mock.write_text(
            "#!/usr/bin/env bash\n"
            "printf '%s\\n' \"$@\" > \"$MOCK_ARGS_FILE\"\n"
            'exit "${MOCK_EXIT_CODE:-0}"\n',
            encoding="utf-8",
        )
        mock.chmod(0o755)
        args_file = root / "args.txt"
        home = root / "home"
        for child in ("", "data", "config", "state", "cache"):
            (home / child).mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env.pop("BASH_ENV", None)
        env.update(
            {
                "PATH": f"{bindir}:{env.get('PATH', '/usr/bin:/bin')}",
                "HOME": str(home),
                "XDG_DATA_HOME": str(home / "data"),
                "XDG_CONFIG_HOME": str(home / "config"),
                "XDG_STATE_HOME": str(home / "state"),
                "XDG_CACHE_HOME": str(home / "cache"),
                "MOCK_ARGS_FILE": str(args_file),
                "MOCK_EXIT_CODE": str(exit_code),
            }
        )
        result = subprocess.run(
            ["bash", str(ENTRYPOINT), *args], env=env, text=True, capture_output=True
        )
        recorded = args_file.read_text(encoding="utf-8").splitlines() if args_file.exists() else []
        return result, recorded

    # -- static descriptor / image contracts -------------------------------

    def test_descriptor_is_native_v3_workload(self):
        text = DESCRIPTOR.read_text(encoding="utf-8")
        self.assertIn('schemaVersion: "3"', text)
        self.assertIn("kind: workload", text)
        self.assertIn("syntax=docker/sandbox-kit:3", text)
        self.assertIn("opencode@${{ kit.args.opencodeVersion }}", text)

    def test_descriptor_and_dockerfile_version_pins_agree(self):
        for descriptor_arg, docker_arg in VERSION_PAIRS.items():
            with self.subTest(arg=descriptor_arg):
                self.assertEqual(
                    self.descriptor_arg_default(descriptor_arg),
                    self.dockerfile_arg(docker_arg),
                )

    def test_image_installs_v2_cli_package_not_v1(self):
        text = DOCKERFILE.read_text(encoding="utf-8")
        self.assertIn("@opencode/cli@", text)
        self.assertNotIn("opencode-ai", text)
        self.assertTrue(self.descriptor_arg_default("opencodeVersion").startswith("2."))

    def test_image_targets_ubuntu_linux_amd64(self):
        text = DOCKERFILE.read_text(encoding="utf-8")
        self.assertIn("FROM ubuntu:24.04", text)
        self.assertIn("linux-amd64", text)
        self.assertIn("linux-x64", text)
        self.assertNotIn("arm64", text)
        self.assertNotIn("aarch64", text)

    def test_credential_is_proxy_managed_without_embedded_key(self):
        text = DESCRIPTOR.read_text(encoding="utf-8")
        self.assertIn("service: opencode-go", text)
        self.assertIn("proxyManaged: true", text)
        self.assertIn("optional: true", text)
        self.assertIn("name: OPENCODE_API_KEY", text)
        self.assertNotRegex(text, r"\bsk-[A-Za-z0-9_-]{8,}")

    def test_kit_sources_never_disable_tls_verification(self):
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (DOCKERFILE, SHELL_ENV, SMOKE_TEST, DESCRIPTOR)
        )
        self.assertNotRegex(combined, r"GIT_SSL_NO_VERIFY=(?:\"|')?1")
        self.assertNotRegex(combined, r"NODE_TLS_REJECT_UNAUTHORIZED=(?:\"|')?0")

    # -- line endings / scope ----------------------------------------------

    def test_gitattributes_lf_scope_is_limited_to_kit(self):
        rules = [
            line.strip()
            for line in GITATTRIBUTES.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        self.assertEqual(rules, ["sandbox/opencode/** text eol=lf"])

    def test_kit_text_files_are_lf_only(self):
        for path in sorted(KIT.rglob("*")):
            if path.is_file():
                with self.subTest(path=str(path.relative_to(ROOT))):
                    data = path.read_bytes()
                    self.assertNotIn(b"\r\n", data)
                    self.assertTrue(data.endswith(b"\n"))

    # -- shell scripts ------------------------------------------------------

    def test_shell_scripts_parse(self):
        for script in (ENTRYPOINT, SHELL_ENV, SMOKE_TEST):
            with self.subTest(script=script.name):
                result = subprocess.run(
                    ["bash", "-n", str(script)], text=True, capture_output=True
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_shell_env_is_quiet_when_sourced(self):
        result, _ = self.run_shell_script("")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_shell_env_exports_pinned_toolchain_and_proxy_ca(self):
        go_version = self.descriptor_arg_default("goVersion")
        result, gvm_root = self.run_shell_script(
            'printf "%s\\n" "$GOTOOLCHAIN" "$SSL_CERT_FILE" "$GOROOT" "$GOPATH"'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(lines[0], "local")
        self.assertEqual(lines[1], "/etc/ssl/certs/ca-certificates.crt")
        self.assertEqual(lines[2], str(gvm_root / "gos" / f"go{go_version}"))
        self.assertEqual(lines[3], str(gvm_root / "pkgsets" / f"go{go_version}" / "global"))

    def test_shell_env_is_idempotent_for_path(self):
        go_version = self.descriptor_arg_default("goVersion")
        result, gvm_root = self.run_shell_script(
            f'. "{SHELL_ENV}"\nprintf "%s\\n" "$PATH"'
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        path_entries = result.stdout.strip().split(":")
        for directory in (
            "/home/agent/.local/bin",
            str(gvm_root / "bin"),
            str(gvm_root / "gos" / f"go{go_version}" / "bin"),
        ):
            self.assertEqual(path_entries.count(directory), 1, result.stdout)

    def test_image_wires_shell_env_into_noninteractive_and_login_shells(self):
        text = DOCKERFILE.read_text(encoding="utf-8")
        self.assertIn("ENV BASH_ENV=/etc/sandbox-persistent.sh", text)
        self.assertIn(". /usr/local/share/opencode-kit/shell-env.sh", text)
        self.assertIn("/etc/profile.d/sandbox-persistent.sh", text)
        self.assertIn("/home/agent/.bashrc", text)

    def test_shell_env_directory_permissions_are_normalized(self):
        text = DOCKERFILE.read_text(encoding="utf-8")
        directory = "/usr/local/share/opencode-kit"
        preparation = f"install -d -m 0755 {directory}"
        copy = "COPY --chmod=0644 files/shell-env.sh"
        self.assertLess(text.index(preparation), text.index(copy))
        # Exercise the same commands on an existing restrictive directory;
        # the mode must not depend on host context permissions or umask.
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "opencode-kit"
            target.mkdir(mode=0o700)
            script = target / "shell-env.sh"
            script.write_text("# shell environment\n", encoding="utf-8")
            script.chmod(0o600)
            commands = [
                preparation,
                f"chmod 0755 {directory}",
                f"chmod 0644 {directory}/shell-env.sh",
            ]
            for command in commands:
                self.assertIn(command, text)
            result = subprocess.run(
                ["bash", "-c", "umask 077; " + "; ".join(commands).replace(directory, '"' + str(target) + '"')],
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.stat().st_mode & 0o777, 0o755)
            self.assertEqual(script.stat().st_mode & 0o777, 0o644)

    def test_entrypoint_defaults_to_standalone_without_arguments(self):
        result, recorded = self.run_entrypoint([])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(recorded, ["--standalone"])

    def test_entrypoint_forwards_explicit_arguments_verbatim(self):
        result, recorded = self.run_entrypoint(["debug", "paths", "db", "two words"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(recorded, ["debug", "paths", "db", "two words"])
        self.assertNotIn("--standalone", recorded)

    def test_entrypoint_propagates_child_exit_code(self):
        result, recorded = self.run_entrypoint(["run", "hello"], exit_code=7)
        self.assertEqual(result.returncode, 7)
        self.assertEqual(recorded, ["run", "hello"])


if __name__ == "__main__":
    unittest.main()
