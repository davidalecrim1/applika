import json
import os
import sys
from dataclasses import dataclass
from datetime import date
from typing import Any

from api import ApiClient, ApiError

MODE_CHOICES = ('active', 'passive', 'all')
STATUS_CHOICES = ('active', 'finalized', 'all')
WORK_MODE_CHOICES = ('remote', 'hybrid', 'on_site')
EXPERIENCE_CHOICES = (
    'intern',
    'junior',
    'mid_level',
    'senior',
    'staff',
    'lead',
    'principal',
    'specialist',
)
CURRENCY_CHOICES = (
    'USD',
    'BRL',
    'EUR',
    'GBP',
    'CAD',
    'AUD',
    'JPY',
    'CHF',
    'INR',
)
SALARY_PERIOD_CHOICES = ('hourly', 'monthly', 'annual')
JSONRPC_VERSION = '2.0'
MCP_PROTOCOL_VERSION = '2024-11-05'


@dataclass
class McpServer:
    client: ApiClient

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                'name': 'applications_list',
                'description': 'List applications for the authenticated user.',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'cycle_id': {'type': 'string'},
                        'search': {'type': 'string'},
                        'mode': {'type': 'string', 'enum': list(MODE_CHOICES)},
                        'status': {
                            'type': 'string',
                            'enum': list(STATUS_CHOICES),
                        },
                        'platform': {'type': 'string'},
                        'from_date': {'type': 'string'},
                        'to_date': {'type': 'string'},
                    },
                },
            },
            {
                'name': 'applications_create',
                'description': 'Create a new application.',
                'inputSchema': {
                    'type': 'object',
                    'required': [
                        'company',
                        'role',
                        'platform',
                        'mode',
                        'application_date',
                    ],
                    'properties': application_input_properties(),
                },
            },
            {
                'name': 'applications_edit',
                'description': 'Edit an existing current-cycle application.',
                'inputSchema': {
                    'type': 'object',
                    'required': ['application_id'],
                    'properties': {
                        'application_id': {'type': 'string'},
                        **application_input_properties(),
                        'clear_job_url': {'type': 'boolean'},
                        'clear_observation': {'type': 'boolean'},
                        'clear_country': {'type': 'boolean'},
                        'clear_salary': {'type': 'boolean'},
                    },
                },
            },
        ]

    def handle_request(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get('method')
        request_id = request.get('id')

        if method == 'initialize':
            return {
                'jsonrpc': JSONRPC_VERSION,
                'id': request_id,
                'result': {
                    'protocolVersion': MCP_PROTOCOL_VERSION,
                    'capabilities': {'tools': {}},
                    'serverInfo': {
                        'name': 'applika-mcp',
                        'version': '0.1.0',
                    },
                },
            }

        if method == 'notifications/initialized':
            return None

        if method == 'tools/list':
            return {
                'jsonrpc': JSONRPC_VERSION,
                'id': request_id,
                'result': {'tools': self.list_tools()},
            }

        if method == 'tools/call':
            try:
                params = request.get('params') or {}
                tool_name = params['name']
                arguments = params.get('arguments') or {}
                result = self.call_tool(tool_name, arguments)
                return {
                    'jsonrpc': JSONRPC_VERSION,
                    'id': request_id,
                    'result': {
                        'content': [
                            {
                                'type': 'text',
                                'text': json.dumps(result, indent=2, sort_keys=True),
                            }
                        ]
                    },
                }
            except Exception as error:
                return {
                    'jsonrpc': JSONRPC_VERSION,
                    'id': request_id,
                    'error': {
                        'code': -32000,
                        'message': str(error),
                    },
                }

        return {
            'jsonrpc': JSONRPC_VERSION,
            'id': request_id,
            'error': {
                'code': -32601,
                'message': f'Method not found: {method}',
            },
        }

    def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        if tool_name == 'applications_list':
            params = {}
            if arguments.get('cycle_id'):
                params['cycle_id'] = arguments['cycle_id']
            applications = self.client.get_json('/mcp/applications', params=params or None)
            supports = self.client.get_json('/mcp/supports')
            return filter_applications(applications, supports, arguments)

        if tool_name == 'applications_create':
            payload = build_application_payload(
                self.client,
                arguments,
                existing=None,
            )
            return self.client.post_json('/mcp/applications', payload)

        if tool_name == 'applications_edit':
            application_id = str(arguments.get('application_id', '')).strip()
            if not application_id:
                raise ValueError('application_id is required')
            applications = self.client.get_json('/mcp/applications')
            existing = next(
                (
                    application
                    for application in applications
                    if str(application['id']) == application_id
                ),
                None,
            )
            if existing is None:
                raise ValueError('Application not found in the current cycle')
            if existing.get('finalized'):
                raise ValueError('Finalized applications cannot be edited')
            payload = build_application_payload(
                self.client,
                arguments,
                existing=existing,
            )
            return self.client.put_json(
                f'/mcp/applications/{application_id}',
                payload,
            )

        raise ValueError(f'Unknown tool: {tool_name}')


def application_input_properties() -> dict[str, Any]:
    return {
        'company': {'type': 'string'},
        'company_url': {'type': 'string'},
        'role': {'type': 'string'},
        'platform': {'type': 'string'},
        'mode': {'type': 'string', 'enum': list(MODE_CHOICES[:2])},
        'application_date': {'type': 'string'},
        'job_url': {'type': 'string'},
        'observation': {'type': 'string'},
        'expected_salary': {'type': 'number'},
        'salary_min': {'type': 'number'},
        'salary_max': {'type': 'number'},
        'currency': {'type': 'string', 'enum': list(CURRENCY_CHOICES)},
        'salary_period': {
            'type': 'string',
            'enum': list(SALARY_PERIOD_CHOICES),
        },
        'experience_level': {
            'type': 'string',
            'enum': list(EXPERIENCE_CHOICES),
        },
        'work_mode': {'type': 'string', 'enum': list(WORK_MODE_CHOICES)},
        'country': {'type': 'string'},
    }


def read_message() -> dict[str, Any] | None:
    headers = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b'\r\n', b'\n'):
            break
        name, value = line.decode().split(':', 1)
        headers[name.strip().lower()] = value.strip()
    content_length = int(headers['content-length'])
    body = sys.stdin.buffer.read(content_length)
    return json.loads(body.decode())


def write_message(payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode()
    sys.stdout.buffer.write(f'Content-Length: {len(body)}\r\n\r\n'.encode())
    sys.stdout.buffer.write(body)
    sys.stdout.buffer.flush()


def main() -> int:
    api_key = os.getenv('APPLIKA_API_KEY')
    if not api_key:
        print('APPLIKA_API_KEY is required', file=sys.stderr)
        return 1

    api_base_url = os.getenv('APPLIKA_API_BASE_URL', 'http://127.0.0.1:8000/api')
    client = ApiClient(api_base_url=api_base_url, api_key=api_key)
    server = McpServer(client)

    try:
        while True:
            message = read_message()
            if message is None:
                return 0
            response = server.handle_request(message)
            if response is not None:
                write_message(response)
    except (ApiError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    finally:
        client.close()


def filter_applications(
    applications: list[dict[str, Any]],
    supports: dict[str, Any],
    args: dict[str, Any],
) -> list[dict[str, Any]]:
    platform_id = None
    if args.get('platform'):
        platform_id = resolve_platform_id(supports, args['platform'])

    filtered = []
    search = (args.get('search') or '').strip().lower()
    from_date = parse_date(args['from_date']) if args.get('from_date') else None
    to_date = parse_date(args['to_date']) if args.get('to_date') else None
    mode = args.get('mode', 'all')
    status = args.get('status', 'all')

    for application in applications:
        if search:
            company_name = (application.get('company_name') or '').lower()
            role = (application.get('role') or '').lower()
            if search not in company_name and search not in role:
                continue
        if mode != 'all' and application.get('mode') != mode:
            continue
        if status == 'active' and application.get('finalized'):
            continue
        if status == 'finalized' and not application.get('finalized'):
            continue
        if platform_id and str(application.get('platform_id')) != platform_id:
            continue
        app_date = parse_date(application['application_date'])
        if from_date and app_date < from_date:
            continue
        if to_date and app_date > to_date:
            continue
        filtered.append(application)

    filtered.sort(key=lambda item: item['application_date'], reverse=True)
    return filtered


def build_application_payload(
    client: ApiClient,
    args: dict[str, Any],
    *,
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    supports = client.get_json('/mcp/supports')
    company = resolve_company_input(
        client,
        company_name=args.get('company'),
        company_url=args.get('company_url'),
        existing=existing,
    )
    platform_id = (
        resolve_platform_id(supports, args['platform'])
        if args.get('platform')
        else str(existing['platform_id'])
    )
    application_date = (
        ensure_date_string(args['application_date'])
        if args.get('application_date')
        else existing['application_date']
    )
    role = args['role'] if args.get('role') is not None else existing['role']
    mode = args['mode'] if args.get('mode') is not None else existing['mode']
    link_to_job = choose_optional_value(
        provided=args.get('job_url'),
        existing=existing.get('link_to_job') if existing else None,
        clear=bool(args.get('clear_job_url')),
    )
    observation = choose_optional_value(
        provided=args.get('observation'),
        existing=existing.get('observation') if existing else None,
        clear=bool(args.get('clear_observation')),
    )
    country = choose_optional_value(
        provided=args.get('country'),
        existing=existing.get('country') if existing else None,
        clear=bool(args.get('clear_country')),
    )
    salary = build_salary_fields(args, existing)

    return {
        'company': company,
        'platform_id': platform_id,
        'role': role,
        'mode': mode,
        'application_date': application_date,
        'link_to_job': link_to_job,
        'observation': observation,
        'country': country,
        'currency': salary['currency'],
        'salary_period': salary['salary_period'],
        'expected_salary': salary['expected_salary'],
        'salary_range_min': salary['salary_range_min'],
        'salary_range_max': salary['salary_range_max'],
        'experience_level': (
            args['experience_level']
            if args.get('experience_level') is not None
            else (existing.get('experience_level') if existing else None)
        ),
        'work_mode': (
            args['work_mode']
            if args.get('work_mode') is not None
            else (existing.get('work_mode') if existing else None)
        ),
    }


def build_salary_fields(
    args: dict[str, Any],
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    if args.get('clear_salary'):
        return {
            'currency': None,
            'salary_period': None,
            'expected_salary': None,
            'salary_range_min': None,
            'salary_range_max': None,
        }

    expected_salary = (
        args['expected_salary']
        if args.get('expected_salary') is not None
        else (existing.get('expected_salary') if existing else None)
    )
    salary_range_min = (
        args['salary_min']
        if args.get('salary_min') is not None
        else (existing.get('salary_range_min') if existing else None)
    )
    salary_range_max = (
        args['salary_max']
        if args.get('salary_max') is not None
        else (existing.get('salary_range_max') if existing else None)
    )
    currency = (
        args['currency']
        if args.get('currency') is not None
        else (existing.get('currency') if existing else None)
    )
    salary_period = (
        args['salary_period']
        if args.get('salary_period') is not None
        else (existing.get('salary_period') if existing else None)
    )
    has_salary = any(
        value is not None
        for value in (
            expected_salary,
            salary_range_min,
            salary_range_max,
        )
    )
    if has_salary and (currency is None or salary_period is None):
        raise ValueError(
            'Currency and salary period are required when salary is set'
        )
    return {
        'currency': currency,
        'salary_period': salary_period,
        'expected_salary': expected_salary,
        'salary_range_min': salary_range_min,
        'salary_range_max': salary_range_max,
    }


def resolve_company_input(
    client: ApiClient,
    *,
    company_name: str | None,
    company_url: str | None,
    existing: dict[str, Any] | None,
) -> str | dict[str, Any]:
    if company_name is None:
        if existing is None:
            raise ValueError('Company is required')
        if existing.get('company_id'):
            return str(existing['company_id'])
        return {
            'name': existing['company_name'],
            'url': None,
        }

    query = company_name.strip().lower()
    matches = client.get_json('/mcp/companies', params={'name': query})
    exact_match = next(
        (
            company
            for company in matches
            if company['name'].strip().lower() == query
        ),
        None,
    )
    if exact_match:
        return str(exact_match['id'])
    return {
        'name': company_name.strip(),
        'url': company_url or None,
    }


def resolve_platform_id(supports: dict[str, Any], platform_name: str) -> str:
    normalized_name = platform_name.strip().lower()
    match = next(
        (
            platform
            for platform in supports['platforms']
            if platform['name'].strip().lower() == normalized_name
        ),
        None,
    )
    if match is None:
        valid = ', '.join(
            sorted(platform['name'] for platform in supports['platforms'])
        )
        raise ValueError(f'Unknown platform. Valid options: {valid}')
    return str(match['id'])


def choose_optional_value(
    *,
    provided: str | None,
    existing: str | None,
    clear: bool,
) -> str | None:
    if clear:
        return None
    if provided is not None:
        return provided
    return existing


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def ensure_date_string(value: str) -> str:
    parse_date(value)
    return value


if __name__ == '__main__':
    raise SystemExit(main())
