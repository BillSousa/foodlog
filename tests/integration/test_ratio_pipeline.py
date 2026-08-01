import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch

from foodlog.calculations.ratios import ratio1, ratio2
from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.models.dim_items import Item
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.product_names_repository import ProductNamesRepository


def test_ratio_pipeline_item_creation_to_calculation() -> None:
    """Integration: create item → retrieve → convert mcg→mg → compute ratios.

    Verifies the full pipeline from storing sodium_mcg in the database
    to converting it back to mg for ratio calculations, ensuring the
    real-world foodlog chain of operations works correctly.
    """
    # Create temp database
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / 'test.db'

    with patch('foodlog.database.connection.get_database_path', return_value=db_path):
        # Initialize database
        conn = get_connection()
        create_schema(conn)
        seed_reference_data(conn)
        conn.close()

        # Set up: create a product name for the item
        names_repo = ProductNamesRepository()
        unique_name = f"Test Pasta {uuid.uuid4().hex[:8]}"
        name_id = names_repo.create_product_name(unique_name)

        # Create a realistic item (like a pasta box)
        items_repo = ItemsRepository()
        item = Item(
            name_id=name_id,
            category_id=None,
            price=2.50,
            servings_per_block=8.0,
            units="g",
            container_size=500,
            serving_size=62.5,
            blocks_must_be_integer=0,
            active=1,
            calories=200,
            total_fat_g=2,
            protein_g=8,
            sodium_mcg=500_000,
            total_carbs_g=40,
            dietary_fiber_g=2,
            total_sugars_g=1,
            glycemic_index=None,
            cholesterol_mcg=0,
            vitamin_d_mcg=0,
            vitamin_a_mcg=0,
            vitamin_c_mcg=0,
            vitamin_e_mcg=0,
            vitamin_k_mcg=0,
            calcium_mcg=0,
            iron_mcg=0,
            potassium_mcg=0,
            thiamin_mcg=0,
            riboflavin_mcg=0,
            niacin_mcg=0,
            vitamin_b6_mcg=0,
            folate_mcg=0,
            vitamin_b12_mcg=0,
            biotin_mcg=0,
            pantothenic_acid_mcg=0,
            phosphorus_mcg=0,
            iodine_mcg=0,
            magnesium_mcg=0,
            zinc_mcg=0,
            selenium_mcg=0,
            copper_mcg=0,
            manganese_mcg=0,
            chromium_mcg=0,
            molybdenum_mcg=0,
            chloride_mcg=0,
            ethanol_g=0,
            ratio1=0.0,
            ratio2=0.0,
        )

        # Create and retrieve the item
        item_id = items_repo.create_item(item)
        retrieved = items_repo.get_item(item_id)

        assert retrieved is not None
        assert retrieved.sodium_mcg == 500_000

        # Convert mcg to mg for ratio functions (the key step)
        sodium_mg = retrieved.sodium_mcg / 1000
        assert sodium_mg == 500.0

        # Calculate ratios using converted value
        r1 = ratio1(retrieved.calories, retrieved.price, sodium_mg)
        r2 = ratio2(
            retrieved.calories, retrieved.price, sodium_mg, retrieved.total_fat_g
        )

        # Hand-computed expected values
        # Ratio1 = 200 / (4*2.50 + 500/100 + 0.00001)
        #        = 200 / (10 + 5 + 0.00001) = 200 / 15.00001
        expected_r1 = 200 / (4 * 2.50 + 500 / 100 + 0.00001)

        # Ratio2 = 200 / (1.333*2.50 + 500/300 + 2/6.6 + 0.00001)
        #        = 200 / (3.3325 + 1.6667 + 0.3030 + 0.00001)
        expected_r2 = 200 / (
            1.333 * 2.50 + 500 / 300 + 2 / 6.6 + 0.00001
        )

        assert abs(r1 - expected_r1) < 1e-6
        assert abs(r2 - expected_r2) < 1e-6
