"""R24 mechanism implementations. No empirical efficacy or novelty is asserted.

These are new development implementations, not replacements for historical projects.
Scientific runs require CUDA in run_development.py. CPU is permitted for unit tests.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable
import torch
from torch import Tensor, nn


def finite(x: Tensor, name: str) -> Tensor:
    if not bool(torch.isfinite(x).all()):
        raise ValueError(f"{name} contains non-finite values")
    return x


def generator(seed: int, device: torch.device | str) -> torch.Generator:
    return torch.Generator(device=device).manual_seed(seed)


def require_gpu() -> torch.device:
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA required: CPU research execution is deliberately disabled.")
    return torch.device("cuda")


def ridge(x: Tensor, y: Tensor, regularization: float) -> Tensor:
    """Mean-square ridge, including the explicit bias coordinate in the penalty."""
    if x.ndim != 2 or y.ndim != 2 or x.shape[0] != y.shape[0]:
        raise ValueError("Expected X[N,D], Y[N,K] with matching N")
    if x.shape[0] == 0 or regularization <= 0:
        raise ValueError("Nonempty data and strictly positive regularization required")
    finite(x, "X"); finite(y, "Y")
    a, b = x.double(), y.double()
    gram = a.T @ a / a.shape[0]
    eye = torch.eye(a.shape[1], device=a.device, dtype=a.dtype)
    return finite(torch.linalg.solve(gram + regularization * eye, a.T @ b / a.shape[0]), "ridge coefficients")


def invariant_ridge(xs: list[Tensor], ys: list[Tensor], regularization: float,
                    invariance: float) -> Tensor:
    """Convex environment-gradient-moment penalty; NOT a causal discovery theorem.

    Minimize mean_e E_e[(Xw-y)^2] + regularization ||w||^2
      + invariance mean_e ||(G_e-Gbar)w-(c_e-cbar)||^2.
    All environments have equal weight, irrespective of row counts.
    """
    if len(xs) != len(ys) or len(xs) < 2 or regularization <= 0 or invariance < 0:
        raise ValueError("Need >=2 paired environments, ridge>0 and invariance>=0")
    dims = {(x.shape[1], y.shape[1]) for x, y in zip(xs, ys) if x.ndim == y.ndim == 2}
    if len(dims) != 1:
        raise ValueError("Environment feature/output dimensions must agree")
    grams, crosses = [], []
    for x, y in zip(xs, ys):
        if x.ndim != 2 or y.ndim != 2 or x.shape[0] == 0 or x.shape[0] != y.shape[0]:
            raise ValueError("Malformed environment")
        a, b = finite(x, "X").double(), finite(y, "Y").double()
        grams.append(a.T @ a / a.shape[0]); crosses.append(a.T @ b / a.shape[0])
    g, c = torch.stack(grams), torch.stack(crosses)
    gm, cm = g.mean(0), c.mean(0)
    dg, dc = g - gm, c - cm
    a = gm + regularization * torch.eye(gm.shape[0], device=gm.device, dtype=gm.dtype)
    a = a + invariance * torch.einsum("eji,ejk->ik", dg, dg) / len(xs)
    b = cm + invariance * torch.einsum("eji,ejk->ik", dg, dc) / len(xs)
    return finite(torch.linalg.solve(a, b), "invariant coefficients")


class FixedReservoir(nn.Module):
    """Contractive tanh reservoir, reset for each independent trajectory."""
    def __init__(self, inputs: int, width: int, seed: int, device: torch.device | str,
                 contraction: float = 0.9):
        super().__init__()
        if inputs < 1 or width < 1 or not 0 < contraction < 1:
            raise ValueError("Invalid dimensions/contraction")
        g = generator(seed, device)
        w = torch.randn(width, width, generator=g, device=device, dtype=torch.float64)
        w = w * (contraction / torch.linalg.matrix_norm(w, ord=2))
        self.register_buffer("w", w)
        self.register_buffer("u", torch.randn(width, inputs, generator=g, device=device,
                                              dtype=torch.float64) / math.sqrt(inputs))

    def forward(self, x: Tensor) -> Tensor:
        if x.ndim != 3 or x.shape[-1] != self.u.shape[-1] or x.shape[1] == 0:
            raise ValueError("Expected X[batch,time,inputs]")
        x = finite(x, "reservoir input").to(self.w)
        h = torch.zeros(x.shape[0], self.w.shape[0], device=x.device, dtype=x.dtype)
        states = []
        for t in range(x.shape[1]):
            h = torch.tanh(h @ self.w.T + x[:, t] @ self.u.T)
            states.append(h)
        ones = torch.ones(*x.shape[:2], 1, device=x.device, dtype=x.dtype)
        return finite(torch.cat((ones, x, torch.stack(states, dim=1)), dim=-1), "features")


def finance_scm(batch: int, steps: int, seed: int, proxy_coefficient: float,
                device: torch.device | str) -> tuple[Tensor, Tensor]:
    """Synthetic lagged SCM, NOT financial-market data.

    X_t=.65 X_(t-1)+eps; Y_(t+1)=.45 Y_t+.8 X_t+.25 eta.
    Observed features at t: noisy X_t, a_e X_t+.1 noise, Y_t, nuisance.
    Intervention changes only the proxy mechanism a_e; latent X is not observed.
    Thus observational identifiability is explicitly NOT assumed.
    """
    if batch < 1 or steps < 2 or not math.isfinite(proxy_coefficient):
        raise ValueError("Invalid SCM parameters")
    g = generator(seed, device)
    noise = torch.randn(batch, steps + 1, 5, generator=g, device=device, dtype=torch.float64)
    x = torch.zeros(batch, device=device, dtype=torch.float64)
    y = torch.zeros_like(x)
    inputs, targets = [], []
    for t in range(steps):
        x = .65 * x + noise[:, t, 0]
        inputs.append(torch.stack((x + .35 * noise[:, t, 1],
                                   proxy_coefficient * x + .1 * noise[:, t, 2],
                                   y, noise[:, t, 3]), dim=-1))
        y = .45 * y + .8 * x + .25 * noise[:, t, 4]
        targets.append(y[:, None])
    return torch.stack(inputs, 1), torch.stack(targets, 1)


def normalized_gate(state: Tensor, alpha: float) -> Tensor:
    """RMS-one, positive gate: conditional expected noise power is unchanged."""
    raw = .2 + torch.sigmoid(alpha * (state.square() - 1.0))
    return raw / raw.square().mean(-1, keepdim=True).sqrt()


@dataclass(frozen=True)
class PhysicalConfig:
    width: int = 32
    dt: float = 0.01
    substeps: int = 4
    coupling: float = 0.2
    sigma: float = 0.05
    alpha: float = 1.0


class PhysicalReservoir(nn.Module):
    """Euler-Maruyama driven double-well lattice with periodic boundaries.

    dh=(h-h^3+kappa Lap(h)+b*u)dt + sigma*g(h)*sqrt(dt)*dW.
    g has RMS one. This is a simulation, not a plasma/turbulence experiment.
    Divergence raises rather than being hidden by state clipping.
    """
    def __init__(self, cfg: PhysicalConfig, seed: int, device: torch.device | str):
        super().__init__()
        if cfg.width < 3 or cfg.dt <= 0 or cfg.substeps < 1 or cfg.sigma < 0 or cfg.coupling < 0:
            raise ValueError("Invalid physical configuration")
        if not all(math.isfinite(v) for v in (cfg.dt, cfg.coupling, cfg.sigma, cfg.alpha)):
            raise ValueError("Physical parameters must be finite")
        self.cfg = cfg
        g = generator(seed, device)
        self.register_buffer("drive", torch.randn(cfg.width, generator=g, device=device,
                                                  dtype=torch.float64) / math.sqrt(cfg.width))

    def forward(self, inputs: Tensor, noise_seed: int) -> tuple[Tensor, dict[str, float]]:
        if inputs.ndim != 3 or inputs.shape[-1] != 1 or inputs.shape[1] == 0:
            raise ValueError("Expected scalar drive[batch,time,1]")
        inputs = finite(inputs, "physical input").to(self.drive)
        cfg = self.cfg
        g = generator(noise_seed, inputs.device)
        h = torch.zeros(inputs.shape[0], cfg.width, device=inputs.device, dtype=inputs.dtype)
        states, energies = [], []
        for t in range(inputs.shape[1]):
            for _ in range(cfg.substeps):
                lap = h.roll(1, -1) + h.roll(-1, -1) - 2 * h
                drift = h - h.pow(3) + cfg.coupling * lap + inputs[:, t] * self.drive
                eps = torch.randn(h.shape, generator=g, device=h.device, dtype=h.dtype)
                kick = cfg.sigma * math.sqrt(cfg.dt) * normalized_gate(h, cfg.alpha) * eps
                h = h + cfg.dt * drift + kick
                energies.append(kick.square().mean())
            finite(h, "physical state")
            if bool((h.abs() > 50).any()):
                raise FloatingPointError("Physical solver diverged; retain this failed run")
            states.append(h)
        ones = torch.ones(*inputs.shape[:2], 1, device=h.device, dtype=h.dtype)
        features = torch.cat((ones, inputs, torch.stack(states, 1)), -1)
        return features, {
            "expected_kick_energy_per_coordinate_substep": cfg.sigma ** 2 * cfg.dt,
            "realized_kick_energy_per_coordinate_substep": torch.stack(energies).mean().item(),
            "integration_substeps": cfg.substeps,
            "dt": cfg.dt,
        }


def delayed_task(batch: int, steps: int, seed: int, device: torch.device | str,
                 input_scale: float = 1.0) -> tuple[Tensor, Tensor]:
    if batch < 1 or steps < 12 or input_scale <= 0:
        raise ValueError("Need positive batch/scale and steps>=12")
    g = generator(seed, device)
    u = input_scale * (2 * torch.rand(batch, steps, 1, generator=g, device=device,
                                    dtype=torch.float64) - 1)
    y = torch.zeros_like(u)
    y[:, 5:] = u[:, 2:-3] * u[:, :-5] + .3 * u[:, 4:-1]
    return u, y


def antithetic_estimate(loss: Callable[[Tensor], Tensor], theta: Tensor, direction: Tensor,
                        epsilon: float, inclusion_probability: float = 1.0) -> Tensor:
    """Two deterministic function evaluations; no backward call or hidden autograd.

    Direction entries are Rademacher signs within the sampled block, zero outside.
    Inverse inclusion correction is needed for uniform block sampling.
    The loss must use identical examples/randomness for the two evaluations.
    """
    if theta.ndim != 1 or theta.shape != direction.shape or epsilon <= 0:
        raise ValueError("Need equal 1D tensors and epsilon>0")
    if not 0 < inclusion_probability <= 1:
        raise ValueError("Invalid inclusion probability")
    finite(theta, "theta"); finite(direction, "direction")
    with torch.no_grad():
        lp = loss(theta + epsilon * direction)
        lm = loss(theta - epsilon * direction)
        if lp.numel() != 1 or lm.numel() != 1:
            raise ValueError("Loss must be scalar")
        result = (lp - lm) / (2 * epsilon * inclusion_probability) * direction
    return finite(result, "zeroth-order estimate")


def block_direction(theta: Tensor, blocks: int, g: torch.Generator) -> tuple[Tensor, float, int]:
    if theta.ndim != 1 or not 1 <= blocks <= theta.numel():
        raise ValueError("Invalid block count")
    block = int(torch.randint(blocks, (1,), generator=g, device=theta.device).item())
    start, end = theta.numel() * block // blocks, theta.numel() * (block + 1) // blocks
    direction = torch.zeros_like(theta)
    direction[start:end] = 2 * torch.randint(2, (end - start,), generator=g,
                                            device=theta.device).to(theta.dtype) - 1
    return direction, 1.0 / blocks, block


def mlp_parameters(inputs: int, width: int, outputs: int) -> int:
    return inputs * width + width + width * outputs + outputs


def flat_mlp(theta: Tensor, x: Tensor, width: int, outputs: int) -> Tensor:
    inputs = x.shape[-1]
    expected = mlp_parameters(inputs, width, outputs)
    if theta.ndim != 1 or theta.numel() != expected:
        raise ValueError("Flat parameter count mismatch")
    p = inputs * width
    w1 = theta[:p].reshape(inputs, width)
    b1 = theta[p:p + width]; p += width
    w2 = theta[p:p + width * outputs].reshape(width, outputs); p += width * outputs
    return torch.tanh(x @ w1 + b1) @ w2 + theta[p:]


class AssociativeMemory(nn.Module):
    """Learned key similarity, explicit value readout and controlled interventions.

    Exact key lookup is an oracle baseline. This model is not claimed to improve it.
    """
    def __init__(self, keys: int, values: int, width: int):
        super().__init__()
        if min(keys, values, width) < 2:
            raise ValueError("Memory dimensions must be >=2")
        self.embedding = nn.Embedding(keys, width)
        self.readout = nn.Linear(values, values)
        self.log_temperature = nn.Parameter(torch.tensor(1.0))
        self.values = values

    def forward(self, keys: Tensor, values: Tensor, query: Tensor,
                keep: Tensor | None = None) -> Tensor:
        if keys.ndim != 2 or keys.shape != values.shape or query.shape != (keys.shape[0],):
            raise ValueError("Expected keys/values[B,M], query[B]")
        if keep is None:
            keep = torch.ones_like(keys, dtype=torch.bool)
        if keep.dtype != torch.bool or keep.shape != keys.shape or not bool(keep.any(-1).all()):
            raise ValueError("Each example needs at least one retained slot")
        k = nn.functional.normalize(self.embedding(keys), dim=-1)
        q = nn.functional.normalize(self.embedding(query), dim=-1)
        logits = (k * q[:, None]).sum(-1) * self.log_temperature.clamp(-4, 4).exp()
        attention = logits.masked_fill(~keep, -torch.inf).softmax(-1)
        v = nn.functional.one_hot(values, self.values).to(k.dtype)
        read = torch.einsum("bm,bmc->bc", attention, v)
        return finite(self.readout(read), "memory logits")


def memory_batch(batch: int, slots: int, keys: int, values: int, seed: int,
                 device: torch.device | str) -> tuple[Tensor, Tensor, Tensor, Tensor, Tensor]:
    if not 2 <= slots <= keys or batch < 1 or values < 2:
        raise ValueError("Invalid memory task dimensions")
    g = generator(seed, device)
    k = torch.rand(batch, keys, generator=g, device=device).argsort(-1)[:, :slots]
    v = torch.randint(values, (batch, slots), generator=g, device=device)
    index = torch.randint(slots, (batch,), generator=g, device=device)
    row = torch.arange(batch, device=device)
    return k, v, k[row, index], v[row, index], index


def memory_interventions(keys: Tensor, values: Tensor, index: Tensor,
                         classes: int) -> dict[str, tuple[Tensor, Tensor]]:
    """Relevant/irrelevant deletion and an in-support value replacement.

    Replacement holds keys/query fixed and changes the queried answer; assess both
    the original label and the replacement label. Deletion alone is not sufficiency.
    """
    if keys.ndim != 2 or keys.shape != values.shape or keys.shape[1] < 2 or classes < 2:
        raise ValueError("Invalid intervention inputs")
    if index.shape != (keys.shape[0],) or bool(((index < 0) | (index >= keys.shape[1])).any()):
        raise ValueError("Invalid queried slot")
    row = torch.arange(keys.shape[0], device=keys.device)
    all_keep = torch.ones_like(keys, dtype=torch.bool)
    relevant, irrelevant = all_keep.clone(), all_keep.clone()
    relevant[row, index] = False
    irrelevant[row, (index + 1) % keys.shape[1]] = False
    swapped = values.clone()
    swapped[row, index] = (swapped[row, index] + 1) % classes
    return {"intact": (values.clone(), all_keep),
            "delete_relevant": (values.clone(), relevant),
            "delete_irrelevant": (values.clone(), irrelevant),
            "replace_relevant_value": (swapped, all_keep.clone())}
