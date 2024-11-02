import pytest
from unittest.mock import patch, MagicMock
import make_commit

@pytest.fixture
def mock_response():
    response = MagicMock()
    response.json.return_value = {'key': 'value'}
    return response

def test_make_get_request(mock_response):
    with patch('make_commit.requests.get', return_value=mock_response) as mock_get:
        result = make_commit.make_get_request('test_path')

        assert result == {'key': 'value'}
        mock_get.assert_called_once_with(
            url=f"{make_commit.base_url}/test_path",
            headers=make_commit.auth_header
        )

def test_make_post_request(mock_response):
    with patch('make_commit.requests.post', return_value=mock_response) as mock_post:
        result = make_commit.make_post_request('test_path', {'data': 'test'})

        assert result == {'key': 'value'}
        mock_post.assert_called_once_with(
            f"{make_commit.base_url}/test_path",
            headers=make_commit.auth_header,
            json={'data': 'test'}
        )

def test_get_latest_commit_sha():
    with patch('make_commit.make_get_request') as mock_get_request:
        mock_get_request.return_value = {
            'commit': {'sha': 'test_sha'}
        }
        result = make_commit.get_latest_commit_sha()

        assert result == 'test_sha'
        mock_get_request.assert_called_once_with(path=f"branches/{make_commit.MAIN_BRANCH}")

def test_get_latest_tree_sha():
    with patch('make_commit.make_get_request') as mock_get_request:
        mock_get_request.return_value = {
            'commit': {'commit': {'tree': {'sha': 'test_tree_sha'}}}
        }
        result = make_commit.get_latest_tree_sha()

        assert result == 'test_tree_sha'
        mock_get_request.assert_called_once_with(path=f"branches/{make_commit.MAIN_BRANCH}")

def test_create_new_tree():
    with patch('make_commit.make_post_request') as mock_post_request:
        mock_post_request.return_value = {'sha': 'new_tree_sha'}
        result = make_commit.create_new_tree('base_tree_sha')

        assert result == 'new_tree_sha'
        mock_post_request.assert_called_once()

def test_create_new_commit():
    with patch('make_commit.make_post_request') as mock_post_request:
        mock_post_request.return_value = {'sha': 'new_commit_sha'}
        result = make_commit.create_new_commit('parent_sha', 'tree_sha', 'message')

        assert result == 'new_commit_sha'
        mock_post_request.assert_called_once()

def test_create_new_ref():
    with patch('make_commit.make_post_request') as mock_post_request:
        mock_post_request.return_value = {'ref': 'new_ref'}
        result = make_commit.create_new_ref('ref_name', 'commit_sha')

        assert result == {'ref': 'new_ref'}
        mock_post_request.assert_called_once()

def test_update_ref(mock_response):
    with patch('make_commit.requests.put', return_value=mock_response) as mock_put:
        result = make_commit.update_ref('ref_name', 'commit_sha')

        assert result == {'key': 'value'}
        mock_put.assert_called_once()
