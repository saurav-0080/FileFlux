from app.progress import Progress


def test_percentage_zero_total():
    p = Progress(operation="Scanning")
    assert p.percentage == 0.0


def test_percentage_calculation():
    p = Progress(operation="Hashing", current=250, total=1000)
    assert p.percentage == 25.0


def test_is_complete():
    p = Progress(operation="Organizing", current=100, total=100)
    assert p.is_complete is True


def test_not_complete():
    p = Progress(operation="Organizing", current=50, total=100)
    assert p.is_complete is False


def test_update():
    p = Progress(operation="Scanning", total=500)
    p.update(200, message="Processing images")
    assert p.current == 200
    assert p.message == "Processing images"


def test_str_representation():
    p = Progress(operation="Hashing", current=1, total=4)
    assert "Hashing" in str(p)
    assert "25.0%" in str(p)