"""Tests for Formcheck."""
from src.core import Formcheck
def test_init(): assert Formcheck().get_stats()["ops"] == 0
def test_op(): c = Formcheck(); c.learn(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Formcheck(); [c.learn() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Formcheck(); c.learn(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Formcheck(); r = c.learn(); assert r["service"] == "formcheck"
