import pytest
import git_stalk.stalk as sk

def test_contri_fake_anshu():
    fake_anshu = sk.show_contri("shaun-frost")
    assert(fake_anshu == "shaun-frost have made 0 contributions today.")