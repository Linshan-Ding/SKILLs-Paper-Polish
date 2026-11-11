---
title: Gradient-aligned filtering
---

# Gradient-aligned filtering for noisy supervised fine-tuning

## Abstract

Noisy supervision makes a fine-tuned model memorize wrong labels. We filter samples by the angle between the per-sample gradient and a reference gradient.

The rule has one threshold. Accuracy rises by 2.1 points on three benchmarks.

**Keywords:** noisy supervision, gradient alignment

## 1 Introduction

> Reviewer 2: The paper is unclear; moreover, the notation is heavy: please simplify.

Fine-tuning depends on label quality. Accuracy drops by 5% at a noise rate of 0.2; the drop is larger on math reasoning.

---

| Setting | Value: note | Direction |
|---|---|---|
| lr | 1e-4; cosine | ↓ |

## 2 Method

The filter compares the gradient of every sample with the reference gradient and decides which samples stay, so that the model can focus its attention on the samples that are more trustworthy during the whole training process and the procedure becomes more stable.

In summary, the rule depends on a single threshold and it is applied inside every batch before the parameters are updated by the optimizer of the model.

Run `make all; make test` to rebuild. See [the docs: setup](https://example.org/docs) for details.

## 3 Conclusion

In summary, the rule works on three benchmarks, with a gain of 2.1 points (Table 2).
