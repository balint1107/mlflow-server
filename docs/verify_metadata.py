"""Read-only comparison of experiment/run API metadata before a version rollout."""
import json
import sys
import urllib.request


def pages(base, path, body, key):
    """Return all keyed results from POST search at base/path with JSON body."""
    result = []
    while True:
        request = urllib.request.Request(base + path, data=json.dumps(body).encode(),
                                         headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=30) as response:
            page = json.load(response)
        result.extend(page.get(key, []))
        if not page.get('next_page_token'):
            return result
        body = dict(body, page_token=page['next_page_token'])


def snapshot(base):
    """Return experiment/run maps from base, including deleted records; never mutate data."""
    experiments = pages(base, '/api/2.0/mlflow/experiments/search',
                        {'view_type': 'ALL', 'max_results': 1000}, 'experiments')
    runs = []
    for experiment in experiments:
        runs.extend(pages(base, '/api/2.0/mlflow/runs/search', {
            'experiment_ids': [experiment['experiment_id']],
            'run_view_type': 'ALL', 'max_results': 1000}, 'runs'))
    # Newer MLflow adds the default workspace to previously unscoped experiments.
    for experiment in experiments:
        if experiment.get('workspace') == 'default':
            experiment.pop('workspace')
    return ({x['experiment_id']: x for x in experiments},
            {x['info']['run_id']: x for x in runs})


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit('Usage: verify_metadata.py OLD_BASE_URL NEW_BASE_URL')
    old, new = map(snapshot, sys.argv[1:])
    if old != new:
        raise SystemExit('Experiment/run metadata differs; do not activate the upgrade.')
    print(f'Metadata matches: {len(old[0])} experiments, {len(old[1])} runs')
