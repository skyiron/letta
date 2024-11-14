from typing import List, Optional

from letta.orm.errors import NoResultFound
from letta.orm.sandbox_config import SandboxConfig as SandboxConfigModel
from letta.orm.sandbox_config import SandboxEnvironmentVariable as SandboxEnvVarModel
from letta.schemas.sandbox_config import SandboxConfig as PydanticSandboxConfig
from letta.schemas.sandbox_config import SandboxConfigUpdate
from letta.schemas.sandbox_config import SandboxEnvironmentVariable as PydanticEnvVar
from letta.schemas.sandbox_config import SandboxEnvVarUpdate, SandboxType
from letta.schemas.user import User as PydanticUser
from letta.utils import enforce_types, printd


class SandboxConfigManager:
    """Manager class to handle business logic related to SandboxConfig and SandboxEnvironmentVariable."""

    def __init__(self):
        from letta.server.server import db_context

        self.session_maker = db_context

    @enforce_types
    def create_or_update_sandbox_config(self, sandbox_config: PydanticSandboxConfig, actor: PydanticUser) -> PydanticSandboxConfig:
        """Create or update a sandbox configuration based on the PydanticSandboxConfig schema."""

        # Attempt to retrieve the existing sandbox configuration by type within the organization
        db_sandbox = self.get_sandbox_config_by_type(sandbox_config.type, actor=actor)
        if db_sandbox:
            # Prepare the update data, excluding fields that should not be reset
            update_data = sandbox_config.model_dump(exclude_unset=True, exclude_none=True)
            update_data = {key: value for key, value in update_data.items() if getattr(db_sandbox, key) != value}

            # If there are changes, update the sandbox configuration
            if update_data:
                db_sandbox = self.update_sandbox_config(db_sandbox.id, SandboxConfigUpdate(**update_data), actor)
            else:
                printd(
                    f"`create_or_update_sandbox_config` was called with user_id={actor.id}, organization_id={actor.organization_id}, "
                    f"type={sandbox_config.type}, but found existing configuration with nothing to update."
                )

            return db_sandbox
        else:
            # If the sandbox configuration doesn't exist, create a new one
            with self.session_maker() as session:
                sandbox_config.organization_id = actor.organization_id
                db_sandbox = SandboxConfigModel(**sandbox_config.model_dump(exclude_none=True))
                db_sandbox.create(session, actor=actor)
                return db_sandbox.to_pydantic()

    @enforce_types
    def update_sandbox_config(self, sandbox_id: str, sandbox_update: SandboxConfigUpdate, actor: PydanticUser) -> PydanticSandboxConfig:
        """Update an existing sandbox configuration."""
        with self.session_maker() as session:
            sandbox = SandboxConfigModel.read(db_session=session, identifier=sandbox_id, actor=actor)
            update_data = sandbox_update.model_dump(exclude_unset=True, exclude_none=True)
            update_data = {key: value for key, value in update_data.items() if getattr(sandbox, key) != value}

            if update_data:
                for key, value in update_data.items():
                    setattr(sandbox, key, value)
                sandbox.update(db_session=session, actor=actor)
            else:
                printd(
                    f"`update_sandbox_config` called with user_id={actor.id}, organization_id={actor.organization_id}, "
                    f"name={sandbox.type}, but nothing to update."
                )
            return sandbox.to_pydantic()

    @enforce_types
    def delete_sandbox_config(self, sandbox_id: str, actor: PydanticUser) -> PydanticSandboxConfig:
        """Delete a sandbox configuration by its ID."""
        with self.session_maker() as session:
            sandbox = SandboxConfigModel.read(db_session=session, identifier=sandbox_id, actor=actor)
            sandbox.hard_delete(db_session=session, actor=actor)
            return sandbox.to_pydantic()

    @enforce_types
    def list_sandbox_configs(
        self, actor: PydanticUser, cursor: Optional[str] = None, limit: Optional[int] = 50
    ) -> List[PydanticSandboxConfig]:
        """List all sandbox configurations with optional pagination."""
        with self.session_maker() as session:
            sandboxes = SandboxConfigModel.list(
                db_session=session,
                cursor=cursor,
                limit=limit,
                organization_id=actor.organization_id,
            )
            return [sandbox.to_pydantic() for sandbox in sandboxes]

    @enforce_types
    def get_sandbox_config_by_id(self, sandbox_id: str, actor: Optional[PydanticUser] = None) -> Optional[PydanticSandboxConfig]:
        """Retrieve a sandbox configuration by its ID."""
        with self.session_maker() as session:
            try:
                sandbox = SandboxConfigModel.read(db_session=session, identifier=sandbox_id, actor=actor)
                return sandbox.to_pydantic()
            except NoResultFound:
                return None

    @enforce_types
    def get_sandbox_config_by_type(self, type: SandboxType, actor: Optional[PydanticUser] = None) -> Optional[PydanticSandboxConfig]:
        """Retrieve a sandbox config by its type."""
        with self.session_maker() as session:
            try:
                sandboxes = SandboxConfigModel.list(
                    db_session=session,
                    type=type,
                    organization_id=actor.organization_id,
                    limit=1,
                )
                if sandboxes:
                    return sandboxes[0].to_pydantic()
                return None
            except NoResultFound:
                return None

    @enforce_types
    def create_sandbox_env_var(self, env_var: PydanticEnvVar, actor: PydanticUser) -> PydanticEnvVar:
        """Create a new sandbox environment variable."""
        db_env_var = self.get_sandbox_env_var_by_key(env_var.key, actor=actor)
        if db_env_var:
            update_data = env_var.model_dump(exclude_unset=True, exclude_none=True)
            update_data = {key: value for key, value in update_data.items() if getattr(db_env_var, key) != value}
            # If there are changes, update the environment variable
            if update_data:
                db_env_var = self.update_sandbox_env_var(db_env_var.id, SandboxEnvVarUpdate(**update_data), actor)
            else:
                printd(
                    f"`create_or_update_sandbox_env_var` was called with user_id={actor.id}, organization_id={actor.organization_id}, "
                    f"key={env_var.key}, but found existing variable with nothing to update."
                )

            return db_env_var
        else:
            with self.session_maker() as session:
                env_var.organization_id = actor.organization_id
                env_var = SandboxEnvVarModel(**env_var.model_dump(exclude_none=True))
                env_var.create(session, actor=actor)
            return env_var.to_pydantic()

    @enforce_types
    def update_sandbox_env_var(self, env_var_id: str, env_var_update: SandboxEnvVarUpdate, actor: PydanticUser) -> PydanticEnvVar:
        """Update an existing sandbox environment variable."""
        with self.session_maker() as session:
            env_var = SandboxEnvVarModel.read(db_session=session, identifier=env_var_id, actor=actor)
            update_data = env_var_update.model_dump(exclude_unset=True, exclude_none=True)
            update_data = {key: value for key, value in update_data.items() if getattr(env_var, key) != value}

            if update_data:
                for key, value in update_data.items():
                    setattr(env_var, key, value)
                env_var.update(db_session=session, actor=actor)
            else:
                printd(
                    f"`update_sandbox_env_var` called with user_id={actor.id}, organization_id={actor.organization_id}, "
                    f"key={env_var.key}, but nothing to update."
                )
            return env_var.to_pydantic()

    @enforce_types
    def delete_sandbox_env_var(self, env_var_id: str, actor: PydanticUser) -> PydanticEnvVar:
        """Delete a sandbox environment variable by its ID."""
        with self.session_maker() as session:
            env_var = SandboxEnvVarModel.read(db_session=session, identifier=env_var_id, actor=actor)
            env_var.hard_delete(db_session=session, actor=actor)
            return env_var.to_pydantic()

    @enforce_types
    def list_sandbox_env_vars(self, actor: PydanticUser, cursor: Optional[str] = None, limit: Optional[int] = 50) -> List[PydanticEnvVar]:
        """List all sandbox environment variables with optional pagination."""
        with self.session_maker() as session:
            env_vars = SandboxEnvVarModel.list(
                db_session=session,
                cursor=cursor,
                limit=limit,
                organization_id=actor.organization_id,
            )
            return [env_var.to_pydantic() for env_var in env_vars]

    @enforce_types
    def get_sandbox_env_var_by_key(self, key: str, actor: Optional[PydanticUser] = None) -> Optional[PydanticEnvVar]:
        """Retrieve a sandbox environment variable by its key."""
        with self.session_maker() as session:
            try:
                env_var = SandboxEnvVarModel.list(
                    db_session=session,
                    key=key,
                    organization_id=actor.organization_id,
                    limit=1,
                )
                if env_var:
                    return env_var[0].to_pydantic()
                return None
            except NoResultFound:
                return None
