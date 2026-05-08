from typing import List

from fastapi import APIRouter, Query

from app.application.dto.application import (
    ApplicationCreateDTO,
    ApplicationUpdateDTO,
)
from app.application.use_cases.applications.create_application import (
    CreateApplicationUseCase,
)
from app.application.use_cases.applications.list_applications import (
    ListApplicationsUseCase,
)
from app.application.use_cases.applications.update_application import (
    UpdateApplicationUseCase,
)
from app.application.use_cases.companies.list_companies import (
    ListCompaniesUseCase,
)
from app.application.use_cases.get_supports import GetSupportsUseCase
from app.lib.types import SnowflakeID
from app.presentation.dependencies import (
    ApplicationRepositoryDp,
    CompanyRepositoryDp,
    CurrentApiKeyUserDp,
    FeedbackDefinitionRepositoryDp,
    PlatformRepositoryDp,
    StepDefinitionRepositoryDp,
)
from app.presentation.schemas import DetailSchema
from app.presentation.schemas.application import (
    Application,
    CreateApplication,
    UpdateApplication,
)
from app.presentation.schemas.company import Company
from app.presentation.schemas.support import SupportSchema

router = APIRouter(
    prefix='/mcp',
    tags=['MCP'],
    responses={'403': {'model': DetailSchema}},
)


@router.get('/applications', response_model=List[Application])
async def list_mcp_applications(
    c_user: CurrentApiKeyUserDp,
    app_repo: ApplicationRepositoryDp,
    cycle_id: SnowflakeID | None = None,
):
    """List applications through the API-key-authenticated MCP surface."""
    use_case = ListApplicationsUseCase(app_repo)
    applications = await use_case.execute(
        c_user.id,
        cycle_id=int(cycle_id) if cycle_id else None,
    )
    return applications


@router.post(
    '/applications',
    response_model=Application,
    status_code=201,
    responses={'404': {'model': DetailSchema}},
)
async def create_mcp_application(
    payload: CreateApplication,
    c_user: CurrentApiKeyUserDp,
    app_repo: ApplicationRepositoryDp,
    platform_repo: PlatformRepositoryDp,
    company_repo: CompanyRepositoryDp,
):
    """Create an application through the API-key-authenticated MCP surface."""
    use_case = CreateApplicationUseCase(app_repo, platform_repo, company_repo)
    company = (
        payload.company
        if isinstance(payload.company, int)
        else payload.company.model_dump()
    )
    data = ApplicationCreateDTO(
        **payload.model_dump(exclude={'company'}),
        company=company,
        user_id=c_user.id,
    )
    application = await use_case.execute(data)
    return Application.model_validate(application)


@router.put(
    '/applications/{application_id}',
    response_model=Application,
    responses={'404': {'model': DetailSchema}},
)
async def update_mcp_application(
    application_id: SnowflakeID,
    payload: UpdateApplication,
    c_user: CurrentApiKeyUserDp,
    app_repo: ApplicationRepositoryDp,
    platform_repo: PlatformRepositoryDp,
    company_repo: CompanyRepositoryDp,
):
    """Update an application through the API-key-authenticated MCP surface."""
    use_case = UpdateApplicationUseCase(app_repo, platform_repo, company_repo)
    company = (
        payload.company
        if isinstance(payload.company, int)
        else payload.company.model_dump()
    )
    data = ApplicationUpdateDTO(
        **payload.model_dump(exclude={'company'}),
        company=company,
        user_id=c_user.id,
    )
    application = await use_case.execute(int(application_id), data)
    return Application.model_validate(application)


@router.get('/supports', response_model=SupportSchema)
async def get_mcp_supports(
    c_user: CurrentApiKeyUserDp,
    feedback_repo: FeedbackDefinitionRepositoryDp,
    platform_repo: PlatformRepositoryDp,
    step_repo: StepDefinitionRepositoryDp,
):
    """Return supports metadata for MCP clients using API keys."""
    use_case = GetSupportsUseCase(
        feedback_repo=feedback_repo,
        platform_repo=platform_repo,
        step_repo=step_repo,
    )
    return await use_case.execute()


@router.get('/companies', response_model=List[Company])
async def list_mcp_companies(
    c_user: CurrentApiKeyUserDp,
    company_repo: CompanyRepositoryDp,
    name: str | None = Query(None, description='Filter companies by name'),
):
    """Return companies for MCP clients using API keys."""
    use_case = ListCompaniesUseCase(company_repo)
    return await use_case.execute(name=name)
