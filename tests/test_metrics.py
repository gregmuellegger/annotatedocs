from annotatedocs import metrics


def test_require():
    class Dependency(metrics.Metric):
        pass

    @metrics.require(Dependency)
    class Dependent(metrics.Metric):
        pass

    assert Dependent.get_required_metrics() == [Dependency]
