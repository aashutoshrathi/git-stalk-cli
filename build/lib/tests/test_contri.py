import pytest
import git_stalk
def test_contri_fake_anshu():
    fake_anshu = git_stalk.show_contri("shaun-frost")
    assert(fake_anshu == 0)

def test_contri_anshu():
    anshu = git_stalk.show_contri("anshumanv")
    assert(anshu > 5)