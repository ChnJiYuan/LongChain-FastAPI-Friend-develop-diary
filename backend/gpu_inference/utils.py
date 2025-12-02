"""GPU helper utilities."""


def current_device():
    try:
        import torch

        if torch.cuda.is_available():
            return torch.device("cuda")
        if torch.backends.mps.is_available():  # type: ignore[attr-defined]
            return torch.device("mps")
        return torch.device("cpu")
    except Exception:
        return "cpu"
