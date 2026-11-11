---
title: Gradient-aligned filtering
---

# Gradient-aligned filtering for noisy supervised fine-tuning

## Abstract

Noisy supervision makes a fine-tuned model memorize wrong labels. We filter samples by the angle between the per-sample gradient and a reference gradient, and the rule has one threshold. At a noise rate of 0.2, accuracy rises by 2.1 points on three benchmarks (Table 2).

**Keywords:** noisy supervision, gradient alignment

## 1 Introduction

> Reviewer 2: The paper is unclear; moreover, the notation is heavy: please simplify.

Fine-tuning depends on label quality. Accuracy drops by 5% at a noise rate of 0.2. The drop is larger on math reasoning.

---

| Setting | Value: note | Direction |
|---|---|---|
| lr | 1e-4; cosine | lower is better |

## 2 Method

The filter compares the gradient of every sample with the reference gradient. A sample whose cosine falls below the threshold $\tau$ is left out of the update. The reference gradient comes from 64 verified samples and is recomputed every 50 steps.

Run `make all; make test` to rebuild. See [the setup notes](https://example.org/docs) for details.

The original reads 2.1 points at a noise rate of 0.2; we quote it unchanged. <!-- style-exempt -->

## 3 Conclusion

In summary, the rule works on three benchmarks, with a gain of 2.1 points (Table 2).
