from fastapi import APIRouter

from app.domain.contracts import CommandRequest, CommandResponse, EveningSnapshot
from app.domain.policies import allowed_actions
from app.domain.service import apply_command
from app.domain.store import store

router = APIRouter(tags=["evening"])


@router.get("/evening/{evening_id}/snapshot", response_model=EveningSnapshot)
def get_snapshot(evening_id: str, user_id: str) -> EveningSnapshot:
    aggregate = store.get_or_create(evening_id=evening_id, user_id=user_id)
    return EveningSnapshot(
        evening_id=aggregate.evening_id,
        user_id=aggregate.user_id,
        status=aggregate.state,
        context=aggregate.context,
        scroll_block_active=aggregate.scroll_block_active,
        updated_at=aggregate.updated_at,
        allowed_actions=allowed_actions(aggregate.state),
    )


@router.post("/evening/{evening_id}/commands", response_model=CommandResponse)
def post_command(evening_id: str, body: CommandRequest) -> CommandResponse:
    aggregate = store.get_or_create(evening_id=evening_id, user_id=body.user_id)
    response = apply_command(
        aggregate=aggregate,
        command=body.command,
        extension_reason=body.extension_reason,
    )
    store.save(aggregate)
    return response
