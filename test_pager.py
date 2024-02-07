import pytest
import pytest_asyncio
from aiohttp import web
import sys 
sys.path.append("")
from pager import Pager


@pytest_asyncio.fixture
def test_url():
    return 'http://testserver:19883/page'


@pytest_asyncio.fixture
async def pager(test_url):
    pager = Pager(test_url)
    await pager.open_session()
    yield pager
    await pager.close_session()


@pytest_asyncio.fixture
async def mock_server(aiohttp_server, loop):
    async def mock_handler(request):
        return web.Response(text="Success", status=200)

    app = web.Application()
    app.router.add_post('/page', mock_handler)
    server = await aiohttp_server(app)
    return server


@pytest.mark.asyncio
async def test_open_session(pager):
    assert pager.session is not None
    assert not pager.session.closed


@pytest.mark.asyncio
async def test_close_session(pager):
    await pager.close_session()
    assert pager.session.closed


@pytest.mark.asyncio
async def test_parse(pager):
    with pytest.raises(Exception):
        await pager.parse(("歪比巴卜", "yeahyeahyeah"))
        await pager.parse(("666666", 'c'))
    try:
        await pager.parse(("114514", "y"))
        await pager.parse((1919810, "y"))
    except Exception as e:
        pytest.fail(f"Unexpected exception: {e}")


@pytest.mark.asyncio
async def test_post_success(pager, mock_server):
    pager.url = f'http://{mock_server.host}:{mock_server.port}/page'
    response = await pager.post('123')
    assert response == "Success"


@pytest.mark.asyncio
async def test_post_network_error(pager):
    pager.url = 'http://this.urldoesnot.exist'
    response = await pager.post('123')
    assert response is None
