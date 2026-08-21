"""Tests for PriceUpdatePopup."""
import tkinter as tk
from unittest.mock import Mock, patch
import pytest

from foodlog.gui.dialogs.price_update_popup import PriceUpdatePopup


@pytest.fixture
def root():
    """Create test Tk root."""
    r = tk.Tk()
    yield r
    r.destroy()


class TestPriceUpdatePopup:
    """Test PriceUpdatePopup dialog."""

    @patch('foodlog.gui.dialogs.price_update_popup.ItemsRepository')
    def test_popup_opens_with_current_price(self, mock_repo, root):
        """Verify popup displays current price."""
        on_saved = Mock()
        popup = PriceUpdatePopup(root, item_id=1, current_price=2.99, on_saved=on_saved)
        assert popup.title() == "Update Item Price"
        assert "$2.99" in popup.price_label.cget("text")
        popup.destroy()

    @patch('foodlog.gui.dialogs.price_update_popup.ItemsRepository')
    def test_entry_prepopulated_with_current_price(self, mock_repo, root):
        """Verify price entry is pre-filled."""
        on_saved = Mock()
        popup = PriceUpdatePopup(root, item_id=1, current_price=2.99, on_saved=on_saved)
        assert popup.price_entry.get() == "2.99"
        popup.destroy()

    @patch('foodlog.gui.dialogs.price_update_popup.ItemsRepository')
    def test_save_valid_price(self, mock_repo, root):
        """Verify save with valid price updates repository and calls callback."""
        mock_items_repo = Mock()
        mock_repo.return_value = mock_items_repo
        on_saved = Mock()

        popup = PriceUpdatePopup(root, item_id=1, current_price=2.99, on_saved=on_saved)
        popup.price_entry.delete(0, tk.END)
        popup.price_entry.insert(0, "3.50")
        popup._on_save()

        mock_items_repo.update_item_price.assert_called_once_with(1, 3.50)
        on_saved.assert_called_once_with(3.50)

    @patch('foodlog.gui.dialogs.price_update_popup.ItemsRepository')
    @patch('foodlog.gui.dialogs.price_update_popup.messagebox')
    def test_save_invalid_price_shows_error(self, mock_msgbox, mock_repo, root):
        """Verify invalid price shows error message."""
        on_saved = Mock()
        popup = PriceUpdatePopup(root, item_id=1, current_price=2.99, on_saved=on_saved)
        popup.price_entry.delete(0, tk.END)
        popup.price_entry.insert(0, "not_a_number")
        popup._on_save()

        mock_msgbox.showerror.assert_called_once()
        on_saved.assert_not_called()

    @patch('foodlog.gui.dialogs.price_update_popup.ItemsRepository')
    def test_save_zero_price(self, mock_repo, root):
        """Verify zero price is accepted."""
        mock_items_repo = Mock()
        mock_repo.return_value = mock_items_repo
        on_saved = Mock()

        popup = PriceUpdatePopup(root, item_id=1, current_price=2.99, on_saved=on_saved)
        popup.price_entry.delete(0, tk.END)
        popup.price_entry.insert(0, "0.00")
        popup._on_save()

        mock_items_repo.update_item_price.assert_called_once_with(1, 0.00)
        on_saved.assert_called_once_with(0.00)

    @patch('foodlog.gui.dialogs.price_update_popup.ItemsRepository')
    def test_popup_destroyed_after_successful_save(self, mock_repo, root):
        """Verify popup is destroyed after successful save."""
        mock_items_repo = Mock()
        mock_repo.return_value = mock_items_repo
        on_saved = Mock()

        popup = PriceUpdatePopup(root, item_id=1, current_price=2.99, on_saved=on_saved)
        popup.price_entry.delete(0, tk.END)
        popup.price_entry.insert(0, "3.50")
        popup._on_save()

        assert not popup.winfo_exists()

    @patch('foodlog.gui.dialogs.price_update_popup.messagebox')
    def test_save_negative_price_shows_error(self, mock_msgbox, root):
        """Verify negative price is rejected by validate_price."""
        on_saved = Mock()
        popup = PriceUpdatePopup(root, item_id=1, current_price=2.99, on_saved=on_saved)
        popup.price_entry.delete(0, tk.END)
        popup.price_entry.insert(0, "-1.50")
        popup._on_save()

        mock_msgbox.showerror.assert_called_once()
        on_saved.assert_not_called()
