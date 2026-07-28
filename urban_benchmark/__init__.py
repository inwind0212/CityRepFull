__version__ = "1.0.0"

from .align import align_embedding
from .embeddings import EmbeddingSource
from .evaluation import evaluate
from .tasks import Task, load_task

__all__ = [
    "__version__",
    "EmbeddingSource",
    "Task",
    "align_embedding",
    "evaluate",
    "load_task",
]
