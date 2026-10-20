"""Execute R24 development pilots. No confirmatory mode is provided.

Example on an authenticated GPU runtime:
  python run_development.py --projects 01,05,09,13 --seeds 0,1,2 --output runs/dev01

Every evaluation here is DEVELOPMENT and may inform a successor protocol.
Never report these outputs as protected confirmation or real-market evidence.
"""
from __future__ import annotations
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import time
import traceback
import torch
from torch import nn
import core


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def save(path, value):
    torch.save(value, Path(path))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tensor_digest(tensors):
    h = hashlib.sha256()
    for t in tensors:
        h.update(str((tuple(t.shape), str(t.dtype))).encode())
        h.update(t.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def features(model, x, burn=12):
    return model(x)[:, burn:]


def fit_selected(xs, ys, vx, vy, candidates, fit):
    records, best = [], None
    for settings in candidates:
        w = fit(xs, ys, *settings)
        loss = (vx @ w - vy).square().mean().item()
        records.append({'settings': list(settings), 'validation_mse': loss})
        if best is None or loss < best[0]:
            best = (loss, settings, w)
    return best[1], best[2], records


def forecast_scores(pred, target, scale):
    per_trajectory = (pred - target).square().mean((1, 2)) / scale
    return {'nmse': per_trajectory.mean().item(),
            'trajectory_nmse': per_trajectory.detach().cpu().tolist()}


@torch.no_grad()
def project01(seed, out, device, steps):
    model = core.FixedReservoir(4, 32, seed, device)
    base = 100000 + 100 * seed
    train = [core.finance_scm(16, 128, base + i, a, device)
             for i, a in enumerate((.5, 1., 2.))]
    valid = [core.finance_scm(8, 128, base + 10 + i, a, device)
             for i, a in enumerate((.5, 1., 2.))]
    # OOD here is an inspected DEVELOPMENT evaluation, not a protected test.
    tx, ty = core.finance_scm(24, 128, base + 20, -1., device)
    x = [features(model, a).flatten(0, 1) for a, b in train]
    y = [b[:, 12:].flatten(0, 1) for a, b in train]
    vx = torch.cat([features(model, a).flatten(0, 1) for a, b in valid])
    vy = torch.cat([b[:, 12:].flatten(0, 1) for a, b in valid])
    test = features(model, tx); target = ty[:, 12:]
    scale = torch.cat(y).var(unbiased=False).clamp_min(1e-12)
    ridge_grid = [(10. ** exponent,) for exponent in range(-6, 3)]
    invariant_grid = [(r, g) for r in (1e-4, 1e-2, 1.) for g in (.1, 1., 10.)]
    settings, w, trace = fit_selected(x, y, vx, vy, invariant_grid,
                                      lambda a, b, r, g: core.invariant_ridge(a, b, r, g))
    _, w0, trace0 = fit_selected(x, y, vx, vy, ridge_grid,
                                 lambda a, b, r: core.invariant_ridge(a, b, r, 0))
    _, wl, tracel = fit_selected([a[:, :5] for a in x], y, vx[:, :5], vy, ridge_grid,
                                  lambda a, b, r: core.invariant_ridge(a, b, r, 0))
    predictions = {'invariant_reservoir': test @ w, 'ridge_reservoir': test @ w0,
                   'linear_lag_baseline': test[:, :, :5] @ wl}
    save(out / 'data.pt', {'train': train, 'validation': valid, 'development_ood': (tx, ty)})
    save(out / 'checkpoint.pt', {'reservoir': model.state_dict(), 'invariant': w,
                                 'ridge': w0, 'linear': wl})
    save(out / 'predictions.pt', {'predictions': predictions, 'target': target})
    return {'project': '01', 'selected': list(settings), 'candidate_fits_per_arm': 9,
            'selection_trace': {'invariant': trace, 'ridge': trace0, 'linear': tracel},
            'data_hash': tensor_digest([t for pair in train + valid + [(tx, ty)] for t in pair]),
            'scores': {k: forecast_scores(v, target, scale) for k, v in predictions.items()},
            'limits': 'Synthetic SCM only. Invariance is not identified financial causality. No GRU/SOTA comparator yet.'}


@torch.no_grad()
def project05(seed, out, device, steps):
    base = 200000 + 100 * seed
    train = core.delayed_task(12, 160, base, device)
    valid = core.delayed_task(8, 160, base + 1, device)
    evaluation = core.delayed_task(16, 160, base + 2, device, input_scale=1.5)
    grids = {
        'adaptive_gate': [(s, a, .01) for s in (.01, .03, .1) for a in (-2., 0., 2.)],
        'uniform_noise': [(s, 0., r) for s in (.01, .03, .1) for r in (.0001, .01, 1.)],
        'zero_noise': [(0., 0., 10. ** e) for e in range(-6, 3)],
    }
    selected, traces, weights = {}, {}, {}
    def make(cfg, split, split_index):
        m = core.PhysicalReservoir(cfg, seed, device)
        f, energy = m(split[0], base + 10 + split_index)
        return m, f[:, 12:], energy
    for name, grid in grids.items():
        best, trace = None, []
        for sigma, alpha, regularization in grid:
            cfg = core.PhysicalConfig(sigma=sigma, alpha=alpha)
            _, f, _ = make(cfg, train, 0); _, vf, _ = make(cfg, valid, 1)
            w = core.ridge(f.flatten(0, 1), train[1][:, 12:].flatten(0, 1), regularization)
            value = (vf @ w - valid[1][:, 12:]).square().mean().item()
            trace.append({'sigma': sigma, 'alpha': alpha, 'ridge': regularization, 'validation_mse': value})
            if best is None or value < best[0]:
                best = (value, cfg, regularization, w)
        selected[name] = {'physical': asdict(best[1]), 'ridge': best[2]}
        weights[name], traces[name] = best[3], trace
    # Exact selected-power ablation, in addition to an independently tuned control.
    chosen = selected['adaptive_gate']
    matched_cfg = core.PhysicalConfig(**{**chosen['physical'], 'alpha': 0.})
    _, mf, _ = make(matched_cfg, train, 0)
    weights['matched_gate_off'] = core.ridge(mf.flatten(0, 1), train[1][:, 12:].flatten(0, 1), chosen['ridge'])
    selected['matched_gate_off'] = {'physical': asdict(matched_cfg), 'ridge': chosen['ridge']}
    predictions, energy = {}, {}
    for name, params in selected.items():
        _, f, energy[name] = make(core.PhysicalConfig(**params['physical']), evaluation, 2)
        predictions[name] = f @ weights[name]
    target = evaluation[1][:, 12:]
    scale = train[1][:, 12:].var(unbiased=False).clamp_min(1e-12)
    save(out / 'data.pt', {'train': train, 'validation': valid, 'development_ood': evaluation})
    save(out / 'checkpoint.pt', {'weights': weights, 'selected': selected, 'substrate_seed': seed})
    save(out / 'predictions.pt', {'predictions': predictions, 'target': target})
    return {'project': '05', 'selected': selected, 'selection_trace': traces, 'energy': energy,
            'data_hash': tensor_digest(list(train + valid + evaluation)),
            'candidate_fits_per_tuned_arm': 9,
            'scores': {k: forecast_scores(v, target, scale) for k, v in predictions.items()},
            'limits': 'Simulated double-well lattice, not hardware or turbulence. Solver refinement and strong ESN baseline remain required.'}


def project09(seed, out, device, steps):
    inputs, width, classes = 8, 12, 3
    n = core.mlp_parameters(inputs, width, classes)
    g = core.generator(300000 + seed, device)
    teacher = torch.randn(n, generator=g, device=device) * .4
    def dataset(size):
        x = torch.randn(size, inputs, generator=g, device=device)
        y = core.flat_mlp(teacher, x, width, classes).argmax(-1)
        return x, y
    train, valid, evaluation = dataset(384), dataset(128), dataset(256)
    initial = torch.randn(n, generator=g, device=device) * .1
    scores, snapshots, traces = {}, {}, {}
    for method, blocks in (('full_antithetic', 1), ('block_antithetic', 4), ('backprop_reference', 0)):
        theta = initial.clone()
        random = core.generator(310000 + seed, device)
        batches = core.generator(320000 + seed, device)
        trace = []
        for step in range(steps):
            index = torch.randint(len(train[0]), (64,), generator=batches, device=device)
            bx, by = train[0][index], train[1][index]
            def loss(t):
                return nn.functional.cross_entropy(core.flat_mlp(t, bx, width, classes), by)
            if blocks:
                d, p, _ = core.block_direction(theta, blocks, random)
                gradient = core.antithetic_estimate(loss, theta, d, .001, p)
            else:
                theta.requires_grad_(True)
                gradient, = torch.autograd.grad(loss(theta), theta)
                theta = theta.detach()
            theta = core.finite(theta - .005 * gradient, 'updated parameters').detach()
            if step % 25 == 0 or step + 1 == steps:
                with torch.no_grad():
                    vl = nn.functional.cross_entropy(core.flat_mlp(theta, valid[0], width, classes), valid[1]).item()
                trace.append({'step': step + 1, 'validation_cross_entropy': vl})
        with torch.no_grad():
            logits = core.flat_mlp(theta, evaluation[0], width, classes)
            scores[method] = {'cross_entropy': nn.functional.cross_entropy(logits, evaluation[1]).item(),
                              'accuracy': (logits.argmax(-1) == evaluation[1]).float().mean().item(),
                              'training_forward_evaluations': steps * (2 if blocks else 1),
                              'training_reverse_evaluations': 0 if blocks else steps}
            save(out / f'{method}_predictions.pt', {'logits': logits, 'labels': evaluation[1]})
        snapshots[method], traces[method] = theta, trace
    save(out / 'checkpoint.pt', {'parameters': snapshots, 'initial': initial, 'teacher': teacher})
    save(out / 'data.pt', {'train': train, 'validation': valid, 'development_evaluation': evaluation})
    return {'project': '09', 'scores': scores, 'traces': traces,
            'data_hash': tensor_digest(list(train + valid + evaluation)),
            'limits': 'Small synthetic MLP. Hyperparameters fixed, not comprehensively calibrated. Equal forward calls do not imply equal FLOPs or memory.'}


def project13(seed, out, device, steps):
    torch.manual_seed(seed)
    model = core.AssociativeMemory(64, 8, 32).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=.003)
    for step in range(steps):
        k, v, q, y, index = core.memory_batch(64, 8, 64, 8, 400000 + seed * 10000 + step, device)
        opt.zero_grad(set_to_none=True)
        loss = nn.functional.cross_entropy(model(k, v, q), y)
        core.finite(loss, 'memory training loss').backward(); opt.step()
    model.eval()
    k, v, q, y, index = core.memory_batch(256, 16, 64, 8, 500000 + seed, device)
    variants = core.memory_interventions(k, v, index, 8)
    row = torch.arange(len(y), device=device)
    scores, predictions = {}, {}
    with torch.no_grad():
        for name, (values, keep) in variants.items():
            logits = model(k, values, q, keep)
            pred = logits.argmax(-1)
            predictions[name] = logits
            scores[name] = {'accuracy_original_target': (pred == y).float().mean().item()}
            if name == 'replace_relevant_value':
                scores[name]['accuracy_replacement_target'] = (pred == values[row, index]).float().mean().item()
    save(out / 'checkpoint.pt', {'model': model.state_dict(), 'optimizer': opt.state_dict()})
    save(out / 'data.pt', {'keys': k, 'values': v, 'query': q, 'target': y, 'index': index})
    save(out / 'predictions.pt', predictions)
    gap = scores['delete_irrelevant']['accuracy_original_target'] - scores['delete_relevant']['accuracy_original_target']
    return {'project': '13', 'scores': scores, 'selective_necessity_gap': gap,
            'exact_lookup_accuracy': (v[row, (k == q[:, None]).long().argmax(-1)] == y).float().mean().item(),
            'data_hash': tensor_digest([k, v, q, y, index]),
            'limits': 'Controlled associative task only, not an LLM memory result. Oracle lookup should be perfect; no superiority over it is claimed.'}


PROJECTS = {'01': project01, '05': project05, '09': project09, '13': project13}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--projects', default='01,05,09,13')
    parser.add_argument('--seeds', default='0,1,2')
    parser.add_argument('--steps', type=int, default=200)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    projects, seeds = args.projects.split(','), [int(s) for s in args.seeds.split(',')]
    if len(set(projects)) != len(projects) or not set(projects) <= PROJECTS.keys():
        parser.error('Specify unique projects from 01,05,09,13')
    if not seeds or len(set(seeds)) != len(seeds) or min(seeds) < 0 or args.steps < 1 or args.steps >= 10000:
        parser.error('Unique nonnegative seeds and 1<=steps<10000 required')
    args.output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parent
    manifest = {'phase': 'DEVELOPMENT', 'projects': projects, 'seeds': seeds, 'steps': args.steps,
                'created_utc': datetime.now(timezone.utc).isoformat(),
                'source_sha256': {p.name: sha(p) for p in root.glob('*.py')},
                'python': platform.python_version(), 'torch': torch.__version__,
                'cuda_build': torch.version.cuda, 'status': 'PREFLIGHT'}
    try:
        manifest['git_commit'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        manifest['git_commit'] = 'unavailable; source hashes remain authoritative'
    dump(args.output / 'manifest.json', manifest)
    failures = []
    try:
        device = core.require_gpu()
        torch.use_deterministic_algorithms(True)
        manifest['gpu'] = torch.cuda.get_device_name(device)
        manifest['status'] = 'RUNNING'; dump(args.output / 'manifest.json', manifest)
        for project in projects:
            for seed in seeds:
                out = args.output / f'p{project}_seed{seed}'; out.mkdir()
                torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
                torch.cuda.synchronize(); torch.cuda.reset_peak_memory_stats()
                before = torch.cuda.memory_allocated(); start = time.perf_counter()
                try:
                    result = PROJECTS[project](seed, out, device, args.steps)
                    torch.cuda.synchronize()
                    result.update(seed=seed, phase='DEVELOPMENT', elapsed_seconds=time.perf_counter()-start,
                                  peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
                                  cuda_allocated_before_bytes=before, empirical_disposition='UNCONFIRMED')
                    dump(out / 'metrics.json', result)
                except Exception as exc:
                    failure = {'project': project, 'seed': seed, 'error': repr(exc), 'traceback': traceback.format_exc()}
                    dump(out / 'failure.json', failure); failures.append(failure)
                finally:
                    torch.cuda.empty_cache()
        manifest['status'] = 'DEVELOPMENT_FINISHED_WITH_FAILURES' if failures else 'DEVELOPMENT_FINISHED'
    except Exception as exc:
        manifest['status'] = 'BLOCKED'
        failures.append({'stage': 'preflight', 'error': repr(exc), 'traceback': traceback.format_exc()})
    finally:
        manifest['finished_utc'] = datetime.now(timezone.utc).isoformat()
        manifest['failure_count'] = len(failures)
        dump(args.output / 'manifest.json', manifest)
        dump(args.output / 'failures.json', failures)
    print(json.dumps({'output': str(args.output), 'status': manifest['status'], 'failures': len(failures)}))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
