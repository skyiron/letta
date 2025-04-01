from enum import Enum
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from letta.schemas.letta_base import LettaBase


class ManagerType(str, Enum):
    round_robin = "round_robin"
    supervisor = "supervisor"
    dynamic = "dynamic"
    background = "background"
    swarm = "swarm"


class GroupBase(LettaBase):
    __id_prefix__ = "group"


class Group(GroupBase):
    id: str = Field(..., description="The id of the group. Assigned by the database.")
    manager_type: ManagerType = Field(..., description="")
    agent_ids: List[str] = Field(..., description="")
    description: str = Field(..., description="")
    shared_block_ids: List[str] = Field([], description="")
    # Pattern fields
    manager_agent_id: Optional[str] = Field(None, description="")
    termination_token: Optional[str] = Field(None, description="")
    max_turns: Optional[int] = Field(None, description="")
    background_agents_interval: Optional[int] = Field(None, description="")
    turns_counter: Optional[int] = Field(None, description="")
    last_processed_message_id: Optional[str] = Field(None, description="")


class ManagerConfig(BaseModel):
    manager_type: ManagerType = Field(..., description="")


class RoundRobinManager(ManagerConfig):
    manager_type: Literal[ManagerType.round_robin] = Field(ManagerType.round_robin, description="")
    max_turns: Optional[int] = Field(None, description="")


class SupervisorManager(ManagerConfig):
    manager_type: Literal[ManagerType.supervisor] = Field(ManagerType.supervisor, description="")
    manager_agent_id: str = Field(..., description="")


class DynamicManager(ManagerConfig):
    manager_type: Literal[ManagerType.dynamic] = Field(ManagerType.dynamic, description="")
    manager_agent_id: str = Field(..., description="")
    termination_token: Optional[str] = Field("DONE!", description="")
    max_turns: Optional[int] = Field(None, description="")


class BackgroundManager(ManagerConfig):
    manager_type: Literal[ManagerType.background] = Field(ManagerType.background, description="")
    manager_agent_id: str = Field(..., description="")
    background_agents_interval: Optional[int] = Field(None, description="")


# class SwarmGroup(ManagerConfig):
#   manager_type: Literal[ManagerType.swarm] = Field(ManagerType.swarm, description="")


ManagerConfigUnion = Annotated[
    Union[RoundRobinManager, SupervisorManager, DynamicManager, BackgroundManager],
    Field(discriminator="manager_type"),
]


class GroupCreate(BaseModel):
    agent_ids: List[str] = Field(..., description="")
    description: str = Field(..., description="")
    manager_config: ManagerConfigUnion = Field(RoundRobinManager(), description="")
    shared_block_ids: List[str] = Field([], description="")


class GroupUpdate(BaseModel):
    agent_ids: Optional[List[str]] = Field(None, description="")
    description: Optional[str] = Field(None, description="")
    manager_config: Optional[ManagerConfigUnion] = Field(None, description="")
    shared_block_ids: Optional[List[str]] = Field(None, description="")
