"""Unit tests for the Menu entity."""
from domain.entities.menu import Menu, MenuCategory, MenuItem
from uuid import uuid4

def test_menu_creation():
    """Test creating a Menu domain entity."""
    business_id = uuid4()
    item = MenuItem(name="Burger", price=5.99)
    category = MenuCategory(name="Mains", items=[item])
    menu = Menu(business_id=business_id, name="Test Menu", categories=[category])
    
    assert menu.business_id == business_id
    assert menu.name == "Test Menu"
    assert len(menu.categories) == 1
    assert menu.categories[0].name == "Mains"
    assert len(menu.categories[0].items) == 1
    assert menu.categories[0].items[0].name == "Burger"
