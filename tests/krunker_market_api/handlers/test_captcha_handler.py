from krunker_market_api.handlers.captcha import _CaptchaHandler, solve_captcha
from krunker_market_api.models import KrunkerMessage
import pytest
from krunker_market_api.models.krunker_captcha import KrunkerCaptcha, KrunkerCaptchaSolution


# kqNjcHSFqWFsZ29yaXRobadTSEEtMjU2qWNoYWxsZW5nZdlANTI4Yzc5YTFkZjYxNDJiODQxYWQ5NTMyOGNmNWE0Nzc0NzY4MzI1ODUxNWY1ZjhiY2M1YjJkYzcwZDA1NGJmOaltYXhudW1iZXLOAAST4KRzYWx02StiN2JiYzQzNjMzYzU4N2UzNjZiNDY2NjY/ZXhwaXJlcz0xNzQ3NjYxOTY2qXNpZ25hdHVyZdlAZWU3OWQ5NzllNGU2OTU0NTc2ODc4NjFhN2I3NjhkOWEzOGRlZjg4YzM5YTQ4NzllNDczMjA1ZTYxYmZmZDQyNAAA
# [
#     "cpt",
#     {
#         "algorithm": "SHA-256",
#         "challenge": "528c79a1df6142b841ad95328cf5a47747683258515f5f8bcc5b2dc70d054bf9",
#         "maxnumber": 300000,
#         "salt": "b7bbc43633c587e366b46666?expires=1747661966",
#         "signature": "ee79d979e4e695457687861a7b768d9a38def88c39a4879e473205e61bffd424"
#     }
# ]

# kqRjcHRS2gFcZXlKaGJHZHZjbWwwYUcwaU9pSlRTRUV0TWpVMklpd2lZMmhoYkd4bGJtZGxJam9pTlRJNFl6YzVZVEZrWmpZeE5ESmlPRFF4WVdRNU5UTXlPR05tTldFME56YzBOelk0TXpJMU9EVXhOV1kxWmpoaVkyTTFZakprWXpjd1pEQTFOR0ptT1NJc0ltNTFiV0psY2lJNk1qWTJPRGt4TENKellXeDBJam9pWWpkaVltTTBNell6TTJNMU9EZGxNelkyWWpRMk5qWTJQMlY0Y0dseVpYTTlNVGMwTnpZMk1UazJOaUlzSW5OcFoyNWhkSFZ5WlNJNkltVmxOemxrT1RjNVpUUmxOamsxTkRVM05qZzNPRFl4WVRkaU56WTRaRGxoTXpoa1pXWTRPR016T1dFME9EYzVaVFEzTXpJd05XVTJNV0ptWm1RME1qUWlMQ0owYjI5cklqb3hOVFo5CQ8=
# [
#     "cptR",
#     "eyJhbGdvcml0aG0iOiJTSEEtMjU2IiwiY2hhbGxlbmdlIjoiNTI4Yzc5YTFkZjYxNDJiODQxYWQ5NTMyOGNmNWE0Nzc0NzY4MzI1ODUxNWY1ZjhiY2M1YjJkYzcwZDA1NGJmOSIsIm51bWJlciI6MjY2ODkxLCJzYWx0IjoiYjdiYmM0MzYzM2M1ODdlMzY2YjQ2NjY2P2V4cGlyZXM9MTc0NzY2MTk2NiIsInNpZ25hdHVyZSI6ImVlNzlkOTc5ZTRlNjk1NDU3Njg3ODYxYTdiNzY4ZDlhMzhkZWY4OGMzOWE0ODc5ZTQ3MzIwNWU2MWJmZmQ0MjQiLCJ0b29rIjoxNTZ9"
# ]

@pytest.mark.asyncio
async def test_handle_receive__real_input__matches_real_output():
    sent_messages = []

    async def mock_send(message: KrunkerMessage):
        sent_messages.append(message)

    async def mock_solve_captcha(captcha: KrunkerCaptcha) -> KrunkerCaptchaSolution:
        result = await solve_captcha(captcha)
        result.took = 156  # Mock the time taken to solve the captcha to match the expected output
        return result

    # Arrange
    handler = _CaptchaHandler(mock_send, mock_solve_captcha)
    message = KrunkerMessage("cpt", [
        {
            "algorithm": "SHA-256",
            "challenge": "528c79a1df6142b841ad95328cf5a47747683258515f5f8bcc5b2dc70d054bf9",
            "maxnumber": 300000,
            "salt": "b7bbc43633c587e366b46666?expires=1747661966",
            "signature": "ee79d979e4e695457687861a7b768d9a38def88c39a4879e473205e61bffd424"
        }
    ])
    expected_response = KrunkerMessage("cptR", [
        "eyJhbGdvcml0aG0iOiJTSEEtMjU2IiwiY2hhbGxlbmdlIjoiNTI4Yzc5YTFkZjYxNDJiODQxYWQ5NTMyOGNmNWE0Nzc0NzY4MzI1ODUxNWY1ZjhiY2M1YjJkYzcwZDA1NGJmOSIsIm51bWJlciI6MjY2ODkxLCJzYWx0IjoiYjdiYmM0MzYzM2M1ODdlMzY2YjQ2NjY2P2V4cGlyZXM9MTc0NzY2MTk2NiIsInNpZ25hdHVyZSI6ImVlNzlkOTc5ZTRlNjk1NDU3Njg3ODYxYTdiNzY4ZDlhMzhkZWY4OGMzOWE0ODc5ZTQ3MzIwNWU2MWJmZmQ0MjQiLCJ0b29rIjoxNTZ9"
    ])

    # Act
    assert await handler.can_handle_receive(message) is True
    await handler.handle_receive(message)

    # Assert
    assert len(sent_messages) == 1
    assert sent_messages[0] == expected_response
