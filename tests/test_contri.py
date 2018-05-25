import pytest
import git_stalk
def test_contri_fake_anshu():
    fake_anshu = git_stalk.show_contri("shaun-frost")
    assert(fake_anshu == "shaun-frost have made 0 contributions today.")