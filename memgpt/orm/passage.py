from typing import Optional, TYPE_CHECKING, List
from datetime import datetime
from sqlalchemy import JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from memgpt.models.pydantic_models import EmbeddingConfigModel
from memgpt.orm.sqlalchemy_base import SqlalchemyBase
from memgpt.orm.mixins import DocumentMixin

if TYPE_CHECKING:
    from memgpt.orm.document import Document

class Passage(DocumentMixin, SqlalchemyBase):
    """A segment of text from a document.
    """
    __tablename__ = "passage"

    text: Mapped[str] = mapped_column(doc="The text of the passage.")
    embedding: Optional[List[float]] = mapped_column(JSON, doc="The embedding of the passage.", nullable=True)
    embedding_config: Optional["EmbeddingConfigModel"] = mapped_column(JSON, doc="The embedding configuration used by the passage.",
    nullable=True)
    data_source: Optional[str] = mapped_column(nullable=True, doc="Human readable description of where the passage came from.")
    metadata_: Optional[dict] = mapped_column(JSON, default_factory=lambda: {}, doc="additional information about the passage.")


    # relationships
    document: Mapped["Document"] = relationship("Document", back_populates="passages")