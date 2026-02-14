"""
Embedding Analyzer — Feature Probing & Concept Algebra utilities

Pure tensor operations for analyzing and manipulating text encoder embeddings.
Used by Feature Probing (Latent Lab Tab 2) and Concept Algebra (Latent Lab Tab 3).
"""

import logging
import torch
from torch import Tensor

logger = logging.getLogger(__name__)


def compute_dimension_differences(embed_a: Tensor, embed_b: Tensor) -> dict:
    """Per-dimension absolute difference, averaged across token positions.

    Returns ALL dimensions sorted by magnitude (no arbitrary top-k cutoff).
    The frontend uses diff_per_dim for threshold-based selection and
    top_dims/top_values for the sorted bar chart display.

    Args:
        embed_a: [1, seq_len, embed_dim] embedding from prompt A
        embed_b: [1, seq_len, embed_dim] embedding from prompt B

    Returns:
        dict with:
        - diff_per_dim: list of floats [embed_dim], absolute difference per dimension
        - top_dims: list of ints, ALL dimension indices sorted by difference magnitude
        - top_values: list of floats, difference values sorted by magnitude
        - embed_dim: int, total number of dimensions
        - total_l2: float, total L2 distance between embeddings
        - nonzero_dims: int, number of dimensions with nonzero difference
    """
    # Average absolute difference across token positions
    diff = (embed_b - embed_a).abs().mean(dim=1).squeeze(0)  # [embed_dim]

    # Total L2 distance for context
    total_l2 = (embed_b - embed_a).norm(p=2).item()
    nonzero = (diff > 1e-6).sum().item()

    # Sort ALL dimensions by magnitude — no arbitrary cutoff
    top = torch.topk(diff, k=diff.shape[0])

    logger.info(
        f"[EMBEDDING-DIFF] embed_dim={diff.shape[0]}, total_L2={total_l2:.4f}, "
        f"nonzero_dims={nonzero}/{diff.shape[0]}, "
        f"top1={top.values[0].item():.4f}, top10_sum={top.values[:10].sum().item():.4f}, "
        f"top50_sum={top.values[:50].sum().item():.4f}, top200_sum={top.values[:min(200, diff.shape[0])].sum().item():.4f}"
    )

    return {
        'diff_per_dim': diff.cpu().tolist(),
        'top_dims': top.indices.cpu().tolist(),
        'top_values': top.values.cpu().tolist(),
        'embed_dim': diff.shape[0],
        'total_l2': total_l2,
        'nonzero_dims': int(nonzero),
    }


def apply_dimension_transfer(embed_a: Tensor, embed_b: Tensor, dims: list) -> Tensor:
    """Copy specific dimensions from embed_b into embed_a.

    Args:
        embed_a: [1, seq_len, embed_dim] base embedding
        embed_b: [1, seq_len, embed_dim] source embedding
        dims: list of dimension indices to transfer

    Returns:
        Modified embedding tensor (clone of embed_a with selected dims from embed_b)
    """
    result = embed_a.clone()
    result[:, :, dims] = embed_b[:, :, dims]

    # Diagnostic: how much did we actually change?
    change_l2 = (result - embed_a).norm(p=2).item()
    total_diff_l2 = (embed_b - embed_a).norm(p=2).item()
    pct = (change_l2 / total_diff_l2 * 100) if total_diff_l2 > 0 else 0

    logger.info(
        f"[DIMENSION-TRANSFER] {len(dims)} dims transferred, "
        f"change_L2={change_l2:.4f}, total_diff_L2={total_diff_l2:.4f}, "
        f"captured={pct:.1f}% of total difference"
    )

    return result


def apply_concept_algebra(
    embed_a: Tensor,
    embed_b: Tensor,
    embed_c: Tensor,
    scale_sub: float = 1.0,
    scale_add: float = 1.0,
) -> tuple[Tensor, float]:
    """Concept Algebra: result = A - scale_sub * B + scale_add * C

    Mikolov analogy: embed("King") - embed("Man") + embed("Woman") ≈ embed("Queen")
    Applied to text encoder embeddings for image generation.

    Args:
        embed_a: [1, seq_len, embed_dim] base embedding
        embed_b: [1, seq_len, embed_dim] embedding to subtract
        embed_c: [1, seq_len, embed_dim] embedding to add
        scale_sub: scaling factor for subtraction (default 1.0)
        scale_add: scaling factor for addition (default 1.0)

    Returns:
        (result_embedding, l2_distance_from_a)
    """
    result = embed_a - scale_sub * embed_b + scale_add * embed_c
    l2_dist = (result - embed_a).norm(p=2).item()

    logger.info(
        f"[CONCEPT-ALGEBRA] A - {scale_sub}*B + {scale_add}*C, "
        f"L2(result, A)={l2_dist:.4f}, shapes: A={embed_a.shape}, B={embed_b.shape}, C={embed_c.shape}"
    )

    return result, l2_dist
