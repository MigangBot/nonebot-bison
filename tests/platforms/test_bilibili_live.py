import pytest
import respx
from httpx import AsyncClient, Response
from nonebug.app import App

from .utils import get_json


@pytest.fixture
def bili_live(app: App):
    from nonebot_bison.platform import platform_manager
    from nonebot_bison.utils import ProcessContext

    return platform_manager["bilibili-live"](ProcessContext(), AsyncClient())


@pytest.fixture
def dummy_only_open_user_subinfo(app: App):
    from nonebot_bison.types import User, UserSubInfo

    user = User(123, "group")
    return UserSubInfo(user=user, categories=[1], tags=[])


@pytest.mark.asyncio
@respx.mock
async def test_fetch_bililive_only_live_open(bili_live, dummy_only_open_user_subinfo):
    mock_bili_live_status = get_json("bili_live_status.json")

    bili_live_router = respx.get(
        "https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids?uids[]=13164144"
    )
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))

    bilibili_main_page_router = respx.get("https://www.bilibili.com/")
    bilibili_main_page_router.mock(return_value=Response(200))

    target = "13164144"
    res = await bili_live.fetch_new_post(target, [dummy_only_open_user_subinfo])
    assert bili_live_router.call_count == 1
    assert len(res) == 0
    # 直播状态更新-上播
    mock_bili_live_status["data"][target]["live_status"] = 1
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res2 = await bili_live.fetch_new_post(target, [dummy_only_open_user_subinfo])
    post = res2[0][1][0]
    assert post.target_type == "Bilibili直播"
    assert post.text == "[开播] 【Zc】从0挑战到15肉鸽！目前10难度"
    assert post.url == "https://live.bilibili.com/3044248"
    assert post.target_name == "魔法Zc目录 其他单机"
    assert post.pics == [
        "https://i0.hdslb.com/bfs/live/new_room_cover/fd357f0f3cbbb48e9acfbcda616b946c2454c56c.jpg"
    ]
    assert post.compress == True
    # 标题变更
    mock_bili_live_status["data"][target]["title"] = "【Zc】从0挑战到15肉鸽！目前11难度"
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res3 = await bili_live.fetch_new_post(target, [dummy_only_open_user_subinfo])
    assert bili_live_router.call_count == 3
    assert len(res3[0][1]) == 0
    # 直播状态更新-下播
    mock_bili_live_status["data"][target]["live_status"] = 0
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res4 = await bili_live.fetch_new_post(target, [dummy_only_open_user_subinfo])
    assert bili_live_router.call_count == 4
    assert len(res4[0][1]) == 0


@pytest.fixture
def dummy_only_title_user_subinfo(app: App):
    from nonebot_bison.types import User, UserSubInfo

    user = User(123, "group")
    return UserSubInfo(user=user, categories=[2], tags=[])


@pytest.mark.asyncio
@respx.mock
async def test_fetch_bililive_only_title_change(
    bili_live, dummy_only_title_user_subinfo
):
    mock_bili_live_status = get_json("bili_live_status.json")
    target = "13164144"

    bili_live_router = respx.get(
        "https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids?uids[]=13164144"
    )
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))

    bilibili_main_page_router = respx.get("https://www.bilibili.com/")
    bilibili_main_page_router.mock(return_value=Response(200))

    res = await bili_live.fetch_new_post(target, [dummy_only_title_user_subinfo])
    assert bili_live_router.call_count == 1
    assert len(res) == 0
    # 未开播前标题变更
    mock_bili_live_status["data"][target]["title"] = "【Zc】从0挑战到15肉鸽！目前11难度"
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res0 = await bili_live.fetch_new_post(target, [dummy_only_title_user_subinfo])
    assert bili_live_router.call_count == 2
    assert len(res0) == 0
    # 直播状态更新-上播
    mock_bili_live_status["data"][target]["live_status"] = 1
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res2 = await bili_live.fetch_new_post(target, [dummy_only_title_user_subinfo])
    assert bili_live_router.call_count == 3
    assert len(res2[0][1]) == 0
    # 标题变更
    mock_bili_live_status["data"][target]["title"] = "【Zc】从0挑战到15肉鸽！目前12难度"
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res3 = await bili_live.fetch_new_post(target, [dummy_only_title_user_subinfo])
    post = res3[0][1][0]
    assert post.target_type == "Bilibili直播"
    assert post.text == "[标题更新] 【Zc】从0挑战到15肉鸽！目前12难度"
    assert post.url == "https://live.bilibili.com/3044248"
    assert post.target_name == "魔法Zc目录 其他单机"
    assert post.pics == [
        "https://i0.hdslb.com/bfs/live-key-frame/keyframe10170435000003044248mwowx0.jpg"
    ]
    assert post.compress == True
    # 直播状态更新-下播
    mock_bili_live_status["data"][target]["live_status"] = 0
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res4 = await bili_live.fetch_new_post(target, [dummy_only_title_user_subinfo])
    assert bili_live_router.call_count == 5
    assert len(res4[0][1]) == 0


@pytest.fixture
def dummy_only_close_user_subinfo(app: App):
    from nonebot_bison.types import User, UserSubInfo

    user = User(123, "group")
    return UserSubInfo(user=user, categories=[3], tags=[])


@pytest.mark.asyncio
@respx.mock
async def test_fetch_bililive_only_close(bili_live, dummy_only_close_user_subinfo):
    mock_bili_live_status = get_json("bili_live_status.json")
    target = "13164144"

    bili_live_router = respx.get(
        "https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids?uids[]=13164144"
    )
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))

    bilibili_main_page_router = respx.get("https://www.bilibili.com/")
    bilibili_main_page_router.mock(return_value=Response(200))

    res = await bili_live.fetch_new_post(target, [dummy_only_close_user_subinfo])
    assert bili_live_router.call_count == 1
    assert len(res) == 0
    # 未开播前标题变更
    mock_bili_live_status["data"][target]["title"] = "【Zc】从0挑战到15肉鸽！目前11难度"
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res0 = await bili_live.fetch_new_post(target, [dummy_only_close_user_subinfo])
    assert bili_live_router.call_count == 2
    assert len(res0) == 0
    # 直播状态更新-上播
    mock_bili_live_status["data"][target]["live_status"] = 1
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res2 = await bili_live.fetch_new_post(target, [dummy_only_close_user_subinfo])
    assert bili_live_router.call_count == 3
    assert len(res2[0][1]) == 0
    # 标题变更
    mock_bili_live_status["data"][target]["title"] = "【Zc】从0挑战到15肉鸽！目前12难度"
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res3 = await bili_live.fetch_new_post(target, [dummy_only_close_user_subinfo])
    assert bili_live_router.call_count == 4
    assert len(res3[0][1]) == 0
    # 直播状态更新-下播
    mock_bili_live_status["data"][target]["live_status"] = 0
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res4 = await bili_live.fetch_new_post(target, [dummy_only_close_user_subinfo])
    assert bili_live_router.call_count == 5
    post = res4[0][1][0]
    assert post.target_type == "Bilibili直播"
    assert post.text == "[下播] 【Zc】从0挑战到15肉鸽！目前12难度"
    assert post.url == "https://live.bilibili.com/3044248"
    assert post.target_name == "魔法Zc目录 其他单机"
    assert post.pics == [
        "https://i0.hdslb.com/bfs/live-key-frame/keyframe10170435000003044248mwowx0.jpg"
    ]
    assert post.compress == True


@pytest.fixture
def dummy_bililive_user_subinfo(app: App):
    from nonebot_bison.types import User, UserSubInfo

    user = User(123, "group")
    return UserSubInfo(user=user, categories=[1, 2, 3], tags=[])


@pytest.mark.asyncio
@respx.mock
async def test_fetch_bililive_combo(bili_live, dummy_bililive_user_subinfo):
    mock_bili_live_status = get_json("bili_live_status.json")
    target = "13164144"

    bili_live_router = respx.get(
        "https://api.live.bilibili.com/room/v1/Room/get_status_info_by_uids?uids[]=13164144"
    )
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))

    bilibili_main_page_router = respx.get("https://www.bilibili.com/")
    bilibili_main_page_router.mock(return_value=Response(200))

    res = await bili_live.fetch_new_post(target, [dummy_bililive_user_subinfo])
    assert bili_live_router.call_count == 1
    assert len(res) == 0
    # 未开播前标题变更
    mock_bili_live_status["data"][target]["title"] = "【Zc】从0挑战到15肉鸽！目前11难度"
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res0 = await bili_live.fetch_new_post(target, [dummy_bililive_user_subinfo])
    assert bili_live_router.call_count == 2
    assert len(res0) == 0
    # 直播状态更新-上播
    mock_bili_live_status["data"][target]["live_status"] = 1
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res2 = await bili_live.fetch_new_post(target, [dummy_bililive_user_subinfo])
    post2 = res2[0][1][0]
    assert post2.target_type == "Bilibili直播"
    assert post2.text == "[开播] 【Zc】从0挑战到15肉鸽！目前11难度"
    assert post2.url == "https://live.bilibili.com/3044248"
    assert post2.target_name == "魔法Zc目录 其他单机"
    assert post2.pics == [
        "https://i0.hdslb.com/bfs/live/new_room_cover/fd357f0f3cbbb48e9acfbcda616b946c2454c56c.jpg"
    ]
    assert post2.compress == True
    # 标题变更
    mock_bili_live_status["data"][target]["title"] = "【Zc】从0挑战到15肉鸽！目前12难度"
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res3 = await bili_live.fetch_new_post(target, [dummy_bililive_user_subinfo])
    post3 = res3[0][1][0]
    assert post3.target_type == "Bilibili直播"
    assert post3.text == "[标题更新] 【Zc】从0挑战到15肉鸽！目前12难度"
    assert post3.url == "https://live.bilibili.com/3044248"
    assert post3.target_name == "魔法Zc目录 其他单机"
    assert post3.pics == [
        "https://i0.hdslb.com/bfs/live-key-frame/keyframe10170435000003044248mwowx0.jpg"
    ]
    assert post3.compress == True
    # 直播状态更新-下播
    mock_bili_live_status["data"][target]["live_status"] = 0
    bili_live_router.mock(return_value=Response(200, json=mock_bili_live_status))
    res4 = await bili_live.fetch_new_post(target, [dummy_bililive_user_subinfo])
    post4 = res4[0][1][0]
    assert post4.target_type == "Bilibili直播"
    assert post4.text == "[下播] 【Zc】从0挑战到15肉鸽！目前12难度"
    assert post4.url == "https://live.bilibili.com/3044248"
    assert post4.target_name == "魔法Zc目录 其他单机"
    assert post4.pics == [
        "https://i0.hdslb.com/bfs/live-key-frame/keyframe10170435000003044248mwowx0.jpg"
    ]
    assert post4.compress == True
