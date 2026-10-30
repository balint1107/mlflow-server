"""Exercise startup argument forwarding without Docker or an MLflow install."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class StartupTests(unittest.TestCase):
    def invoke(self, *arguments):
        """Run the entrypoint with a fake mlflow; return its captured argument lines."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            executable = path / 'mlflow'
            executable.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
            executable.chmod(0o755)
            env = dict(os.environ, PATH=str(path) + os.pathsep + os.environ['PATH'])
            result = subprocess.run(['bash', str(Path(__file__).parents[1] / 'start-server.sh'),
                                     *arguments], env=env, check=True, capture_output=True, text=True)
            return result.stdout.splitlines()

    def test_new_install_uses_persistent_sqlite(self):
        """Keep new standalone metadata/artifacts on their mounted durable paths."""
        args = self.invoke()
        self.assertEqual(args[0], 'server')
        self.assertIn('sqlite:////mlruns/mlflow.db', args)
        self.assertEqual(args[-1], '/mlartifacts')

    def test_existing_file_store_arguments_are_preserved(self):
        """Never silently replace explicit existing-store configuration or split values."""
        args = ['--backend-store-uri', 'file:///mlruns', '--allowed-hosts', 'localhost:*,example.org']
        self.assertEqual(self.invoke(*args), ['server', *args])


if __name__ == '__main__':
    unittest.main()
