import pytest
import git_stalk.stalk as sk

def test_contri_fake_anshu():
    fake_anshu = sk.jft("shaun-frost")
    assert(fake_anshu == 200 or fake_anshu == 403)
