# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

from arche.resources import User
from arche.testing import barebone_fixture
from pyramid import testing
from pyramid.request import apply_request_extensions
from pyramid_mailer import get_mailer


class NotificationTests(TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.config.include('pyramid_chameleon')
        self.config.include('pyramid_mailer.testing')
        self.config.include('arche.testing')
        self.config.include('arche_comments.models.notification')

    def tearDown(self):
        testing.tearDown()

    def _fixture(self):
        from arche_comments.models.comments import CommentsFolder
        root = barebone_fixture()
        root['users']['a'] = User(email='hello@world.org')
        root['_comments'] = CommentsFolder()
        request = testing.DummyRequest()
        apply_request_extensions(request)
        request.root = root
        self.config.begin(request)
        return root, request

    @property
    def _comment(self):
        from arche_comments.models.comment import Comment
        return Comment

    def test_basic(self):
        root, request = self._fixture()
        comments = root['_comments']
        comments.add_subscribing_userid('a')
        comments.add_subscribing_userid('b')
        comments['hi'] = self._comment(body='Hello world')
        mailer = get_mailer(self.config.registry)
        self.assertEqual(len(mailer.outbox), 1)
        #self.assertEqual(mailer.outbox[0].subject, "hello world")
        #mailer = get_mailer(registry)
        #self.assertEqual(len(mailer.outbox), 1)
        #self.assertEqual(mailer.outbox[0].subject, "hello world")

