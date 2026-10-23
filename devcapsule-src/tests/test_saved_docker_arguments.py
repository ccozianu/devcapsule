from __future__ import annotations
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import pytest
from devcapsule import cli
from devcapsule.configuration.docker_arguments import arguments_path, read_arguments
from devcapsule.configuration.execution import ExecutionConfiguration
from devcapsule.configuration.storage import registered_checkouts
from devcapsule.docker_arguments import redact_environment
from devcapsule.materialization import parse_locked_environment
from tests.test_checkout_environment import project, config
from tests.test_project_commands import initialize_codium_project, LOCKED_BASE


def test_saved_args_replace_list_clear_and_share_hidden_env(project, tmp_path, capsys, monkeypatch):
    path = arguments_path(registered_checkouts()[0].record_path)
    args = ['--gpus', 'all', '--volume', f'{tmp_path}/space dir:/data:ro',
            '--label', 'literal=$(touch NO_SHELL)', '--env', 'TOKEN=sensitive=with spaces']
    assert config(project, 'set-extra-docker-args', '--', *args) == 0
    assert read_arguments(path) == args
    assert path.stat().st_mode & 0o777 == 0o600
    assert path.parent.stat().st_mode & 0o777 == 0o700
    capsys.readouterr()
    assert config(project, 'list-extra-docker-args', '--json') == 0
    report = capsys.readouterr().out
    assert 'sensitive' not in report
    assert json.loads(report) == {'path': str(path), 'arguments': redact_environment(args)}
    assert config(project, 'list-extra-docker-args') == 0
    text = capsys.readouterr().out
    assert 'sensitive' not in text and 'TOKEN=<redacted>' in text and f'{tmp_path}/space dir:/data:ro' in text
    monkeypatch.setattr('sys.stdin.isatty', lambda: True)
    with patch('getpass.getpass', return_value='hidden replacement'):
        assert config(project, 'set-env', 'TOKEN') == 0
    assert read_arguments(path) == [*args[:-2], '--env', 'TOKEN=hidden replacement']
    assert config(project, 'unset-env', 'TOKEN') == 0
    assert read_arguments(path) == args[:-2]
    assert config(project, 'set-extra-docker-args', '--', '--gpus=all') == 0
    assert read_arguments(path) == ['--gpus=all']
    assert config(project, 'remove-extra-docker-args') == 0
    assert config(project, 'remove-extra-docker-args') == 0
    assert not path.exists()
    capsys.readouterr()
    assert config(project, 'list-extra-docker-args') == 0
    assert 'No saved extra Docker arguments.' in capsys.readouterr().out


@pytest.mark.parametrize('args', [['--network=host'], ['--memory', '2g'], ['--user', 'root']])
def test_launcher_owned_options_refused_without_changing_saved_list(project, args, capsys):
    assert config(project, 'set-extra-docker-args', '--', '--gpus', 'all') == 0
    path = arguments_path(registered_checkouts()[0].record_path)
    before = path.read_bytes()
    assert config(project, 'set-extra-docker-args', '--', *args) == 2
    assert 'composed by the launcher' in capsys.readouterr().err
    assert path.read_bytes() == before


def test_malformed_store_can_be_replaced_or_removed(project, capsys):
    assert config(project, 'set-extra-docker-args', '--', '--gpus', 'all') == 0
    path = arguments_path(registered_checkouts()[0].record_path)
    path.write_text('broken secret')
    assert config(project, 'list-extra-docker-args') == 2
    assert 'broken secret' not in str(capsys.readouterr())
    assert config(project, 'set-extra-docker-args', '--', '--gpus=all') == 0
    assert read_arguments(path) == ['--gpus=all']
    path.write_text('broken secret')
    assert config(project, 'remove-extra-docker-args') == 0
    assert not path.exists()


@pytest.mark.parametrize('tokens', [ ['--env', 'TOKEN=sentinel'], ['--env=TOKEN=sentinel'],
                                    ['-e', 'TOKEN=sentinel'], ['-eTOKEN=sentinel'], ['-e=TOKEN=sentinel'] ])
def test_all_env_spellings_are_masked(tokens):
    assert 'sentinel' not in str(redact_environment(tokens))
    assert '<redacted>' in str(redact_environment(tokens))
    assert redact_environment(['--env', 'TOKEN', '--env-file', 'private.env']) == ['--env', 'TOKEN', '--env-file', 'private.env']


def test_saved_args_precede_one_offs_and_are_read_each_launch(tmp_path, capsys):
    root = tmp_path / 'project'
    initialize_codium_project(root)
    assert config(root, 'authorize', 'base-image', LOCKED_BASE) == 0
    assert config(root, 'resolve') == 0
    selected = ExecutionConfiguration.load(root).project
    before = selected.resolution_path.read_bytes()
    saved = ['--gpus', 'all', '--volume', '/example/key:/home/devcapsule/key:ro', '--env=APP_SECRET=stored-value']
    assert config(root, 'set-extra-docker-args', '--', *saved) == 0
    realized = SimpleNamespace(image=SimpleNamespace(labels={}, reference='devcapsule-local-codium:fixture'), created=False, locked=parse_locked_environment(selected.lock))
    with patch('devcapsule.commands.project.realize_environment', return_value=realized), patch('devcapsule.commands.project.run_pycharm', return_value=0) as launch:
        assert cli.main(['project', '--path', str(root), 'run', '--', '-eAPP_SECRET=one-off-value']) == 0
        assert launch.call_args.args[0].extra_docker_args == ['--pull=never', *saved, '-eAPP_SECRET=one-off-value']
        assert config(root, 'remove-extra-docker-args') == 0
        assert cli.main(['project', '--path', str(root), 'run']) == 0
        assert launch.call_args.args[0].extra_docker_args == ['--pull=never']
    assert selected.resolution_path.read_bytes() == before
    output = str(capsys.readouterr())
    assert 'stored-value' not in output and 'one-off-value' not in output
