"""Engineering tests only: tiny hand-checkable fixtures are not research results."""
import itertools
import math
import unittest
from unittest.mock import patch
import torch
import core


class NumericalTests(unittest.TestCase):
    def setUp(self):
        torch.manual_seed(7)
        torch.set_num_threads(1)

    def test_ridge_closed_form(self):
        x = torch.eye(2, dtype=torch.float64)
        y = torch.tensor([[2.0], [4.0]], dtype=torch.float64)
        self.assertTrue(torch.allclose(core.ridge(x, y, .5), y / 2))

    def test_ridge_rejects_nonfinite(self):
        with self.assertRaises(ValueError):
            core.ridge(torch.tensor([[float('nan')]]), torch.ones(1, 1), .1)

    def test_ridge_rejects_empty(self):
        with self.assertRaises(ValueError):
            core.ridge(torch.empty(0, 2), torch.empty(0, 1), .1)

    def test_invariance_zero_matches_equal_environment_ridge(self):
        x = [torch.randn(5, 3, dtype=torch.float64) for _ in range(3)]
        y = [torch.randn(5, 1, dtype=torch.float64) for _ in range(3)]
        actual = core.invariant_ridge(x, y, .03, 0)
        expected = core.ridge(torch.cat(x), torch.cat(y), .03)
        self.assertTrue(torch.allclose(actual, expected, atol=1e-10))

    def test_invariant_solution_has_zero_objective_gradient(self):
        xs = [torch.randn(6, 3, dtype=torch.float64), torch.randn(9, 3, dtype=torch.float64)]
        ys = [torch.randn(6, 1, dtype=torch.float64), torch.randn(9, 1, dtype=torch.float64)]
        w = core.invariant_ridge(xs, ys, .2, 3).requires_grad_()
        moments = torch.stack([x.T @ (x @ w - y) / len(x) for x, y in zip(xs, ys)])
        objective = sum((x @ w - y).square().mean() for x, y in zip(xs, ys)) / 2
        objective = objective + .2 * w.square().sum() + 3 * (moments - moments.mean(0)).square().sum() / 2
        objective.backward()
        self.assertLess(w.grad.abs().max().item(), 1e-9)

    def test_reservoir_is_contractive(self):
        m = core.FixedReservoir(2, 5, 7, 'cpu')
        self.assertAlmostEqual(torch.linalg.matrix_norm(m.w, 2).item(), .9, places=10)

    def test_reservoir_reset_and_prefix_causality(self):
        m = core.FixedReservoir(2, 5, 7, 'cpu')
        x = torch.randn(2, 8, 2, dtype=torch.float64)
        f = m(x)
        changed = x.clone(); changed[:, 4:] += 100
        self.assertTrue(torch.equal(f[:, :4], m(changed)[:, :4]))
        self.assertTrue(torch.equal(f, m(x)))
        self.assertEqual(f.shape, (2, 8, 8))

    def test_scm_proxy_intervention_preserves_target(self):
        a, ya = core.finance_scm(2, 8, 5, 1, 'cpu')
        b, yb = core.finance_scm(2, 8, 5, -1, 'cpu')
        self.assertTrue(torch.equal(ya, yb))
        self.assertTrue(torch.equal(a[:, :, [0, 2, 3]], b[:, :, [0, 2, 3]]))
        self.assertFalse(torch.equal(a[:, :, 1], b[:, :, 1]))

    def test_split_seeds_are_distinct(self):
        a, _ = core.finance_scm(2, 8, 5, 1, 'cpu')
        b, _ = core.finance_scm(2, 8, 6, 1, 'cpu')
        self.assertFalse(torch.equal(a, b))

    def test_gate_power_identity(self):
        h = torch.tensor([[0., 1., 2.], [-2., .2, .5]], dtype=torch.float64)
        for alpha in (-20., 0., 20.):
            g = core.normalized_gate(h, alpha)
            self.assertTrue(torch.allclose(g.square().mean(-1), torch.ones(2, dtype=h.dtype)))
            self.assertTrue(bool((g > 0).all()))
        self.assertTrue(torch.equal(core.normalized_gate(h, 0), torch.ones_like(h)))

    def test_physical_zero_noise_is_seed_independent(self):
        m = core.PhysicalReservoir(core.PhysicalConfig(width=4, substeps=1, sigma=0), 3, 'cpu')
        x = torch.ones(2, 4, 1, dtype=torch.float64) * .1
        a, ea = m(x, 1); b, eb = m(x, 2)
        self.assertTrue(torch.equal(a, b))
        self.assertEqual(ea['realized_kick_energy_per_coordinate_substep'], 0)
        self.assertEqual(eb['expected_kick_energy_per_coordinate_substep'], 0)

    def test_physical_noise_reproducible(self):
        m = core.PhysicalReservoir(core.PhysicalConfig(width=4, substeps=1), 3, 'cpu')
        x = torch.zeros(2, 4, 1, dtype=torch.float64)
        a, _ = m(x, 6); b, _ = m(x, 6)
        self.assertTrue(torch.equal(a, b))

    def test_delay_alignment(self):
        u, y = core.delayed_task(2, 14, 7, 'cpu')
        self.assertTrue(torch.equal(y[:, :5], torch.zeros_like(y[:, :5])))
        self.assertTrue(torch.allclose(y[:, 10], u[:, 7] * u[:, 5] + .3 * u[:, 9]))

    def test_antithetic_quadratic_unbiased_exact_enumeration(self):
        theta = torch.tensor([.4, -.7], dtype=torch.float64)
        matrix = torch.tensor([[2., .2], [.2, 3.]], dtype=torch.float64)
        def loss(v):
            return .5 * v @ matrix @ v
        estimates = [core.antithetic_estimate(loss, theta, torch.tensor(s, dtype=theta.dtype), .001)
                     for s in itertools.product((-1., 1.), repeat=2)]
        self.assertTrue(torch.allclose(torch.stack(estimates).mean(0), matrix @ theta, atol=1e-10))

    def test_block_inverse_probability_correction(self):
        theta = torch.tensor([.4, -.7], dtype=torch.float64)
        estimates = []
        for index in range(2):
            for sign in (-1., 1.):
                d = torch.zeros_like(theta); d[index] = sign
                estimates.append(core.antithetic_estimate(lambda v: v.square().sum() / 2,
                                                         theta, d, .001, .5))
        self.assertTrue(torch.allclose(torch.stack(estimates).mean(0), theta, atol=1e-10))

    def test_zo_does_not_mutate_or_build_autograd(self):
        theta = torch.tensor([1., 2.], requires_grad=True)
        before = theta.detach().clone()
        g = core.antithetic_estimate(lambda v: v.square().sum(), theta, torch.ones_like(theta), .01)
        self.assertTrue(torch.equal(theta.detach(), before))
        self.assertFalse(g.requires_grad)
        self.assertIsNone(theta.grad)

    def test_block_support_and_probability(self):
        theta = torch.zeros(11)
        d, p, block = core.block_direction(theta, 3, core.generator(2, 'cpu'))
        start, end = 11 * block // 3, 11 * (block + 1) // 3
        self.assertEqual(p, 1 / 3)
        self.assertEqual(torch.count_nonzero(d).item(), end - start)
        self.assertTrue(bool((d[:start] == 0).all() and (d[end:] == 0).all()))

    def test_flat_mlp_dimensions_and_gradients(self):
        t = torch.randn(core.mlp_parameters(3, 4, 2), dtype=torch.float64, requires_grad=True)
        y = core.flat_mlp(t, torch.randn(5, 3, dtype=torch.float64), 4, 2)
        self.assertEqual(y.shape, (5, 2))
        y.square().mean().backward()
        self.assertTrue(bool(torch.isfinite(t.grad).all()))

    def test_memory_labels_and_unique_keys(self):
        k, v, q, y, i = core.memory_batch(3, 4, 8, 5, 7, 'cpu')
        row = torch.arange(3)
        self.assertTrue(torch.equal(q, k[row, i]))
        self.assertTrue(torch.equal(y, v[row, i]))
        self.assertTrue(all(len(torch.unique(r)) == 4 for r in k))

    def test_memory_interventions_are_local_and_nonmutating(self):
        k, v, q, y, i = core.memory_batch(3, 4, 8, 5, 7, 'cpu')
        before = v.clone()
        variants = core.memory_interventions(k, v, i, 5)
        row = torch.arange(3)
        self.assertTrue(torch.equal(v, before))
        self.assertTrue(bool((variants['delete_relevant'][1].sum(-1) == 3).all()))
        self.assertTrue(bool((variants['delete_irrelevant'][1].sum(-1) == 3).all()))
        self.assertTrue(bool((~variants['delete_relevant'][1][row, i]).all()))
        self.assertTrue(bool(variants['delete_irrelevant'][1][row, i].all()))
        self.assertTrue(bool(((variants['replace_relevant_value'][0] != v).sum(-1) == 1).all()))

    def test_memory_mask_removes_value_influence(self):
        m = core.AssociativeMemory(8, 5, 4)
        k, v, q, y, i = core.memory_batch(3, 4, 8, 5, 7, 'cpu')
        keep = torch.ones_like(k, dtype=torch.bool); keep[:, 1] = False
        changed = v.clone(); changed[:, 1] = (changed[:, 1] + 1) % 5
        self.assertTrue(torch.equal(m(k, v, q, keep), m(k, changed, q, keep)))

    def test_memory_gradient_and_empty_mask_guard(self):
        m = core.AssociativeMemory(8, 5, 4)
        k, v, q, y, i = core.memory_batch(3, 4, 8, 5, 7, 'cpu')
        torch.nn.functional.cross_entropy(m(k, v, q), y).backward()
        self.assertTrue(all(p.grad is not None and bool(torch.isfinite(p.grad).all()) for p in m.parameters()))
        with self.assertRaises(ValueError):
            m(k, v, q, torch.zeros_like(k, dtype=torch.bool))

    def test_gpu_guard_has_no_cpu_fallback(self):
        with patch('torch.cuda.is_available', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'CPU research execution'):
                core.require_gpu()


if __name__ == '__main__':
    unittest.main(verbosity=2)
