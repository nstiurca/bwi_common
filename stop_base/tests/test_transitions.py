#!/usr/bin/env python

# enable some python3 compatibility options:
# (unicode_literals not compatible with python2 uuid module)
from __future__ import absolute_import, print_function

import copy
import uuid
import unittest

# ROS dependencies
from bwi_msgs.msg import StopBaseStatus
from bwi_msgs.srv import StopBaseRequest, StopBaseResponse

# module being tested:
from stop_base.transitions import *


class TestTransitions(unittest.TestCase):
    """Unit tests for stop base controller state transitions.

    These tests do not require a running ROS core.
    """
    def test_constructor(self):
        st = StopBaseState()
        self.assertEqual(st.status, StopBaseStatus.RUNNING)
        self.assertEqual(len(st.pauses), 0)

    def test_state_names(self):
        # test that STATE_NAME list matches the actual values
        self.assertEqual(len(STATE_NAME), 3)
        self.assertEqual(STATE_NAME[StopBaseStatus.RUNNING], 'RUNNING')
        self.assertEqual(STATE_NAME[StopBaseStatus.PAUSED], 'PAUSED')
        self.assertEqual(STATE_NAME[StopBaseStatus.STOPPED], 'STOPPED')

    def test_valid(self):
        # first, start in RUNNING state
        st = StopBaseState()
        self.assertTrue(st._valid(StopBaseStatus.RUNNING))
        self.assertTrue(st._valid(StopBaseStatus.PAUSED))
        self.assertTrue(st._valid(StopBaseStatus.STOPPED))

        # now, try PAUSED state
        st._transition(StopBaseRequest(
                status=StopBaseStatus.PAUSED,
                requester='test_valid'))
        self.assertTrue(st._valid(StopBaseStatus.RUNNING))
        self.assertTrue(st._valid(StopBaseStatus.PAUSED))
        self.assertTrue(st._valid(StopBaseStatus.STOPPED))

        # last, try STOPPED state
        st._transition(StopBaseRequest(
                status=StopBaseStatus.STOPPED,
                requester='test_valid'))
        self.assertFalse(st._valid(StopBaseStatus.RUNNING))
        self.assertFalse(st._valid(StopBaseStatus.PAUSED))
        self.assertTrue(st._valid(StopBaseStatus.STOPPED))

    def test_pause_and_resume(self):
        # first, start in RUNNING state
        st = StopBaseState()
        self.assertEqual(st.status, StopBaseStatus.RUNNING)

        # now, request PAUSED state
        st._transition(StopBaseRequest(
                status=StopBaseStatus.PAUSED,
                requester='pause_requester_1'))
        self.assertEqual(st.status, StopBaseStatus.PAUSED)

        # then, tell it to run again
        st._transition(StopBaseRequest(
                status=StopBaseStatus.RUNNING,
                requester='pause_requester_1'))
        self.assertEqual(st.status, StopBaseStatus.RUNNING)

    def test_multi_pauses(self):
        # first, start in RUNNING state
        st = StopBaseState()
        self.assertEqual(st.status, StopBaseStatus.RUNNING)

        # now, request PAUSED state twice
        st._transition(StopBaseRequest(
                status=StopBaseStatus.PAUSED,
                requester='pause_requester_1'))
        st._transition(StopBaseRequest(
                status=StopBaseStatus.PAUSED,
                requester='pause_requester_2'))
        self.assertEqual(st.status, StopBaseStatus.PAUSED)

        # tell it to run again once
        st._transition(StopBaseRequest(
                status=StopBaseStatus.RUNNING,
                requester='pause_requester_1'))
        self.assertEqual(st.status, StopBaseStatus.PAUSED)

        # the first requester cannot cancel the second requester's pause
        st._transition(StopBaseRequest(
                status=StopBaseStatus.RUNNING,
                requester='pause_requester_1'))
        self.assertEqual(st.status, StopBaseStatus.PAUSED)

        # finally, let the second requester resume
        st._transition(StopBaseRequest(
                status=StopBaseStatus.RUNNING,
                requester='pause_requester_2'))
        self.assertEqual(st.status, StopBaseStatus.RUNNING)


if __name__ == '__main__':
    import rosunit
    rosunit.unitrun('stop_base', 'test_transitions', TestTransitions)

