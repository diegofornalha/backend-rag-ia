import pytest
from typing import List, Dict, Optional, Any
from ..middleware.type_validator import TypeValidator, TypeValidationError

def test_validate_basic_types():
    """Testa validação de tipos básicos"""
    # String
    assert TypeValidator.validate_type("test", str)
    assert not TypeValidator.validate_type(123, str)
    
    # Int
    assert TypeValidator.validate_type(123, int)
    assert not TypeValidator.validate_type("123", int)
    
    # Float
    assert TypeValidator.validate_type(1.23, float)
    assert not TypeValidator.validate_type("1.23", float)
    
    # Bool
    assert TypeValidator.validate_type(True, bool)
    assert not TypeValidator.validate_type("true", bool)

def test_validate_list():
    """Testa validação de listas"""
    # Lista de strings
    assert TypeValidator.validate_type(["a", "b"], List[str])
    assert not TypeValidator.validate_type([1, 2], List[str])
    assert not TypeValidator.validate_type(["a", 1], List[str])
    
    # Lista de ints
    assert TypeValidator.validate_type([1, 2], List[int])
    assert not TypeValidator.validate_type(["1", "2"], List[int])
    
    # Lista vazia
    assert TypeValidator.validate_type([], List[str])
    assert TypeValidator.validate_type([], List[int])

def test_validate_dict():
    """Testa validação de dicionários"""
    # Dict[str, str]
    assert TypeValidator.validate_type({"a": "b"}, Dict[str, str])
    assert not TypeValidator.validate_type({"a": 1}, Dict[str, str])
    assert not TypeValidator.validate_type({1: "b"}, Dict[str, str])
    
    # Dict[str, int]
    assert TypeValidator.validate_type({"a": 1}, Dict[str, int])
    assert not TypeValidator.validate_type({"a": "1"}, Dict[str, int])
    
    # Dict vazio
    assert TypeValidator.validate_type({}, Dict[str, str])
    assert TypeValidator.validate_type({}, Dict[str, int])

def test_validate_optional():
    """Testa validação de tipos opcionais"""
    # Optional[str]
    assert TypeValidator.validate_type("test", Optional[str])
    assert TypeValidator.validate_type(None, Optional[str])
    assert not TypeValidator.validate_type(123, Optional[str])
    
    # Optional[int]
    assert TypeValidator.validate_type(123, Optional[int])
    assert TypeValidator.validate_type(None, Optional[int])
    assert not TypeValidator.validate_type("123", Optional[int])

def test_validate_complex_types():
    """Testa validação de tipos complexos"""
    # List[Dict[str, Any]]
    assert TypeValidator.validate_type(
        [{"a": "b"}, {"c": 1}],
        List[Dict[str, Any]]
    )
    assert not TypeValidator.validate_type(
        [{"a": "b"}, "not a dict"],
        List[Dict[str, Any]]
    )
    
    # Dict[str, List[int]]
    assert TypeValidator.validate_type(
        {"a": [1, 2], "b": [3, 4]},
        Dict[str, List[int]]
    )
    assert not TypeValidator.validate_type(
        {"a": [1, "2"], "b": [3, 4]},
        Dict[str, List[int]]
    )

@TypeValidator.validate
def sample_function(x: int, y: str, z: Optional[List[int]] = None) -> Dict[str, Any]:
    """Função de exemplo para testar decorators"""
    return {"x": x, "y": y, "z": z}

def test_validate_function():
    """Testa validação de função decorada"""
    # Chamada válida
    result = sample_function(1, "test")
    assert result == {"x": 1, "y": "test", "z": None}
    
    result = sample_function(1, "test", [1, 2, 3])
    assert result == {"x": 1, "y": "test", "z": [1, 2, 3]}
    
    # Argumentos inválidos
    with pytest.raises(TypeValidationError):
        sample_function("1", "test")  # x deve ser int
    
    with pytest.raises(TypeValidationError):
        sample_function(1, 2)  # y deve ser str
    
    with pytest.raises(TypeValidationError):
        sample_function(1, "test", ["1", "2"])  # z deve ser List[int]

@TypeValidator.validate
def invalid_return() -> str:
    """Função que retorna tipo errado"""
    return 123

def test_validate_return():
    """Testa validação de retorno"""
    with pytest.raises(TypeValidationError):
        invalid_return() 