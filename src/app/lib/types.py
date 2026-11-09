type JSONScalar = str | int | float | bool | None
type JSONType = JSONScalar | JSONList | JSONObject
type JSONList = list[JSONType]
type JSONObject = dict[str, JSONType]
