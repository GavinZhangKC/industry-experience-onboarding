from app.config import Settings


def test_aurora_region_uses_project_specific_environment_name(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AURORA_AWS_REGION", "ap-southeast-2")

    settings = Settings(_env_file=None)

    assert settings.aws_region == "ap-southeast-2"


def test_aws_region_remains_a_backwards_compatible_fallback(monkeypatch):
    monkeypatch.delenv("AURORA_AWS_REGION", raising=False)
    monkeypatch.setenv("AWS_REGION", "ap-southeast-2")

    settings = Settings(_env_file=None)

    assert settings.aws_region == "ap-southeast-2"


def test_aurora_region_can_still_be_passed_by_field_name():
    settings = Settings(aws_region="eu-west-1", _env_file=None)

    assert settings.aws_region == "eu-west-1"
