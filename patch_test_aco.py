content = open("tests/test_aco.py").read()
content = content.replace(
    'select_path(graph, "M", "S6", rng=random.Random(123))',
    'select_path(graph, "M", "S6", alpha=1.0, beta=1.0, rng=random.Random(123))'
)
content = content.replace(
    'select_path(graph, "M", "UNKNOWN") is None',
    'select_path(graph, "M", "UNKNOWN", alpha=1.0, beta=1.0) is None'
)
content = content.replace(
    'select_path(graph, "M", "S6", exploration_rate=1.5)',
    'select_path(graph, "M", "S6", alpha=1.0, beta=1.0, exploration_rate=1.5)'
)
open("tests/test_aco.py", "w").write(content)
