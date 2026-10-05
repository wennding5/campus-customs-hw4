from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2_000)


class PageContext(BaseModel):
    path: str = Field(default="/", max_length=300)
    product_id: str | None = Field(default=None, max_length=160, pattern=r"^[a-z0-9][a-z0-9-]*$")
    product_name: str | None = Field(default=None, max_length=300)

    @field_validator("path")
    @classmethod
    def valid_site_path(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.startswith("/") or cleaned.startswith("//"):
            raise ValueError("Page path must be a local site route")
        return cleaned


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2_000)
    history: list[ChatHistoryMessage] = Field(default_factory=list, max_length=12)
    page_context: PageContext | None = None

    @field_validator("message")
    @classmethod
    def nonempty_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Message cannot be blank")
        return cleaned


class AgentProductMatch(BaseModel):
    product_id: str
    reason: str = Field(description="A brief explanation of why this product fits the request")


class AgentReply(BaseModel):
    reply: str = Field(description="The concise, customer-facing response")
    products: list[AgentProductMatch] = Field(
        default_factory=list,
        max_length=4,
        description="IDs of products actually returned by catalogue tools and mentioned in the reply",
    )
    needs_clarification: bool = False
    follow_up_question: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def valid_clarification(self) -> "AgentReply":
        if self.needs_clarification and not self.follow_up_question:
            raise ValueError("A clarification response must include a follow-up question")
        if self.needs_clarification and self.products:
            raise ValueError("Do not recommend products before clarifying an unclear request")
        return self


class SizeStock(BaseModel):
    size: str
    quantity: int = Field(ge=0)
    in_stock: bool


class CatalogueMatch(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    image_url: str
    stock_by_size: list[SizeStock]
    total_stock: int


class ChatProductMatch(CatalogueMatch):
    reason: str


class ChatResponse(BaseModel):
    reply: str
    products: list[ChatProductMatch] = Field(default_factory=list, max_length=4)
    needs_clarification: bool = False
    follow_up_question: str | None = None


class StoredChatMessage(ChatHistoryMessage):
    id: int
    products: list[ChatProductMatch] = Field(default_factory=list)
    created_at: str


class ChatHistoryResponse(BaseModel):
    messages: list[StoredChatMessage]


class AgentDependencies(BaseModel):
    customer_id: int | None = None
    customer_name: str | None = None
    customer_email: str | None = None
    page_context: PageContext | None = None

    @property
    def is_authenticated(self) -> bool:
        return self.customer_id is not None


class StockLookup(BaseModel):
    product_id: str
    name: str
    requested_size: str | None = None
    stock_by_size: list[SizeStock]
    total_stock: int
    availability_message: str


class AuditEvent(BaseModel):
    time: datetime
    tool_name: str = Field(min_length=1, max_length=80)
    args: dict[str, str | int | bool | None] = Field(default_factory=dict)
    result: str = Field(max_length=500)
    stop_reason: str | None = Field(default=None, max_length=120)
