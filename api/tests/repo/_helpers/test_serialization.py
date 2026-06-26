from pydantic import BaseModel
from app.repo._helpers.serialization import load_model, dump_model


# def test_pydantic_model_serialization(subtests):

#     class SomeModel(BaseModel):
#         foo: str
#         bar: int
#         baz: bool = False

#     with subtests.test("load model"):
#         obj = load_model(SomeModel, {"foo": "A FOO", "bar": 42})
#         assert isinstance(obj, SomeModel)
#         assert obj.foo == "A FOO"
#         assert obj.bar == 42
#         assert obj.baz is False

#     with subtests.test("dump model"):
#         obj = SomeModel(foo="FOO2", bar=33)
#         data = dump_model(obj)
#         assert data == {"foo": "FOO2", "bar": 33, "baz": False}
