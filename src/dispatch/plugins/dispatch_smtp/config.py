from pydantic import Field, SecretStr

from dispatch.config import BaseConfigurationModel


class SMTPConfiguration(BaseConfigurationModel):
    """SMTP configuration"""

    smtp_server: str = Field(
        title="SMTP Server",
        description="SMTP Server address.",
    )
    smtp_port: str = Field(
        title="SMTP Server Port",
        description="SMTP Server Port, default is 25",
    )
    from_email_address: str = Field(
        title="From email address",
        description="From email address.",
    )
