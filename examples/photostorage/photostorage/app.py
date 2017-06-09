"""PhotoStorage application."""

import asyncio
import logging

import aiohttp
import passlib.hash

from microjet.ioc import (ApplicationContainer, Configuration, Factory,
                          Singleton, Callable)
from microjet.gateways import pg
from microjet.gateways import redis
from microjet.gateways import s3

from . import models
from . import mappers
from . import services
from . import webapi


class PhotoStorage(ApplicationContainer):
    """Application container."""

    # Core
    config = Configuration(name='config')
    logger = Singleton(logging.getLogger, name='example')
    loop = Singleton(asyncio.get_event_loop)

    # Gateways
    database = Singleton(pg.PostgreSQL, config=config.pgsql, loop=loop)
    redis = Singleton(redis.Redis, config=config.redis, loop=loop)
    s3 = Singleton(s3.S3, config=config.s3, loop=loop)

    # Profiles
    profile_model_factory = Factory(models.Profile)

    profile_mapper = Singleton(
        mappers.ProfileMapper,
        profile_model_factory=profile_model_factory.delegate(),
        database=database)

    profile_password_hasher_factory = Factory(
        passlib.hash.scrypt.using,
        salt_size=32, rounds=16, block_size=8, parallelism=1)

    profile_password_service = Singleton(
        services.ProfilePasswordService,
        profile_password_hasher=profile_password_hasher_factory)

    profile_registration_service = Singleton(
        services.ProfileRegistrationService,
        profile_model_factory=profile_model_factory.delegate(),
        profile_password_service=profile_password_service,
        profile_mapper=profile_mapper)

    # Auth
    auth_token_model_factory = Factory(models.AuthToken)

    auth_token_mapper = Singleton(
        mappers.AuthTokenMapper,
        auth_token_model_factory=auth_token_model_factory.delegate(),
        database=database)

    auth_service = Singleton(
        services.AuthenticationService,
        auth_token_model_factory=auth_token_model_factory.delegate(),
        database=database)

    # Photos
    photo_model_factory = Factory(models.Photo)

    photo_mapper = Singleton(
        mappers.PhotoMapper,
        photo_model_factory=photo_model_factory.delegate(),
        database=database)

    photo_uploading_service = Singleton(
        services.PhotoUploadingService,
        photo_model_factory=photo_model_factory.delegate(),
        database=database)

    # Web API
    web_handle = Factory(webapi.example_hander, logger=logger, db=database)

    web_app_factory = Factory(aiohttp.web.Application, logger=logger,
                              debug=config.debug)

    run_web_app = Callable(aiohttp.web.run_app, host=config.host,
                           port=config.port, loop=loop)
