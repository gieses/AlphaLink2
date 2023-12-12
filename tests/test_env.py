""""Quick testing of AlphaLink env."""
import torch


def test_import_alphalink():
    imported_alphalink = False
    try:
        import alphalink
        imported_alphalink = True
    except ImportError:
        pass
    assert imported_alphalink


def test_import_alphafold():
    imported_alphalink = False
    try:
        import alphafold
        imported_alphalink = True
    except ImportError:
        pass
    assert imported_alphalink


def test_pytorch_gpu():
    has_gpu = torch.cuda.is_available()
    assert has_gpu
