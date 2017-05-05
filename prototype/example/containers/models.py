"""Model providers container."""

import microjet.core.models as models

import example.models.users
import example.models.photos
import example.handlers.example

from .services import Services


class Models(models.Container):
    """Photo model providers container."""

    photos_factory = models.DelegatedFactory(example.models.photos.Photo)

    photos_manager = models.Singleton(example.models.photos.PhotosManager,
                                      photos_factory=photos_factory,
                                      db=Services.db)

    users_factory = models.DelegatedFactory(example.models.users.User)

    users_manager = models.Singleton(example.models.users.UsersManager,
                                     users_factory=users_factory,
                                     photos_manager=photos_manager,
                                     db=Services.db)