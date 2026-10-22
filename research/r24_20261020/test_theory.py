"""Exact finite mathematical fixtures; no task training or efficacy experiment."""
import itertools
import math
import unittest
import torch
import core


class TheoryTests(unittest.TestCase):
    def test_equal_uniform_blocks_do_not_reduce_quadratic_variance(self):
        theta = torch.tensor([.4, -.7, 1.2, -.2], dtype=torch.float64)
        loss = lambda t: .5 * t.square().sum()
        dense = [core.antithetic_estimate(loss, theta, torch.tensor(signs, dtype=theta.dtype), .001)
                 for signs in itertools.product((-1., 1.), repeat=4)]
        blocked = []
        for block in range(2):
            for signs in itertools.product((-1., 1.), repeat=2):
                direction = torch.zeros_like(theta)
                direction[2 * block:2 * block + 2] = torch.tensor(signs, dtype=theta.dtype)
                blocked.append(core.antithetic_estimate(loss, theta, direction, .001, .5))
        dense_variance = (torch.stack(dense) - theta).square().sum(-1).mean()
        block_variance = (torch.stack(blocked) - theta).square().sum(-1).mean()
        expected = 3 * theta.square().sum()
        self.assertTrue(torch.allclose(dense_variance, expected, atol=1e-9))
        self.assertTrue(torch.allclose(block_variance, expected, atol=1e-9))

    def test_oracle_nonuniform_allocation_formula_not_a_free_algorithm(self):
        theta = torch.tensor([2., 1., .1, .2], dtype=torch.float64)
        norms = [theta[:2].norm().item(), theta[2:].norm().item()]
        probabilities = [n / sum(norms) for n in norms]
        second_moment = 0.
        for block, probability in enumerate(probabilities):
            for signs in itertools.product((-1., 1.), repeat=2):
                direction = torch.zeros_like(theta)
                direction[2 * block:2 * block + 2] = torch.tensor(signs, dtype=theta.dtype)
                estimate = core.antithetic_estimate(lambda t: .5 * t.square().sum(),
                                                    theta, direction, .001, probability)
                second_moment += probability / 4 * estimate.square().sum().item()
        expected = sum(math.sqrt(2) * n for n in norms) ** 2
        self.assertAlmostEqual(second_moment, expected, places=8)
        self.assertLess(second_moment, 4 * theta.square().sum().item())

    def test_value_only_substitution_identity(self):
        torch.manual_seed(4)
        model = core.AssociativeMemory(8, 5, 4)
        keys = torch.tensor([[0, 1, 2]])
        query = torch.tensor([1])
        values = torch.tensor([[1, 2, 3]])
        replacement = torch.tensor([[1, 4, 3]])
        k = torch.nn.functional.normalize(model.embedding(keys), dim=-1)
        q = torch.nn.functional.normalize(model.embedding(query), dim=-1)
        attention = ((k * q[:, None]).sum(-1) * model.log_temperature.clamp(-4, 4).exp()).softmax(-1)
        actual = model(keys, replacement, query) - model(keys, values, query)
        expected = attention[:, 1, None] * (model.readout.weight[:, 4] - model.readout.weight[:, 2])[None]
        self.assertTrue(torch.allclose(actual, expected, atol=1e-6))


if __name__ == '__main__':
    unittest.main(verbosity=2)
