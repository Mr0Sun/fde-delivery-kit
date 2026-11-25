from pydantic import BaseModel, ConfigDict, Field, field_validator

class Item(BaseModel):
    name: str
    description: str | None = Field(
        default=None, title="The description of the item", max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than zero")
    tax: float | None = None

    @field_validator("name")
    def validate_name(cls, v: str) -> str:
        if not v.startswith("fde"):
            raise ValueError("Name must start with 'fde'")
        return v

# 检索请求 SearchQuery
class SearchQuery(BaseModel):
    q: str = Field(description="Query string", min_length=1)
    short: bool = Field(description="Short query", default=False)

    # 生成注释，提示用户查询字符串不能为空
    @field_validator("q")
    def validate_q(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError("Query string cannot be empty")
        return v

# 文档元数据 DocMeta
class DocMeta(BaseModel):
    title: str = Field(description="The title of the document", max_length=100)
    version: str = Field(description="The version of the document", max_length=10)
    service: str = Field(description="The service of the document", max_length=100)

    #校验文档元数据
    @field_validator("title")
    def validate_title(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError("Title cannot be empty")
        return v
    @field_validator("version")
    def validate_version(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError("Version cannot be empty")
        return v
    @field_validator("service")
    def validate_service(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError("Service cannot be empty")
        return v

class HealthResponse(BaseModel):
    # 允许依赖动态注入的额外字段原样返回，无需预先声明
    model_config = ConfigDict(extra="allow")

    status: str
    version: str
    service: str

class Echo(BaseModel):
    word: str
    limit: int = Field(description="The limit of the echo", default=1)

    @field_validator("word")
    def validate_word(cls, v: str) -> str:
        if len(v.strip()) == 0:
            raise ValueError("Word cannot be empty")
        return v