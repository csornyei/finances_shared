import os
from logging import Logger
from dataclasses import dataclass


@dataclass
class DatabaseParams:
    """Database connection parameters"""

    host: str
    port: int
    user: str
    password: str
    database: str

    @classmethod
    def from_env(cls, logger: Logger) -> "DatabaseParams":
        """
        Create a DatabaseParams instance from environment variables.

        Args:
            logger (Logger): Logger instance for logging errors.

        Returns:
            DatabaseParams: An instance of DatabaseParams with values from environment variables.
        """
        db_host = os.getenv("POSTGRES_HOST")
        db_port = os.getenv("POSTGRES_PORT")
        db_user = os.getenv("POSTGRES_USER")
        db_password = os.getenv("POSTGRES_PASSWORD")
        db_name = os.getenv("POSTGRES_DB")

        if not db_host or not db_port or not db_user or not db_password or not db_name:
            logger.error(
                "Database connection parameters are not set in environment variables."
            )
            raise ValueError(
                "Database connection parameters are not set in environment variables."
            )

        if not db_port.isdigit():
            raise ValueError("POSTGRES_PORT must be a valid integer.")
        else:
            db_port = int(db_port)

        return cls(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
        )

    def connection_string(self) -> str:
        """
        Get the connection string for the database.

        Returns:
            str: The connection string for the database.
        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


@dataclass
class RabbitMQParams:
    """RabbitMQ connection parameters"""

    host: str
    port: int
    user: str
    password: str

    @classmethod
    def from_env(cls, logger: Logger) -> "RabbitMQParams":
        """
        Get the RabbitMQ connection string from environment variables.

        Returns:
            RabbitMQParams: A dictionary containing the RabbitMQ connection parameters.
        Raises:
            ValueError: If any of the required environment variables are not set.
        """

        rabbitmq_host = os.getenv("RABBITMQ_HOST")
        rabbitmq_port = os.getenv("RABBITMQ_PORT")
        rabbitmq_user = os.getenv("RABBITMQ_USER")
        rabbitmq_password = os.getenv("RABBITMQ_PASSWORD")

        if (
            not rabbitmq_host
            or not rabbitmq_port
            or not rabbitmq_user
            or not rabbitmq_password
        ):
            logger.error(
                "RabbitMQ connection parameters are not set in environment variables."
            )
            raise ValueError(
                "RabbitMQ connection parameters are not set in environment variables."
            )
        if not rabbitmq_port.isdigit():
            raise ValueError("RABBITMQ_PORT must be a valid integer.")
        else:
            rabbitmq_port = int(rabbitmq_port)

        return cls(
            host=rabbitmq_host,
            port=rabbitmq_port,
            user=rabbitmq_user,
            password=rabbitmq_password,
        )

    def connection_string(self) -> str:
        """
        Get the connection string for RabbitMQ.

        Returns:
            str: The connection string for RabbitMQ.
        """
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"
