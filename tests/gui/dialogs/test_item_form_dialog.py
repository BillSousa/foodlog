"""Tests for ItemFormDialog."""
import tkinter as tk
from unittest.mock import Mock, MagicMock, patch, call
import pytest

from foodlog.gui.dialogs.item_form_dialog import ItemFormDialog
from foodlog.models.dim_items import Item


@pytest.fixture
def root():
    """Create test Tk root."""
    r = tk.Tk()
    yield r
    r.destroy()


@pytest.fixture
def item():
    """Fixture: existing item."""
    return Item(
        item_id=1,
        name_id=10,
        category_id=5,
        price=2.99,
        servings_per_block=6.0,
        units='oz',
        container_size=10.0,
        serving_size=1.67,
        blocks_must_be_integer=0,
        active=1,
        glycemic_index=50,
        calories=100.0,
        sodium_mcg=2300000.0,
        total_fat_g=5.0,
    )


class TestItemFormDialogPopulate:
    """Test _populate_form()."""

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ProductNamesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ItemsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.CategoriesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.populate_item_form_data')
    def test_populate_form_called_on_init_with_item(
        self, mock_populate, mock_cat_repo, mock_items_repo, mock_names_repo, mock_tracked_repo, root, item
    ):
        """Verify _populate_form is called during __init__ when item_id provided."""
        mock_items_repo.return_value.get_item.return_value = item
        mock_cat_repo.return_value.list_categories.return_value = []
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        form_data = {
            'name_text': 'Test Item',
            'price': '2.99',
            'units': 'oz',
            'container_size': '10.0',
            'serving_size': '1.67',
            'active': True,
            'blocks_must_be_integer': False,
            'glycemic_index': '50',
            'nutrition_values': {'calories': 100.0},
        }
        mock_populate.return_value = form_data

        dialog = ItemFormDialog(root, item_id=1)

        mock_populate.assert_called_once()
        assert mock_populate.call_args[0][0] == item

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ProductNamesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ItemsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.CategoriesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.populate_item_form_data')
    def test_populate_form_sets_widget_values(
        self, mock_populate, mock_cat_repo, mock_items_repo, mock_names_repo, mock_tracked_repo, root, item
    ):
        """Verify _populate_form sets all widget values."""
        mock_items_repo.return_value.get_item.return_value = item
        mock_cat_repo.return_value.list_categories.return_value = []
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        form_data = {
            'name_text': 'Rice',
            'price': '5.99',
            'units': 'kg',
            'container_size': '2.0',
            'serving_size': '0.1',
            'active': True,
            'blocks_must_be_integer': True,
            'glycemic_index': '70',
            'nutrition_values': {'calories': 150.0},
        }
        mock_populate.return_value = form_data

        dialog = ItemFormDialog(root, item_id=1)

        assert dialog.name_entry.get() == 'Rice'
        assert dialog.price_entry.get() == '5.99'
        assert dialog.units_entry.get() == 'kg'
        assert dialog.container_entry.get() == '2.0'
        assert dialog.serving_entry.get() == '0.1'
        assert dialog.active_var.get() is True
        assert dialog.blocks_must_be_integer_var.get() is True
        assert dialog.glycemic_index_entry.get() == '70'

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ProductNamesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ItemsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.CategoriesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.populate_item_form_data')
    def test_populate_form_glycemic_index_none(
        self, mock_populate, mock_cat_repo, mock_items_repo, mock_names_repo, mock_tracked_repo, root, item
    ):
        """Verify glycemic index blank when None."""
        item.glycemic_index = None
        mock_items_repo.return_value.get_item.return_value = item
        mock_cat_repo.return_value.list_categories.return_value = []
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        form_data = {
            'name_text': 'Pasta',
            'price': '1.50',
            'units': 'g',
            'container_size': '500',
            'serving_size': '50',
            'active': True,
            'blocks_must_be_integer': False,
            'glycemic_index': None,
            'nutrition_values': {},
        }
        mock_populate.return_value = form_data

        dialog = ItemFormDialog(root, item_id=1)

        assert dialog.glycemic_index_entry.get() == ''


class TestItemFormDialogSave:
    """Test _save() flow."""

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ItemsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ProductNamesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.CategoriesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_new_item(
        self, mock_msgbox, mock_cat_repo, mock_names_repo,
        mock_items_repo, mock_tracked_repo, root
    ):
        """Test saving a new item."""
        mock_names_repo.return_value.create_product_name.return_value = 20
        mock_cat_repo.return_value.list_categories.return_value = []
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        mock_items_repo.return_value.create_item.return_value = 2

        dialog = ItemFormDialog(root)
        dialog.name_entry.insert(0, 'Chicken')
        dialog.units_entry.insert(0, 'lb')
        dialog.price_entry.insert(0, '7.99')
        dialog.container_entry.insert(0, '5')
        dialog.serving_entry.insert(0, '1')
        dialog.active_var.set(True)
        dialog.blocks_must_be_integer_var.set(False)

        dialog._save()

        mock_names_repo.return_value.create_product_name.assert_called_once_with(
            'Chicken'
        )
        mock_items_repo.return_value.create_item.assert_called_once()
        mock_msgbox.showinfo.assert_called_once()

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ItemsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ProductNamesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.CategoriesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.should_create_new_version')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_scd2_nutrition_changed(
        self, mock_msgbox, mock_should_scd2, mock_cat_repo,
        mock_names_repo, mock_items_repo, mock_tracked_repo, root, item
    ):
        """Test saving with nutrition change triggers SCD2."""
        mock_items_repo.return_value.get_item.return_value = item
        mock_cat_repo.return_value.list_categories.return_value = []
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        mock_should_scd2.return_value = True

        dialog = ItemFormDialog(root, item_id=1)
        # Clear pre-populated values and set new ones
        dialog.name_entry.delete(0, tk.END)
        dialog.name_entry.insert(0, 'Chicken')
        dialog.units_entry.delete(0, tk.END)
        dialog.units_entry.insert(0, 'lb')
        dialog.price_entry.delete(0, tk.END)
        dialog.price_entry.insert(0, '7.99')
        dialog.container_entry.delete(0, tk.END)
        dialog.container_entry.insert(0, '5')
        dialog.serving_entry.delete(0, tk.END)
        dialog.serving_entry.insert(0, '1')
        dialog.active_var.set(True)
        dialog.blocks_must_be_integer_var.set(False)
        dialog.nutrition_panel.get_values = Mock(return_value={})

        dialog._save()

        mock_should_scd2.assert_called_once()
        mock_items_repo.return_value.create_item_version.assert_called_once()
        mock_items_repo.return_value.update_item_price.assert_not_called()

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ItemsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ProductNamesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.CategoriesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.should_create_new_version')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_scd1_price_only(
        self, mock_msgbox, mock_should_scd2, mock_cat_repo,
        mock_names_repo, mock_items_repo, mock_tracked_repo, root, item
    ):
        """Test saving price-only change (SCD1)."""
        mock_items_repo.return_value.get_item.return_value = item
        mock_cat_repo.return_value.list_categories.return_value = []
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        mock_should_scd2.return_value = False

        dialog = ItemFormDialog(root, item_id=1)
        dialog.name_entry.delete(0, tk.END)
        dialog.name_entry.insert(0, 'Chicken')
        dialog.units_entry.delete(0, tk.END)
        dialog.units_entry.insert(0, 'lb')
        dialog.price_entry.delete(0, tk.END)
        dialog.price_entry.insert(0, '8.99')
        dialog.container_entry.delete(0, tk.END)
        dialog.container_entry.insert(0, '5')
        dialog.serving_entry.delete(0, tk.END)
        dialog.serving_entry.insert(0, '1')
        dialog.active_var.set(True)
        dialog.blocks_must_be_integer_var.set(False)
        dialog.nutrition_panel.get_values = Mock(return_value={})

        dialog._save()

        mock_should_scd2.assert_called_once()
        mock_items_repo.return_value.update_item_price.assert_called_once_with(
            1, 8.99
        )
        mock_items_repo.return_value.update_item_metadata.assert_called_once()
        mock_items_repo.return_value.create_item_version.assert_not_called()

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ItemsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ProductNamesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.CategoriesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.should_create_new_version')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_metadata_only(
        self, mock_msgbox, mock_should_scd2, mock_cat_repo,
        mock_names_repo, mock_items_repo, mock_tracked_repo, root, item
    ):
        """Test metadata-only changes (category, glycemic_index, etc)."""
        mock_items_repo.return_value.get_item.return_value = item
        mock_cat_repo.return_value.list_categories.return_value = []
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        mock_should_scd2.return_value = False

        dialog = ItemFormDialog(root, item_id=1)
        dialog.name_entry.delete(0, tk.END)
        dialog.name_entry.insert(0, 'Chicken')
        dialog.units_entry.delete(0, tk.END)
        dialog.units_entry.insert(0, 'lb')
        dialog.price_entry.delete(0, tk.END)
        dialog.price_entry.insert(0, '7.99')
        dialog.container_entry.delete(0, tk.END)
        dialog.container_entry.insert(0, '5')
        dialog.serving_entry.delete(0, tk.END)
        dialog.serving_entry.insert(0, '1')
        dialog.active_var.set(False)
        dialog.blocks_must_be_integer_var.set(True)
        dialog.glycemic_index_entry.delete(0, tk.END)
        dialog.glycemic_index_entry.insert(0, '60')
        dialog.nutrition_panel.get_values = Mock(return_value={})

        dialog._save()

        mock_items_repo.return_value.update_item_metadata.assert_called_once_with(
            1, None, 60, 1, 0
        )


class TestItemFormDialogValidation:
    """Test validation on save."""

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_empty_name_rejected(self, mock_msgbox, mock_tracked_repo, root):
        """Empty name shows error and doesn't save."""
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        dialog = ItemFormDialog(root)
        dialog.name_entry.insert(0, '   ')
        dialog.units_entry.insert(0, 'oz')
        dialog.price_entry.insert(0, '1.0')
        dialog.container_entry.insert(0, '10')
        dialog.serving_entry.insert(0, '1')

        dialog._save()

        mock_msgbox.showerror.assert_called_once()
        assert 'required' in mock_msgbox.showerror.call_args[0][1].lower()

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_empty_units_rejected(self, mock_msgbox, mock_tracked_repo, root):
        """Empty units shows error and doesn't save."""
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        dialog = ItemFormDialog(root)
        dialog.name_entry.insert(0, 'Rice')
        dialog.units_entry.insert(0, '   ')
        dialog.price_entry.insert(0, '1.0')
        dialog.container_entry.insert(0, '10')
        dialog.serving_entry.insert(0, '1')

        dialog._save()

        mock_msgbox.showerror.assert_called_once()
        assert 'required' in mock_msgbox.showerror.call_args[0][1].lower()

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_negative_container_rejected(self, mock_msgbox, mock_tracked_repo, root):
        """Negative container size rejected."""
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        dialog = ItemFormDialog(root)
        dialog.name_entry.insert(0, 'Rice')
        dialog.units_entry.insert(0, 'g')
        dialog.price_entry.insert(0, '1.0')
        dialog.container_entry.insert(0, '-10')
        dialog.serving_entry.insert(0, '1')

        dialog._save()

        mock_msgbox.showerror.assert_called_once()
        assert 'positive' in mock_msgbox.showerror.call_args[0][1].lower()

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_zero_serving_rejected(self, mock_msgbox, mock_tracked_repo, root):
        """Zero serving size rejected."""
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        dialog = ItemFormDialog(root)
        dialog.name_entry.insert(0, 'Rice')
        dialog.units_entry.insert(0, 'g')
        dialog.price_entry.insert(0, '1.0')
        dialog.container_entry.insert(0, '10')
        dialog.serving_entry.insert(0, '0')

        dialog._save()

        mock_msgbox.showerror.assert_called_once()
        assert 'positive' in mock_msgbox.showerror.call_args[0][1].lower()

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ItemsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ProductNamesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.CategoriesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_non_integer_glycemic_index_rejected(
        self, mock_msgbox, mock_cat_repo, mock_names_repo, mock_items_repo,
        mock_tracked_repo, root
    ):
        """Non-integer glycemic index rejected."""
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        dialog = ItemFormDialog(root)
        dialog.name_entry.insert(0, 'Rice')
        dialog.units_entry.insert(0, 'g')
        dialog.price_entry.insert(0, '1.0')
        dialog.container_entry.insert(0, '10')
        dialog.serving_entry.insert(0, '1')
        dialog.glycemic_index_entry.insert(0, '50.5')

        dialog._save()

        mock_msgbox.showerror.assert_called_once()
        assert 'whole number' in mock_msgbox.showerror.call_args[0][1].lower()

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_invalid_price_rejected(self, mock_msgbox, mock_tracked_repo, root):
        """Non-numeric price rejected."""
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        dialog = ItemFormDialog(root)
        dialog.name_entry.insert(0, 'Rice')
        dialog.units_entry.insert(0, 'g')
        dialog.price_entry.insert(0, 'abc')
        dialog.container_entry.insert(0, '10')
        dialog.serving_entry.insert(0, '1')

        dialog._save()

        mock_msgbox.showerror.assert_called_once()


class TestItemFormDialogCategoryResolution:
    """Test category name → ID resolution."""

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ItemsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ProductNamesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.CategoriesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_category_resolved_to_id(
        self, mock_msgbox, mock_cat_repo, mock_names_repo,
        mock_items_repo, mock_tracked_repo, root
    ):
        """Category name is resolved to ID."""
        from foodlog.models.dim_categories import Category

        cat1 = Category(category_id=5, category_name='Pasta')
        cat2 = Category(category_id=6, category_name='Meat')
        mock_cat_repo.return_value.list_categories.return_value = [cat1, cat2]
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        mock_names_repo.return_value.create_product_name.return_value = 1

        dialog = ItemFormDialog(root)
        dialog.name_entry.insert(0, 'Chicken')
        dialog.units_entry.insert(0, 'lb')
        dialog.price_entry.insert(0, '7.99')
        dialog.container_entry.insert(0, '5')
        dialog.serving_entry.insert(0, '1')
        dialog.category_var.set('Meat')

        dialog._save()

        # Verify create_item was called with category_id=6
        call_args = mock_items_repo.return_value.create_item.call_args
        item_arg = call_args[0][0]
        assert item_arg.category_id == 6

    @patch('foodlog.gui.components.nutrition_panel.TrackedNutrientsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ItemsRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.ProductNamesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.CategoriesRepository')
    @patch('foodlog.gui.dialogs.item_form_dialog.messagebox')
    def test_save_no_category_none_id(
        self, mock_msgbox, mock_cat_repo, mock_names_repo,
        mock_items_repo, mock_tracked_repo, root
    ):
        """No category selected results in category_id=None."""
        mock_cat_repo.return_value.list_categories.return_value = []
        mock_tracked_repo.return_value.get_tracked_nutrients.return_value = []
        mock_tracked_repo.return_value.list_all_nutrients.return_value = []
        mock_names_repo.return_value.create_product_name.return_value = 1

        dialog = ItemFormDialog(root)
        dialog.name_entry.insert(0, 'Chicken')
        dialog.units_entry.insert(0, 'lb')
        dialog.price_entry.insert(0, '7.99')
        dialog.container_entry.insert(0, '5')
        dialog.serving_entry.insert(0, '1')

        dialog._save()

        call_args = mock_items_repo.return_value.create_item.call_args
        item_arg = call_args[0][0]
        assert item_arg.category_id is None
